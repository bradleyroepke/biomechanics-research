#!/usr/bin/env python3
"""
Verify and audit article enrichment quality.

Modes:
  python3 verify_extractions.py                  # Dashboard: confidence stats, domain coverage
  python3 verify_extractions.py --review N       # Show N random enrichments for spot-check
  python3 verify_extractions.py --flagged        # Show all articles needing manual review
  python3 verify_extractions.py --ids 1,5,23     # Show specific articles for review
  python3 verify_extractions.py --concepts       # Concept frequency analysis
"""

import argparse
import json
import os
import random
import sys
import textwrap
from pathlib import Path

from supabase import create_client

BASE_DIR = Path(__file__).parent

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
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmZndtemNpb2VrZXlqeWtzaHhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTc5MDUwNCwiZXhwIjoyMDg1MzY2NTA0fQ.NeKQHoG96Yw4vnUfOQlZbBExtiiLZ0HNYVHkxBN_beU"


def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def show_dashboard(sb):
    """Overview statistics of enrichment quality."""
    # Total articles vs enriched
    total = sb.table("research_articles").select("id", count="exact").execute()
    enriched = sb.table("article_enrichments").select("id", count="exact").execute()

    print(f"{'='*60}")
    print(f"ENRICHMENT DASHBOARD")
    print(f"{'='*60}")
    print(f"Total articles:     {total.count}")
    print(f"Enriched:           {enriched.count}")
    print(f"Remaining:          {total.count - enriched.count}")
    print(f"Coverage:           {enriched.count/total.count*100:.1f}%" if total.count else "N/A")

    if enriched.count == 0:
        print("\nNo enrichments yet. Run enrich_articles.py first.")
        return

    # Confidence distribution
    all_enrichments = sb.table("article_enrichments").select("extraction_confidence, needs_manual_review, methodology, domain_tags, joint_region, tissue_system").execute()

    conf = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    review_count = 0
    methods = {}
    domains = {}
    joints = {}
    tissues = {}

    for e in all_enrichments.data:
        conf[e.get("extraction_confidence", "MEDIUM")] = conf.get(e.get("extraction_confidence", "MEDIUM"), 0) + 1
        if e.get("needs_manual_review"):
            review_count += 1
        m = e.get("methodology", "unknown")
        methods[m] = methods.get(m, 0) + 1
        for d in (e.get("domain_tags") or []):
            domains[d] = domains.get(d, 0) + 1
        for j in (e.get("joint_region") or []):
            joints[j] = joints.get(j, 0) + 1
        for t in (e.get("tissue_system") or []):
            tissues[t] = tissues.get(t, 0) + 1

    print(f"\n{'─'*60}")
    print(f"CONFIDENCE DISTRIBUTION")
    print(f"  HIGH:   {conf['HIGH']:>4}  ({conf['HIGH']/enriched.count*100:.1f}%)")
    print(f"  MEDIUM: {conf['MEDIUM']:>4}  ({conf['MEDIUM']/enriched.count*100:.1f}%)")
    print(f"  LOW:    {conf['LOW']:>4}  ({conf['LOW']/enriched.count*100:.1f}%)")
    print(f"  Needs review: {review_count}")

    print(f"\n{'─'*60}")
    print(f"METHODOLOGY BREAKDOWN")
    for m, c in sorted(methods.items(), key=lambda x: -x[1]):
        print(f"  {m:<30} {c:>4}")

    print(f"\n{'─'*60}")
    print(f"DOMAIN COVERAGE")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        bar = "█" * min(c, 50)
        print(f"  {d:<25} {c:>4}  {bar}")

    print(f"\n{'─'*60}")
    print(f"JOINT/REGION COVERAGE")
    for j, c in sorted(joints.items(), key=lambda x: -x[1]):
        bar = "█" * min(c, 50)
        print(f"  {j:<20} {c:>4}  {bar}")

    print(f"\n{'─'*60}")
    print(f"TISSUE COVERAGE")
    for t, c in sorted(tissues.items(), key=lambda x: -x[1]):
        bar = "█" * min(c, 50)
        print(f"  {t:<20} {c:>4}  {bar}")


def show_article(sb, article_id: int):
    """Display full enrichment for one article."""
    # Get article metadata
    art = sb.table("research_articles").select("*").eq("id", article_id).execute()
    if not art.data:
        print(f"  Article ID {article_id} not found.")
        return
    art = art.data[0]

    # Get enrichment
    enr = sb.table("article_enrichments").select("*").eq("article_id", article_id).execute()
    if not enr.data:
        print(f"  No enrichment for article ID {article_id}: {art['filename']}")
        return
    enr = enr.data[0]

    # Get concepts
    concepts = sb.table("article_concepts").select("concept, relevance").eq("article_id", article_id).execute()

    print(f"\n{'='*70}")
    print(f"ARTICLE: {art['filename']}")
    print(f"{'='*70}")
    print(f"ID: {article_id} | Year: {art.get('year')} | Author: {art.get('first_author')} | Journal: {art.get('journal')}")
    print(f"Title: {art.get('title')}")
    print(f"Confidence: {enr.get('extraction_confidence')} | Review needed: {enr.get('needs_manual_review')}")
    if enr.get("review_notes"):
        print(f"Review notes: {enr['review_notes']}")

    print(f"\n{'─'*70}")
    print(f"ABSTRACT:")
    abstract = enr.get("abstract") or "(none)"
    print(textwrap.fill(abstract, width=70, initial_indent="  ", subsequent_indent="  "))

    print(f"\n{'─'*70}")
    print(f"KEY TAKEAWAYS:")
    takeaways = enr.get("key_takeaways") or "(none)"
    print(textwrap.fill(takeaways, width=70, initial_indent="  ", subsequent_indent="  "))

    print(f"\n{'─'*70}")
    print(f"KEY FINDINGS:")
    findings = enr.get("key_findings")
    if isinstance(findings, str):
        findings = json.loads(findings)
    if findings:
        for j, f in enumerate(findings, 1):
            print(f"\n  [{j}] {f.get('finding', '?')}")
            if f.get("statistic"):
                print(f"      Stat: {f['statistic']}")
            if f.get("sample"):
                print(f"      Sample: {f['sample']}")
            if f.get("source_location"):
                print(f"      Source: {f['source_location']}")
            if f.get("verbatim_quote"):
                q = f["verbatim_quote"][:200]
                print(f"      Quote: \"{q}{'...' if len(f['verbatim_quote']) > 200 else ''}\"")
            elif f.get("statistic"):
                print(f"      ⚠ NO VERBATIM QUOTE for this statistic")
    else:
        print("  (none)")

    print(f"\n{'─'*70}")
    print(f"MECHANISTIC REASONING:")
    mech = enr.get("mechanistic_reasoning") or "(none)"
    print(textwrap.fill(mech, width=70, initial_indent="  ", subsequent_indent="  "))

    print(f"\n{'─'*70}")
    print(f"LIMITATIONS:")
    lim = enr.get("limitations") or "(none)"
    print(textwrap.fill(lim, width=70, initial_indent="  ", subsequent_indent="  "))

    print(f"\n{'─'*70}")
    print(f"CLASSIFICATION:")
    print(f"  Methodology:  {enr.get('methodology')}")
    print(f"  Species:      {enr.get('species')}")
    print(f"  Tissue:       {', '.join(enr.get('tissue_system') or [])}")
    print(f"  Joint/Region: {', '.join(enr.get('joint_region') or [])}")
    print(f"  Domains:      {', '.join(enr.get('domain_tags') or [])}")

    print(f"\n{'─'*70}")
    print(f"CONCEPTS:")
    if concepts.data:
        for c in sorted(concepts.data, key=lambda x: {"primary": 0, "secondary": 1, "mentioned": 2}.get(x["relevance"], 3)):
            print(f"  [{c['relevance']:<10}] {c['concept']}")
    else:
        print("  (none)")


def show_concepts(sb):
    """Concept frequency analysis."""
    concepts = sb.table("article_concepts").select("concept, relevance").execute()
    if not concepts.data:
        print("No concepts found.")
        return

    freq = {}
    primary_freq = {}
    for c in concepts.data:
        name = c["concept"]
        freq[name] = freq.get(name, 0) + 1
        if c["relevance"] == "primary":
            primary_freq[name] = primary_freq.get(name, 0) + 1

    print(f"{'='*60}")
    print(f"CONCEPT FREQUENCY (top 40)")
    print(f"{'='*60}")
    print(f"{'Concept':<35} {'Total':>5} {'Primary':>7}")
    print(f"{'─'*35} {'─'*5} {'─'*7}")
    for name, count in sorted(freq.items(), key=lambda x: -x[1])[:40]:
        p = primary_freq.get(name, 0)
        bar = "█" * min(count, 30)
        print(f"  {name:<33} {count:>5} {p:>7}  {bar}")

    print(f"\n{'─'*60}")
    print(f"Total unique concepts: {len(freq)}")
    print(f"Total concept-article links: {len(concepts.data)}")


def main():
    parser = argparse.ArgumentParser(description="Verify article enrichments")
    parser.add_argument("--review", type=int, metavar="N", help="Show N random enrichments for spot-check")
    parser.add_argument("--flagged", action="store_true", help="Show articles needing manual review")
    parser.add_argument("--ids", type=str, help="Comma-separated article IDs to display")
    parser.add_argument("--concepts", action="store_true", help="Concept frequency analysis")
    parser.add_argument("--low", action="store_true", help="Show LOW confidence articles")
    args = parser.parse_args()

    sb = get_sb()

    if args.ids:
        ids = [int(x.strip()) for x in args.ids.split(",")]
        for aid in ids:
            show_article(sb, aid)
        return

    if args.flagged:
        flagged = sb.table("article_enrichments").select("article_id").eq("needs_manual_review", True).execute()
        if not flagged.data:
            print("No articles flagged for manual review.")
            return
        print(f"Found {len(flagged.data)} articles needing review:\n")
        for f in flagged.data:
            show_article(sb, f["article_id"])
        return

    if args.low:
        low = sb.table("article_enrichments").select("article_id").eq("extraction_confidence", "LOW").execute()
        if not low.data:
            print("No LOW confidence articles.")
            return
        print(f"Found {len(low.data)} LOW confidence articles:\n")
        for l in low.data:
            show_article(sb, l["article_id"])
        return

    if args.review:
        all_enriched = sb.table("article_enrichments").select("article_id").execute()
        if not all_enriched.data:
            print("No enrichments to review.")
            return
        ids = [e["article_id"] for e in all_enriched.data]
        sample = random.sample(ids, min(args.review, len(ids)))
        print(f"Random sample of {len(sample)} articles:\n")
        for aid in sample:
            show_article(sb, aid)
        return

    if args.concepts:
        show_concepts(sb)
        return

    # Default: dashboard
    show_dashboard(sb)


if __name__ == "__main__":
    main()
