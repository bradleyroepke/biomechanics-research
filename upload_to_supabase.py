#!/usr/bin/env python3
"""
Upload article PDFs to Supabase storage and populate metadata table.

Creates:
  - Storage bucket: research-articles
  - Table: research_articles (year, author, journal, title, doi, storage_path, file_size_kb)

Parses Year_Author_Journal_Title.pdf filenames for metadata.

Usage: python3 upload_to_supabase.py
"""

import os
import re
import time
from pathlib import Path

from supabase import create_client

# ─── Configuration ───────────────────────────────────────────────────────────

ARTICLES_DIR = Path(__file__).parent / "Articles"
BUCKET_NAME = "research-articles"

# Load credentials
SUPABASE_URL = "https://vffwmzcioekeyjykshxi.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZmZndtemNpb2VrZXlqeWtzaHhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTc5MDUwNCwiZXhwIjoyMDg1MzY2NTA0fQ.NeKQHoG96Yw4vnUfOQlZbBExtiiLZ0HNYVHkxBN_beU"


def parse_filename(filename):
    """Parse Year_Author_Journal_Title.pdf into metadata fields."""
    stem = Path(filename).stem
    # Expected: YYYY_Author_Journal_Title_Words
    match = re.match(r'^(\d{4})_([^_]+)_([^_]+(?:_[^_]+)?)_(.+)$', stem)
    if not match:
        # Fallback: just extract year if possible
        year_match = re.match(r'^(\d{4})_(.+)$', stem)
        if year_match:
            return {
                'year': int(year_match.group(1)),
                'first_author': year_match.group(2).split('_')[0],
                'journal': '',
                'title': year_match.group(2).replace('_', ' '),
            }
        return {
            'year': None,
            'first_author': '',
            'journal': '',
            'title': stem.replace('_', ' '),
        }

    year = int(match.group(1))
    author = match.group(2)
    journal = match.group(3)
    title = match.group(4).replace('_', ' ')

    return {
        'year': year,
        'first_author': author,
        'journal': journal,
        'title': title,
    }


def create_table(supabase):
    """Create research_articles table via SQL."""
    sql = """
    CREATE TABLE IF NOT EXISTS research_articles (
        id BIGSERIAL PRIMARY KEY,
        year INTEGER,
        first_author TEXT,
        journal TEXT,
        title TEXT,
        filename TEXT NOT NULL UNIQUE,
        storage_path TEXT,
        file_size_kb INTEGER,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_research_articles_year ON research_articles(year);
    CREATE INDEX IF NOT EXISTS idx_research_articles_author ON research_articles(first_author);
    CREATE INDEX IF NOT EXISTS idx_research_articles_title ON research_articles USING gin(to_tsvector('english', title));
    """
    # Execute via the REST SQL endpoint
    import httpx
    resp = httpx.post(
        f"{SUPABASE_URL}/rest/v1/rpc/",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        },
        json={"query": sql},
        timeout=30,
    )
    # If rpc doesn't work, try the SQL endpoint directly
    if resp.status_code != 200:
        # Use the management API
        resp2 = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
            },
            json={"sql": sql},
            timeout=30,
        )
        if resp2.status_code != 200:
            return False
    return True


def main():
    supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

    # ─── 1. Create storage bucket ────────────────────────────────────────
    print(f"Creating storage bucket '{BUCKET_NAME}'...", flush=True)
    try:
        supabase.storage.create_bucket(
            BUCKET_NAME,
            options={"public": False, "file_size_limit": 52428800}  # 50MB limit
        )
        print(f"  Bucket created.", flush=True)
    except Exception as e:
        if "already exists" in str(e).lower() or "Duplicate" in str(e):
            print(f"  Bucket already exists, continuing.", flush=True)
        else:
            print(f"  Bucket creation note: {e}", flush=True)

    # ─── 2. Verify metadata table exists ────────────────────────────────
    print(f"\nVerifying research_articles table...", flush=True)
    try:
        supabase.table("research_articles").select("id").limit(1).execute()
        print(f"  Table exists.", flush=True)
    except Exception as e:
        print(f"  ERROR: research_articles table not found.")
        print(f"  Create it in the Supabase SQL Editor first. See script header for SQL.")
        return

    # ─── 3. Get list of already-uploaded files to support resume ──────────
    print(f"\nChecking existing uploads...", flush=True)
    existing_files = set()
    try:
        # List files in bucket (paginated)
        offset = 0
        while True:
            files = supabase.storage.from_(BUCKET_NAME).list(
                path="",
                options={"limit": 1000, "offset": offset}
            )
            if not files:
                break
            for f in files:
                existing_files.add(f['name'])
            if len(files) < 1000:
                break
            offset += 1000
        print(f"  {len(existing_files)} files already in bucket.", flush=True)
    except Exception as e:
        print(f"  Could not list existing files: {e}", flush=True)

    # ─── 4. Upload PDFs and insert metadata ──────────────────────────────
    pdfs = sorted(ARTICLES_DIR.glob("*.pdf"))
    print(f"\nUploading {len(pdfs)} PDFs to '{BUCKET_NAME}'...", flush=True)

    uploaded = 0
    skipped = 0
    errors = 0
    start_time = time.time()

    for i, pdf_path in enumerate(pdfs):
        filename = pdf_path.name
        storage_path = filename  # flat structure in bucket

        if (i + 1) % 25 == 0 or i == 0:
            elapsed = time.time() - start_time
            rate = (uploaded + skipped) / elapsed if elapsed > 0 else 0
            remaining = (len(pdfs) - i) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(pdfs)}] {elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining | {filename[:50]}...", flush=True)

        # Skip if already uploaded
        if filename in existing_files:
            skipped += 1
            continue

        # Upload file
        try:
            file_bytes = pdf_path.read_bytes()
            file_size_kb = len(file_bytes) // 1024

            supabase.storage.from_(BUCKET_NAME).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )

            # Insert metadata
            meta = parse_filename(filename)
            meta['filename'] = filename
            meta['storage_path'] = storage_path
            meta['file_size_kb'] = file_size_kb

            supabase.table("research_articles").upsert(
                meta, on_conflict="filename"
            ).execute()

            uploaded += 1

        except Exception as e:
            err_str = str(e)
            if "Duplicate" in err_str or "already exists" in err_str:
                skipped += 1
            else:
                print(f"  ERROR [{filename[:40]}]: {err_str[:80]}", flush=True)
                errors += 1

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"UPLOAD COMPLETE ({elapsed:.0f}s)")
    print(f"{'='*60}")
    print(f"Uploaded:  {uploaded}")
    print(f"Skipped:   {skipped} (already existed)")
    print(f"Errors:    {errors}")
    print(f"Total:     {len(pdfs)}")
    print(f"{'─'*60}")
    print(f"Bucket:    {BUCKET_NAME}")
    print(f"Table:     research_articles")


if __name__ == '__main__':
    main()
