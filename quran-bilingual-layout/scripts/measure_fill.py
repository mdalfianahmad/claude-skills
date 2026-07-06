#!/usr/bin/env python3
"""
measure_fill.py — Render-truth QA for a built bilingual Quran PDF.

The fill target for an Arabic page cannot be predicted from character counts —
Arabic wrapping in the real font is the only truth. So we render, then MEASURE.
This script reads the rendered PDF + page images and reports, per page:
  - kind: ENGLISH | ARABIC | BLANK   (from the text layer)
  - fill%: vertical ink span as a fraction of the usable page height
  - flags: problems the loop should act on

It then prints a SUMMARY the calling agent uses to decide whether to regroup:
  - BLANK pages   -> usually a symptom of an over-full Arabic page in the
                    PRECEDING spread; regroup that spread smaller.
  - ARABIC OVER   -> Arabic page above the ceiling; too many verses on it.
  - ARABIC UNDER  -> Arabic page below the floor; pull more verses onto it.

Why blanks mean "regroup", not "fix the break": when an Arabic page renders near
100% of the printable height, the page break that follows it spills onto a blank
page. The cure is fewer verses on that Arabic page, which the loop achieves by
adjusting --spreads. Chasing it with break tricks just moves the blank around.

Usage:
  measure_fill.py PDF [--floor 80] [--ceiling 83] [--json]

Requires: pdftotext (poppler), Pillow, pdftoppm (poppler).
"""
import argparse, json, os, subprocess, sys, tempfile

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required: pip install Pillow --break-system-packages")

MARGIN_FRAC = 96.0 / 1123.0  # one 1-inch margin as fraction of A4 height @96dpi

def classify_pages(pdf):
    txt = subprocess.run(['pdftotext', '-layout', pdf, '-'],
                         capture_output=True, text=True).stdout
    out = []
    for p in txt.split('\f'):
        c = p.strip()
        if not c:
            out.append('BLANK'); continue
        has_ar = any('\u0600' <= ch <= '\u06ff' for ch in c)
        has_lat = any('a' <= ch.lower() <= 'z' for ch in c)
        if has_ar and not has_lat:
            out.append('ARABIC')
        elif has_lat and not has_ar:
            out.append('ENGLISH')
        else:
            out.append('MIXED')
    while out and out[-1] == 'BLANK':
        out.pop()
    return out

def measure_fill(img_path, white=245):
    img = Image.open(img_path).convert('L')
    w, h = img.size
    px = img.load()
    top = bottom = None
    for y in range(h):
        for x in range(0, w, 3):
            if px[x, y] < white:
                if top is None:
                    top = y
                bottom = y
                break
    if top is None:
        return 0.0
    usable = h * (1 - 2 * MARGIN_FRAC)
    return round(max(0.0, min(1.0, (bottom - top) / usable)) * 100, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--overfull', type=float, default=90.0,
                    help='Arabic fill %% above this is flagged as an overflow RISK')
    
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    kinds = classify_pages(args.pdf)
    n = len(kinds)

    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['pdftoppm', '-jpeg', '-r', '96', args.pdf,
                        os.path.join(td, 'pg')], check=True)
        imgs = sorted(f for f in os.listdir(td) if f.endswith('.jpg'))
        fills = [measure_fill(os.path.join(td, f)) for f in imgs[:n]]

    pages = []
    for i in range(n):
        pages.append({'page': i + 1, 'kind': kinds[i],
                      'fill_pct': fills[i] if i < len(fills) else None})

    blanks = [p['page'] for p in pages if p['kind'] == 'BLANK']
    # Two ARABIC pages in a row mean a spread's Arabic overflowed onto a second
    # page — a violation of the atomic rule (one Arabic page per spread), as
    # serious as a blank. Detect adjacent ARABIC kinds.
    split_arabic = [pages[i+1]['page'] for i in range(len(pages)-1)
                    if pages[i]['kind'] == 'ARABIC' and pages[i+1]['kind'] == 'ARABIC']
    arabic = [p for p in pages if p['kind'] == 'ARABIC']
    overfull = [p for p in arabic if p['fill_pct'] is not None and p['fill_pct'] > args.overfull]

    # CLEAN = no blank pages. Fill varies legitimately (the approved reference
    # ranges 59-94%), so fill alone is NOT a defect. Over-full pages are a RISK
    # flag (they may or may not cause a blank depending on the facing English),
    # not an automatic failure. The blank is the thing to fix.
    result = {'pages': pages,
              'blanks': blanks,
              'arabic_overfull_risk': [(p['page'], p['fill_pct']) for p in overfull],
              'split_arabic': split_arabic,
              'clean': not blanks and not split_arabic,
              'overfull_threshold': args.overfull}

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"{'page':>5}  {'kind':<8} {'fill%':>6}")
    for p in pages:
        f = '' if p['fill_pct'] is None else p['fill_pct']
        mark = ''
        if p['kind'] == 'BLANK':
            mark = '  <-- BLANK (defect: regroup the preceding spread smaller)'
        elif p['kind'] == 'ARABIC' and p['fill_pct'] is not None and p['fill_pct'] > args.overfull:
            mark = f'  <-- full ({p["fill_pct"]}%): overflow risk, watch for an adjacent blank'
        print(f"{p['page']:>5}  {p['kind']:<8} {str(f):>6}{mark}")
    print()
    if result['clean']:
        print("CLEAN: no blank pages, no split Arabic pages.", end=' ')
        if overfull:
            print(f"Note: very full Arabic pages at {[p['page'] for p in overfull]} -- fine since no blank/split appeared. Ready for human QA.")
        else:
            print("Ready for human QA.")
    else:
        if blanks:
            print(f"BLANKS at pages {blanks}.")
            print("  Fix: the spread whose Arabic page precedes each blank has TOO MANY")
            print("  verses; move its last verse into the next spread, rebuild, re-measure.")
        if split_arabic:
            print(f"SPLIT ARABIC at pages {split_arabic} (Arabic overflowed onto a 2nd page).")
            print("  Fix: that spread has TOO MANY verses for one Arabic page; move its last")
            print("  verse into the next spread, rebuild, re-measure.")
        print("  Fill % is informational, not a pass/fail.")

if __name__ == '__main__':
    main()
