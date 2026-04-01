#!/usr/bin/env python3
"""
Extract text from all article PDFs using pdftotext.

Stores extracted text as .txt files in Articles/_text/.
Flags PDFs with poor extraction quality (< 500 chars) for manual review.

Usage: python3 extract_text.py [--limit N] [--reextract]
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent / "Articles"
TEXT_DIR = ARTICLES_DIR / "_text"
MIN_CHARS = 500  # Below this, flag as likely scanned/image-based


def extract_one(pdf_path: Path, output_path: Path) -> dict:
    """Extract text from a single PDF. Returns status dict."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return {
                "status": "error",
                "error": result.stderr.strip() or f"pdftotext returned {result.returncode}",
            }

        if not output_path.exists():
            return {"status": "error", "error": "No output file produced"}

        text = output_path.read_text(errors="replace")
        char_count = len(text.strip())

        if char_count < MIN_CHARS:
            return {
                "status": "low_quality",
                "chars": char_count,
            }

        return {"status": "ok", "chars": char_count}

    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout (>60s)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Extract text from article PDFs")
    parser.add_argument("--limit", type=int, help="Process only first N PDFs")
    parser.add_argument("--reextract", action="store_true", help="Re-extract even if .txt exists")
    args = parser.parse_args()

    TEXT_DIR.mkdir(exist_ok=True)

    pdfs = sorted(ARTICLES_DIR.glob("*.pdf"))
    if args.limit:
        pdfs = pdfs[: args.limit]

    print(f"Found {len(pdfs)} PDFs in {ARTICLES_DIR}")
    print(f"Output directory: {TEXT_DIR}")
    print()

    stats = {"ok": 0, "low_quality": 0, "error": 0, "skipped": 0}
    low_quality_files = []
    error_files = []
    start_time = time.time()

    for i, pdf_path in enumerate(pdfs):
        txt_name = pdf_path.stem + ".txt"
        output_path = TEXT_DIR / txt_name

        # Resume: skip if already extracted
        if output_path.exists() and not args.reextract:
            stats["skipped"] += 1
            continue

        result = extract_one(pdf_path, output_path)

        if result["status"] == "ok":
            stats["ok"] += 1
        elif result["status"] == "low_quality":
            stats["low_quality"] += 1
            low_quality_files.append((pdf_path.name, result["chars"]))
        else:
            stats["error"] += 1
            error_files.append((pdf_path.name, result["error"]))

        # Progress every 50 files
        processed = stats["ok"] + stats["low_quality"] + stats["error"]
        if processed % 50 == 0 and processed > 0:
            elapsed = time.time() - start_time
            remaining_count = len(pdfs) - i - 1 - stats["skipped"]
            rate = processed / elapsed if elapsed > 0 else 0
            eta = remaining_count / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(pdfs)}] {processed} extracted, ~{eta:.0f}s remaining", flush=True)

    elapsed = time.time() - start_time

    # Summary
    print(f"\n{'='*60}")
    print(f"TEXT EXTRACTION COMPLETE ({elapsed:.1f}s)")
    print(f"{'='*60}")
    print(f"Extracted OK:    {stats['ok']}")
    print(f"Low quality:     {stats['low_quality']}  (< {MIN_CHARS} chars — likely scanned)")
    print(f"Errors:          {stats['error']}")
    print(f"Skipped:         {stats['skipped']}  (already extracted)")
    print(f"Total PDFs:      {len(pdfs)}")

    if low_quality_files:
        print(f"\n{'─'*60}")
        print(f"LOW QUALITY — may need OCR or manual review:")
        for name, chars in sorted(low_quality_files, key=lambda x: x[1]):
            print(f"  {chars:>5} chars  {name}")

    if error_files:
        print(f"\n{'─'*60}")
        print(f"ERRORS:")
        for name, err in error_files:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
