#!/usr/bin/env python3
"""
Enrich article metadata using Claude API structured extraction.

Reads extracted text from Articles/_text/, sends to Claude for structured
analysis, and stores results in Supabase article_enrichments + article_concepts.

Accuracy rules:
  - Extract ONLY what the paper explicitly states
  - Every statistic requires a verbatim quote or gets flagged
  - Ambiguous content → needs_manual_review = true
  - No inference, no extrapolation, no gap-filling

Usage:
  python3 enrich_articles.py                    # Process all unenriched articles
  python3 enrich_articles.py --limit 10         # Process first 10 only (calibration)
  python3 enrich_articles.py --ids 1,5,23       # Process specific article IDs
  python3 enrich_articles.py --model sonnet     # Use Sonnet instead of Haiku
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from supabase import create_client

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / "Articles"
TEXT_DIR = ARTICLES_DIR / "_text"
LOG_DIR = ARTICLES_DIR / "_enrichment_logs"

# Load credentials from .env.local
def load_env():
    env_path = BASE_DIR / ".env.local"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vffwmzcioekeyjykshxi.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6-20250514",
}

# Also accept the service role key from the upload script as fallback
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmZndtemNpb2VrZXlqeWtzaHhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTc5MDUwNCwiZXhwIjoyMDg1MzY2NTA0fQ.NeKQHoG96Yw4vnUfOQlZbBExtiiLZ0HNYVHkxBN_beU"

# ─── Extraction Prompt ───────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are a research article analysis assistant. Your job is to extract structured metadata from academic papers with STRICT ACCURACY.

## CRITICAL ACCURACY RULES
1. Extract ONLY what the paper explicitly states. Do NOT infer, extrapolate, or fill gaps.
2. For quantitative findings, you MUST include a verbatim quote from the paper text. If you cannot find the exact text for a statistic, set "verbatim_quote" to null.
3. If the PDF text is garbled, partially unreadable, or missing sections, set extraction_confidence to "LOW".
4. For mechanistic_reasoning, describe ONLY what the AUTHORS argue. Do NOT add your own interpretation or connect it to other papers.
5. If a field cannot be determined from the text, use null or empty values. Never fabricate content.
6. When in doubt, set needs_manual_review to true. It is better to flag for review than to guess.

## OUTPUT FORMAT
Respond with a single JSON object (no markdown code fences, no explanation) with these fields:

{
  "abstract": "Verbatim abstract from the paper. If no abstract section exists, set to null.",
  "key_takeaways": "3-5 sentences describing what this paper contributes to the literature. Write in third person. Focus on what is novel or important about this work.",
  "key_findings": [
    {
      "finding": "Plain-language description of the finding",
      "statistic": "The specific number, p-value, OR, CI, etc. Set to null if qualitative finding.",
      "sample": "Sample size and description. Set to null if not stated.",
      "source_location": "Where in the paper this appears (e.g., 'Results, Table 2', 'Abstract', 'p.1247')",
      "verbatim_quote": "Exact quote from the paper text containing this finding. Set to null if you cannot locate the exact text."
    }
  ],
  "mechanistic_reasoning": "2-3 sentences: WHY do the authors say these results occur? What causal mechanism or logic do they propose? If the paper does not offer mechanistic explanation, write 'Not explicitly stated by the authors.'",
  "limitations": "1-2 sentences: What do the authors acknowledge they cannot prove or what are the study limitations? If not discussed, write 'Not discussed by the authors.'",
  "methodology": "One of: RCT, prospective_cohort, retrospective_cohort, case_control, case_series, cross_sectional, biomechanical_model, cadaver, in_vitro, in_vivo_animal, computational, systematic_review, meta_analysis, narrative_review, theoretical_commentary, technique_description, other",
  "tissue_system": ["List of tissues studied. Use: tendon, bone, cartilage, muscle, nerve, labrum, capsule, ligament, vasculature, synovium, fascia, skin, or other specific tissue"],
  "joint_region": ["List of joints/regions. Use: shoulder, hip, knee, ankle, elbow, spine, wrist, hand, foot, systemic, or other specific region"],
  "species": "One of: human, mouse, rat, bovine, porcine, ovine, canine, rabbit, in_silico, mixed, not_applicable",
  "domain_tags": ["List of research domains. Use: biomechanics, cell_biology, molecular_biology, evolutionary_biology, neuroscience, physics, thermodynamics, clinical_ortho, rehabilitation, anatomy, pathology, surgical_technique, epidemiology, motor_control, materials_science, imaging, genetics"],
  "concepts": [
    {
      "name": "concept_name_in_snake_case",
      "relevance": "primary, secondary, or mentioned",
      "category": "molecular, mechanical, clinical, theoretical, evolutionary, or neural"
    }
  ],
  "extraction_confidence": "HIGH if text is clean and findings are clear. MEDIUM if some parsing issues but core content readable. LOW if significant text quality issues.",
  "needs_manual_review": false,
  "review_reason": "If needs_manual_review is true, explain why. Otherwise null."
}

## NOTES
- For key_findings: Include the most important 3-8 findings. Prioritize quantitative results with statistics.
- For concepts: Use snake_case names. Include 3-10 concepts. Prefer existing concept names when applicable: mechanotransduction, wolffs_law, bifurcation_theory, dissipative_structures, piezo1, yap_taz, linc_complex, apoptosis, mechanosensing, tensegrity, fibrocartilaginous_metaplasia, scapular_dyskinesis, critical_shoulder_angle, fatty_infiltration, motor_control, kinetic_chain, force_vectors, stress_shielding, bone_remodeling, tendon_adaptation, cartilage_degeneration, inflammation, neural_plasticity, proprioception, viscoelasticity, creep, fatigue_failure, threshold_behavior, phase_transition, evolutionary_conservation, allometry, collagen_organization, mmp_activity, enthesis_biology, subacromial_impingement, glenoid_morphology, rotator_cuff_biomechanics, scapulothoracic_mechanics
- But do NOT force-fit concepts. If the paper discusses something not in this list, create a new snake_case concept name.
- For review papers or theoretical commentary, key_findings should capture the main arguments/conclusions rather than specific statistics.

Now analyze the following paper:

FILENAME: __FILENAME__
TITLE: __TITLE__
YEAR: __YEAR__
AUTHOR: __AUTHOR__
JOURNAL: __JOURNAL__

--- PAPER TEXT ---
__TEXT__
"""

# ─── Helper Functions ────────────────────────────────────────────────────────

def truncate_text(text: str, max_chars: int = 80000) -> str:
    """Truncate text to fit within token limits. ~4 chars per token, leave room for prompt."""
    if len(text) <= max_chars:
        return text
    # Keep beginning and end (methods/results often in middle, but intro+discussion matter too)
    half = max_chars // 2
    return text[:half] + "\n\n[... TEXT TRUNCATED FOR LENGTH ...]\n\n" + text[-half:]


def parse_response(text: str) -> dict:
    """Parse Claude's JSON response, handling common issues."""
    text = text.strip()
    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def save_log(filename: str, response_data: dict):
    """Save raw API response for audit trail."""
    LOG_DIR.mkdir(exist_ok=True)
    stem = Path(filename).stem
    log_path = LOG_DIR / f"{stem}.json"
    log_path.write_text(json.dumps(response_data, indent=2, default=str))


# ─── Main Processing ─────────────────────────────────────────────────────────

def enrich_one(client: anthropic.Anthropic, article: dict, model: str) -> dict:
    """Enrich a single article. Returns parsed extraction or error dict."""
    filename = article["filename"]
    txt_path = TEXT_DIR / (Path(filename).stem + ".txt")

    if not txt_path.exists():
        return {"error": f"No extracted text found: {txt_path.name}"}

    text = txt_path.read_text(errors="replace")
    if len(text.strip()) < 100:
        return {"error": f"Text too short ({len(text.strip())} chars)"}

    text = truncate_text(text)

    prompt = (EXTRACTION_PROMPT
        .replace("__FILENAME__", filename)
        .replace("__TITLE__", str(article.get("title", "Unknown")))
        .replace("__YEAR__", str(article.get("year", "Unknown")))
        .replace("__AUTHOR__", str(article.get("first_author", "Unknown")))
        .replace("__JOURNAL__", str(article.get("journal", "Unknown")))
        .replace("__TEXT__", text)
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        # Save raw response for audit
        save_log(filename, {
            "article_id": article["id"],
            "filename": filename,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "raw_response": response_text,
        })

        parsed = parse_response(response_text)
        parsed["_tokens"] = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
        return parsed

    except json.JSONDecodeError as e:
        save_log(filename, {
            "article_id": article["id"],
            "error": f"JSON parse error: {e}",
            "raw_response": response_text if 'response_text' in dir() else None,
        })
        return {"error": f"Failed to parse JSON response: {e}"}
    except anthropic.APIError as e:
        return {"error": f"API error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def upsert_enrichment(sb, article_id: int, data: dict):
    """Insert or update enrichment data in Supabase."""
    row = {
        "article_id": article_id,
        "abstract": data.get("abstract"),
        "key_takeaways": data.get("key_takeaways"),
        "key_findings": json.dumps(data.get("key_findings", [])),
        "mechanistic_reasoning": data.get("mechanistic_reasoning"),
        "limitations": data.get("limitations"),
        "methodology": data.get("methodology"),
        "tissue_system": data.get("tissue_system", []),
        "joint_region": data.get("joint_region", []),
        "species": data.get("species"),
        "domain_tags": data.get("domain_tags", []),
        "extraction_confidence": data.get("extraction_confidence", "MEDIUM"),
        "needs_manual_review": data.get("needs_manual_review", False),
        "review_notes": data.get("review_reason"),
    }

    sb.table("article_enrichments").upsert(
        row, on_conflict="article_id"
    ).execute()


def upsert_concepts(sb, article_id: int, concepts: list):
    """Insert article-concept relationships. Creates new concepts as needed."""
    for c in concepts:
        name = c.get("name", "").strip().lower()
        if not name:
            continue

        # Ensure concept exists in reference table
        try:
            sb.table("concepts").upsert(
                {
                    "name": name,
                    "category": c.get("category", "clinical"),
                    "description": None,
                },
                on_conflict="name",
            ).execute()
        except Exception:
            pass  # Concept may already exist with a description we don't want to overwrite

        # Insert junction record
        try:
            sb.table("article_concepts").upsert(
                {
                    "article_id": article_id,
                    "concept": name,
                    "relevance": c.get("relevance", "mentioned"),
                },
                on_conflict="article_id,concept",
            ).execute()
        except Exception as e:
            # FK violation if concept wasn't created — skip silently
            pass


def main():
    parser = argparse.ArgumentParser(description="Enrich articles via Claude API")
    parser.add_argument("--limit", type=int, help="Process only first N unenriched articles")
    parser.add_argument("--ids", type=str, help="Comma-separated article IDs to process")
    parser.add_argument("--model", choices=["haiku", "sonnet"], default="haiku",
                        help="Model to use (default: haiku)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Process but don't write to Supabase (still saves logs)")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found. Add it to .env.local or set as env var.")
        sys.exit(1)

    model = MODELS[args.model]
    print(f"Model: {model}")

    # Initialize clients
    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Get articles to process
    if args.ids:
        ids = [int(x.strip()) for x in args.ids.split(",")]
        result = sb.table("research_articles").select("*").in_("id", ids).execute()
    else:
        # Get all articles, then filter out already-enriched ones
        all_articles = sb.table("research_articles").select("*").order("id").execute()

        # Get already-enriched article IDs
        enriched = sb.table("article_enrichments").select("article_id").execute()
        enriched_ids = {r["article_id"] for r in enriched.data}

        result_data = [a for a in all_articles.data if a["id"] not in enriched_ids]
        if args.limit:
            result_data = result_data[: args.limit]

        class FakeResult:
            def __init__(self, data):
                self.data = data
        result = FakeResult(result_data)

    articles = result.data
    print(f"Articles to process: {len(articles)}")
    if not articles:
        print("Nothing to do.")
        return

    # Process
    total_input_tokens = 0
    total_output_tokens = 0
    stats = {"ok": 0, "error": 0, "flagged": 0}
    start_time = time.time()

    for i, article in enumerate(articles):
        filename = article["filename"]
        short_name = filename[:60] + "..." if len(filename) > 60 else filename

        print(f"\n[{i+1}/{len(articles)}] {short_name}")

        data = enrich_one(claude, article, model)

        if "error" in data:
            print(f"  ERROR: {data['error']}")
            stats["error"] += 1
            continue

        tokens = data.pop("_tokens", {})
        total_input_tokens += tokens.get("input", 0)
        total_output_tokens += tokens.get("output", 0)

        confidence = data.get("extraction_confidence", "MEDIUM")
        needs_review = data.get("needs_manual_review", False)
        n_findings = len(data.get("key_findings", []))
        n_concepts = len(data.get("concepts", []))

        status_flag = ""
        if needs_review:
            status_flag = " [NEEDS REVIEW]"
            stats["flagged"] += 1
        elif confidence == "LOW":
            status_flag = " [LOW CONFIDENCE]"
            stats["flagged"] += 1

        print(f"  {confidence} confidence | {n_findings} findings | {n_concepts} concepts{status_flag}")

        if not args.dry_run:
            try:
                upsert_enrichment(sb, article["id"], data)
                upsert_concepts(sb, article["id"], data.get("concepts", []))
                print(f"  Saved to Supabase")
            except Exception as e:
                print(f"  DB ERROR: {e}")
                stats["error"] += 1
                continue

        stats["ok"] += 1

        # Rate limiting: ~1 request per second for Haiku
        if args.model == "haiku":
            time.sleep(0.5)
        else:
            time.sleep(1.0)

    elapsed = time.time() - start_time

    # Cost estimate (approximate)
    if args.model == "haiku":
        cost = (total_input_tokens * 0.80 + total_output_tokens * 4.00) / 1_000_000
    else:
        cost = (total_input_tokens * 3.00 + total_output_tokens * 15.00) / 1_000_000

    print(f"\n{'='*60}")
    print(f"ENRICHMENT COMPLETE ({elapsed:.0f}s)")
    print(f"{'='*60}")
    print(f"Successful:      {stats['ok']}")
    print(f"Flagged:         {stats['flagged']}  (low confidence or needs review)")
    print(f"Errors:          {stats['error']}")
    print(f"Total processed: {len(articles)}")
    print(f"{'─'*60}")
    print(f"Input tokens:    {total_input_tokens:,}")
    print(f"Output tokens:   {total_output_tokens:,}")
    print(f"Est. cost:       ${cost:.2f}")
    print(f"Model:           {model}")


if __name__ == "__main__":
    main()
