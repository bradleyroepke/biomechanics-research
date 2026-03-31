#!/usr/bin/env python3
"""
Extract high-quality figures from academic PDF collection.

Caption-aware extraction with quality scoring. Produces a curated repository
of anatomical illustrations, surgical photos, biomechanical diagrams, and
conceptual schematics — filtering out tables, data dumps, logos, and artifacts.

Usage: python3 extract_figures.py
"""

import csv
import hashlib
import io
import os
import re
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageOps

# ─── Configuration ───────────────────────────────────────────────────────────

ARTICLES_DIR = Path(__file__).parent / "Articles"
OUTPUT_DIR = ARTICLES_DIR / "_figures"
UNCAPTIONED_DIR = OUTPUT_DIR / "_uncaptioned"
INDEX_CSV = OUTPUT_DIR / "index.csv"

MIN_DIM = 100
MAX_DIM = 3000
MIN_FILE_SIZE = 2048
MAX_ASPECT = 3.5
SCANNED_THRESHOLD = 0.80
SCORE_THRESHOLD = 4
CROP_PADDING = 10
MAX_PAGES = 100          # Skip books/monographs
MAX_IMAGES_PER_PAGE = 30 # Skip pages with fragmented text-as-images

CAPTION_RE = re.compile(
    r'(Fig(?:ure|\.)\s*(\d+[a-zA-Z]?))'
    r'|(Diagram\s*(\d*))'
    r'|(Illustration\s*(\d*))'
    r'|(Schematic\s*(\d*))'
    r'|(Framework\s*(\d*))'
    r'|(Chart\s*(\d*))',
    re.IGNORECASE
)


def is_scanned_document(doc):
    """Quick check: sample first 5 pages for large single images."""
    if len(doc) == 0:
        return True
    check_pages = min(len(doc), 5)
    large_pages = 0
    for i in range(check_pages):
        page = doc[i]
        images = page.get_images(full=True)
        if len(images) == 1:
            xref = images[0][0]
            try:
                base = doc.extract_image(xref)
                if max(base['width'], base['height']) > 2400:
                    large_pages += 1
            except Exception:
                pass
    return (large_pages / check_pages) > SCANNED_THRESHOLD


def find_captions_on_page(text_blocks):
    """Pre-scan all text blocks on a page for figure captions. Returns list of (rect, fig_num, caption_text)."""
    captions = []
    for tb in text_blocks:
        if tb.get("type") != 0:
            continue
        full_text = " ".join(
            span["text"] for line in tb["lines"] for span in line["spans"]
        ).strip()
        match = CAPTION_RE.search(full_text)
        if match:
            groups = match.groups()
            fig_num = ""
            for i in range(0, len(groups), 2):
                if groups[i] is not None:
                    fig_num = groups[i + 1] if groups[i + 1] else ""
                    break
            captions.append((fitz.Rect(tb["bbox"]), fig_num, full_text[:200]))
    return captions


def match_image_to_caption(img_rect, captions):
    """Find closest caption within 60pt below or above an image."""
    best = None
    best_dist = 60
    for cap_rect, fig_num, cap_text in captions:
        # Horizontal overlap
        h_overlap = min(img_rect.x1, cap_rect.x1) - max(img_rect.x0, cap_rect.x0)
        if h_overlap < 20:
            continue
        dist_below = cap_rect.y0 - img_rect.y1
        dist_above = img_rect.y0 - cap_rect.y1
        dist = min(d for d in [dist_below, dist_above, 999] if d >= 0)
        if dist < best_dist:
            best_dist = dist
            best = (fig_num, cap_text)
    return best


def compute_quality_score(pil_img):
    """Score 0-10. Higher = more likely a real figure."""
    arr = np.array(pil_img.convert('RGB'))
    score = 0
    h, w = arr.shape[:2]

    # Subsample large images for speed
    if h > 400 or w > 400:
        step = max(h, w) // 400
        arr_sub = arr[::step, ::step]
    else:
        arr_sub = arr

    r, g, b = arr_sub[:,:,0].astype(np.float32), arr_sub[:,:,1].astype(np.float32), arr_sub[:,:,2].astype(np.float32)
    max_rgb = np.maximum(np.maximum(r, g), b)
    min_rgb = np.minimum(np.minimum(r, g), b)
    mask = max_rgb > 0
    sat = np.zeros_like(max_rgb)
    sat[mask] = (max_rgb[mask] - min_rgb[mask]) / max_rgb[mask]
    if np.mean(sat) > 0.1:
        score += 3

    gray = np.array(pil_img.convert('L'))
    if gray.shape[0] > 400 or gray.shape[1] > 400:
        step = max(gray.shape) // 400
        gray = gray[::step, ::step]
    hist = np.histogram(gray, bins=256, range=(0, 256))[0]
    hist_norm = hist / hist.sum()
    hist_pos = hist_norm[hist_norm > 0]
    entropy = -np.sum(hist_pos * np.log2(hist_pos))
    if entropy > 5.0:
        score += 2
    elif entropy > 3.0:
        score += 1

    white_pct = np.mean(np.all(arr_sub > 240, axis=2))
    if white_pct < 0.50:
        score += 2
    if white_pct > 0.85:
        score -= 4

    # Color variance as proxy for visual complexity (fast alternative to unique color count)
    color_std = np.std(arr_sub)
    if color_std > 50:
        score += 1

    if min(w, h) > 300:
        score += 1
    if entropy < 1.0:
        score -= 3
    if max(w, h) / max(min(w, h), 1) > MAX_ASPECT:
        score -= 2

    return max(0, min(10, score))


def autocrop_whitespace(pil_img, ext):
    """Crop whitespace, return cropped PIL Image."""
    if pil_img.mode in ('RGBA', 'P', 'LA'):
        bg = Image.new('RGB', pil_img.size, (255, 255, 255))
        if pil_img.mode == 'P':
            pil_img = pil_img.convert('RGBA')
        if 'A' in pil_img.mode:
            bg.paste(pil_img, mask=pil_img.split()[-1])
        else:
            bg.paste(pil_img)
        pil_img = bg
    elif pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    inverted = ImageOps.invert(pil_img)
    bbox = inverted.getbbox()
    if bbox is None:
        return pil_img

    x0 = max(0, bbox[0] - CROP_PADDING)
    y0 = max(0, bbox[1] - CROP_PADDING)
    x1 = min(pil_img.width, bbox[2] + CROP_PADDING)
    y1 = min(pil_img.height, bbox[3] + CROP_PADDING)
    cropped = pil_img.crop((x0, y0, x1, y1))

    if cropped.width < 80 or cropped.height < 80:
        return pil_img
    return cropped


def save_image(pil_img, path, ext):
    """Save PIL image in appropriate format."""
    fmt = 'JPEG' if ext in ('jpeg', 'jpg') else 'PNG'
    if fmt == 'JPEG':
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        pil_img.save(path, format=fmt, quality=95)
    else:
        pil_img.save(path, format=fmt)


def sanitize_dirname(name, max_len=60):
    name = Path(name).stem
    name = re.sub(r'[^\w\s\-]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:max_len]


def extract_all():
    pdfs = sorted(ARTICLES_DIR.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs in {ARTICLES_DIR}", flush=True)

    OUTPUT_DIR.mkdir(exist_ok=True)
    UNCAPTIONED_DIR.mkdir(exist_ok=True)

    seen_hashes = set()
    index_rows = []
    stats = {
        'pdfs_processed': 0, 'pdfs_skipped_scanned': 0, 'pdfs_skipped_error': 0,
        'captioned_saved': 0, 'uncaptioned_saved': 0,
        'filtered_size': 0, 'filtered_score': 0, 'filtered_dedup': 0,
    }
    start_time = time.time()

    for i, pdf_path in enumerate(pdfs):
        if (i + 1) % 50 == 0 or i == 0:
            elapsed = time.time() - start_time
            print(f"  [{i+1}/{len(pdfs)}] {elapsed:.0f}s elapsed | {pdf_path.name[:50]}...", flush=True)

        try:
            doc = fitz.open(str(pdf_path))
        except Exception:
            stats['pdfs_skipped_error'] += 1
            continue

        if len(doc) == 0 or len(doc) > MAX_PAGES:
            stats['pdfs_skipped_error'] += 1
            doc.close()
            continue

        if is_scanned_document(doc):
            stats['pdfs_skipped_scanned'] += 1
            doc.close()
            continue

        stats['pdfs_processed'] += 1
        dir_name = sanitize_dirname(pdf_path.name)
        fig_counter = {}

        for page_num in range(len(doc)):
            page = doc[page_num]

            try:
                blocks = page.get_text("dict")["blocks"]
            except Exception:
                blocks = []

            text_blocks = [b for b in blocks if b.get("type") == 0]
            img_blocks = [b for b in blocks if b.get("type") == 1]
            captions = find_captions_on_page(text_blocks)

            # Also get figure references from raw page text as fallback
            page_fig_refs = re.findall(r'(?i)Fig(?:ure|\.)\s*(\d+[a-zA-Z]?)', page.get_text())

            images = page.get_images(full=True)
            if len(images) > MAX_IMAGES_PER_PAGE:
                continue
            seen_xrefs = set()

            for img_idx, img_info in enumerate(images):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                try:
                    base = doc.extract_image(xref)
                except Exception:
                    continue

                w, h = base['width'], base['height']
                ext = base['ext'] or 'png'
                img_bytes = base['image']

                # Hard filters
                if min(w, h) < MIN_DIM or max(w, h) > MAX_DIM:
                    stats['filtered_size'] += 1
                    continue
                if len(img_bytes) < MIN_FILE_SIZE:
                    stats['filtered_size'] += 1
                    continue
                if max(w, h) / max(min(w, h), 1) > MAX_ASPECT:
                    stats['filtered_size'] += 1
                    continue

                # Dedup
                img_hash = hashlib.md5(img_bytes).hexdigest()
                if img_hash in seen_hashes:
                    stats['filtered_dedup'] += 1
                    continue
                seen_hashes.add(img_hash)

                # Open with PIL once, reuse for scoring and cropping
                try:
                    pil_img = Image.open(io.BytesIO(img_bytes))
                except Exception:
                    continue

                # Try to match to caption via image block positions
                fig_num = None
                caption_text = None
                for ib in img_blocks:
                    ib_rect = fitz.Rect(ib["bbox"])
                    if ib_rect.width < 30 or ib_rect.height < 30:
                        continue
                    # Check proportional match
                    ratio_w = w / ib_rect.width if ib_rect.width > 0 else 999
                    ratio_h = h / ib_rect.height if ib_rect.height > 0 else 999
                    if abs(ratio_w - ratio_h) < 1.0 and 0.1 < ratio_w < 30:
                        result = match_image_to_caption(ib_rect, captions)
                        if result:
                            fig_num, caption_text = result
                            break

                # Fallback: if page has exactly 1 qualifying image and figure refs
                if fig_num is None and len(seen_xrefs) == len(images) and page_fig_refs:
                    # Count qualifying images on this page
                    qualifying = sum(1 for ii in images if ii[0] in seen_xrefs)
                    if qualifying == 1 and len(page_fig_refs) >= 1:
                        fig_num = page_fig_refs[0]

                has_caption = fig_num is not None
                score = compute_quality_score(pil_img)

                if has_caption:
                    # Auto-include captioned figures
                    fig_label = fig_num if fig_num else "X"
                    fig_key = f"Fig{fig_label}"
                    if fig_key in fig_counter:
                        fig_counter[fig_key] += 1
                        fig_label = f"{fig_label}_{fig_counter[fig_key]}"
                    else:
                        fig_counter[fig_key] = 0

                    filename = f"Fig{fig_label}_p{page_num+1:02d}_s{score}.{ext}"
                    out_dir = OUTPUT_DIR / dir_name
                    out_dir.mkdir(exist_ok=True)

                    cropped = autocrop_whitespace(pil_img, ext)
                    save_image(cropped, out_dir / filename, ext)
                    stats['captioned_saved'] += 1

                    index_rows.append({
                        'filename': f"{dir_name}/{filename}",
                        'source_pdf': pdf_path.name,
                        'page': page_num + 1,
                        'fig_number': fig_num or "",
                        'caption_text': (caption_text or "")[:200],
                        'width': w, 'height': h, 'format': ext,
                        'size_kb': round(os.path.getsize(out_dir / filename) / 1024, 1) if (out_dir / filename).exists() else 0,
                        'quality_score': score,
                        'has_caption': True,
                    })
                else:
                    if score < SCORE_THRESHOLD:
                        stats['filtered_score'] += 1
                        continue

                    filename = f"img_p{page_num+1:02d}_{img_idx:03d}_s{score}.{ext}"
                    out_dir = UNCAPTIONED_DIR / dir_name
                    out_dir.mkdir(exist_ok=True)

                    cropped = autocrop_whitespace(pil_img, ext)
                    save_image(cropped, out_dir / filename, ext)
                    stats['uncaptioned_saved'] += 1

                    index_rows.append({
                        'filename': f"_uncaptioned/{dir_name}/{filename}",
                        'source_pdf': pdf_path.name,
                        'page': page_num + 1,
                        'fig_number': "",
                        'caption_text': "",
                        'width': w, 'height': h, 'format': ext,
                        'size_kb': round(os.path.getsize(out_dir / filename) / 1024, 1) if (out_dir / filename).exists() else 0,
                        'quality_score': score,
                        'has_caption': False,
                    })

        doc.close()

    # Write index CSV
    if index_rows:
        fieldnames = [
            'filename', 'source_pdf', 'page', 'fig_number', 'caption_text',
            'width', 'height', 'format', 'size_kb', 'quality_score', 'has_caption'
        ]
        with open(INDEX_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in sorted(index_rows, key=lambda r: (r['source_pdf'], r['page'])):
                writer.writerow(row)

    elapsed = time.time() - start_time
    total_saved = stats['captioned_saved'] + stats['uncaptioned_saved']
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE ({elapsed:.0f}s)")
    print(f"{'='*60}")
    print(f"PDFs processed:          {stats['pdfs_processed']}")
    print(f"PDFs skipped (scanned):  {stats['pdfs_skipped_scanned']}")
    print(f"PDFs skipped (error):    {stats['pdfs_skipped_error']}")
    print(f"{'─'*60}")
    print(f"Captioned figures saved: {stats['captioned_saved']}")
    print(f"Uncaptioned figs saved:  {stats['uncaptioned_saved']}")
    print(f"TOTAL figures saved:     {total_saved}")
    print(f"{'─'*60}")
    print(f"Filtered (size/aspect):  {stats['filtered_size']}")
    print(f"Filtered (low score):    {stats['filtered_score']}")
    print(f"Filtered (duplicate):    {stats['filtered_dedup']}")
    print(f"{'─'*60}")
    print(f"Index:   {INDEX_CSV}")
    print(f"Figures: {OUTPUT_DIR}")


if __name__ == '__main__':
    extract_all()
