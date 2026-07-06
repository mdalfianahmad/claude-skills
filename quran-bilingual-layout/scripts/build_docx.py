#!/usr/bin/env python3
"""
build_docx.py — Build a bilingual Quran docx from a 4-column spreadsheet.

Input CSV columns (header names are flexible, matched case-insensitively):
  - ayah_number      (verse number; required)
  - arabic_uthmani   (Arabic text, rendered VERBATIM — never altered; required)
  - transliteration  (Latin transliteration; required)
  - translation      (English translation; required)
  (surah_number is ignored if present)

The script does NOT decide verse grouping. Grouping is passed in via --spreads,
a JSON list of [start, end] inclusive verse ranges, one per spread. This is
deliberate: grouping is the judgment that the calling agent iterates on using the
render+measure loop. A default 1-verse-per-spread grouping is used only if none
is given (useful for a first structural smoke test, never for final output).

Each spread produces, in document order:
  English 5-column table  →  page break  →  Arabic page paragraph  →  page break

Why this split exists: the Arabic page is the atomic unit (one whole page, never
split). English flows freely and may spill onto a second page — that tail is
correct, not a defect. See SKILL.md.

Output: a .docx (well-formed OOXML, opens in Word and LibreOffice).
"""

import argparse, csv, html, json, os, re, shutil, subprocess, sys, zipfile

# ---------------------------------------------------------------------------
# Sacred-word detection (Allah + Rabb). See references/sacred-words.md.
# Anchored on shadda so it does not false-match unrelated words like
# وَرَبَطنا ("We made firm"). Verified false-positive-free on Al-Kahf, but the
# human MUST confirm green words on the render for any new surah.
# ---------------------------------------------------------------------------
HARAKAT = r'[\u064b-\u0652\u0670]*'   # tanwin, short vowels, sukun, superscript alef
SHADDA  = '\u0651'

_RE_ALLAH = re.compile(r'ل' + HARAKAT + r'ل' + SHADDA + HARAKAT + r'ه')  # ...llâh core
_RE_RABB  = re.compile(r'ر' + HARAKAT + r'ب' + SHADDA)                   # rabb (ba carries shadda)

def is_sacred(token: str) -> bool:
    return bool(_RE_ALLAH.search(token) or _RE_RABB.search(token))

def to_arabic_numeral(n: int) -> str:
    return str(n).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))

def clean_source_arabic(text: str) -> str:
    """Strip any end-of-ayah ornament (U+06DD) and ayah numerals the SOURCE
    already carries, so the build adds exactly one ornament + numeral per verse.

    Some sources (e.g. a CSV exported from an already-laid-out mushaf) end each
    verse's Arabic with ۝, sometimes followed by the verse number in
    Arabic-Indic digits. If we don't remove these, the output gets a DOUBLE
    ornament and a misplaced number (this was a real bug). Bare sources (no
    ornament) are unaffected — there is nothing to strip.

    Note: this removes ALL U+06DD and any Arabic-Indic digit runs that are
    adjacent to an ornament or sit at the very end of the verse. It does NOT
    touch the verse's actual letters or the inline waqf marks (ۖ ۗ ۚ ۜ ۞)."""
    import re as _re
    t = text
    # remove ornament + optional surrounding spaces + optional trailing numerals
    t = _re.sub(r'\s*\u06dd\s*[\u0660-\u0669]*\s*', ' ', t)
    # also strip a trailing standalone Arabic-Indic numeral left at the very end
    t = _re.sub(r'\s*[\u0660-\u0669]+\s*$', ' ', t)
    return t.strip()

# ---------------------------------------------------------------------------
# Colors / sizes — exact values from the approved reference output.
# ---------------------------------------------------------------------------
C_ARABIC   = '1F2937'   # Arabic body + numerals (dark)
C_GREEN    = '008000'   # ornament U+06DD and sacred words
C_TRANSLIT = '374151'   # transliteration (grey)
C_ENGLISH  = '000000'   # English (black)
SZ_ARABIC  = '52'       # 26pt (half-points)
SZ_BODY    = '28'       # 14pt English/translit
SZ_VNUM    = '24'       # 12pt verse numbers
ORNAMENT   = '\u06dd'   # ۝ end-of-ayah marker

# ---------------------------------------------------------------------------
# Run builders
# ---------------------------------------------------------------------------
def _arabic_run(text: str, color: str) -> str:
    # CRITICAL: cs="Scheherazade New" is what makes LibreOffice use the font for
    # rtl runs. eastAsia alone is NOT enough — the ornament renders as tofu
    # without cs set. This was the silent failure mode. Do not remove cs.
    rpr = (
        '<w:rFonts w:ascii="Scheherazade New" w:hAnsi="Scheherazade New" '
        'w:cs="Scheherazade New" w:eastAsia="Scheherazade New"/>'
        '<w:b/><w:bCs/>'
        f'<w:color w:val="{color}"/>'
        f'<w:sz w:val="{SZ_ARABIC}"/><w:szCs w:val="{SZ_ARABIC}"/>'
        '<w:rtl/>'
    )
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{html.escape(text)}</w:t></w:r>'

def _ornament_run(verse_num: int, color: str) -> str:
    # End-of-ayah ornament WITH the verse number ENCLOSED inside it.
    # Scheherazade New's U+06DD encloses the digits that immediately follow it
    # IN THE SAME RUN WITH NO SPACE. This is what Word renders (confirmed against
    # an approved Al-Kahf output: number sits inside the ornament). Do NOT put a
    # space between the ornament and the digits, and do NOT split them into two
    # runs — either breaks the enclosure and the number drifts outside.
    #
    # Engine note: LibreOffice (our render/QA engine) is inconsistent about this
    # enclosure — it may show the number beside the ornament in the verification
    # PDF. Word is the target and encloses it correctly. See word-deltas.md.
    text = ORNAMENT + to_arabic_numeral(verse_num)
    rpr = (
        '<w:rFonts w:ascii="Scheherazade New" w:hAnsi="Scheherazade New" '
        'w:cs="Scheherazade New" w:eastAsia="Scheherazade New"/>'
        '<w:b/><w:bCs/>'
        f'<w:color w:val="{color}"/>'
        f'<w:sz w:val="{SZ_ARABIC}"/><w:szCs w:val="{SZ_ARABIC}"/>'
        '<w:rtl/>'
    )
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{html.escape(text)}</w:t></w:r>'

def _latin_run(text: str, color: str, *, italic=False, bold=False, sz=SZ_BODY) -> str:
    rpr = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/>'
    if bold:   rpr += '<w:b/><w:bCs/>'
    if italic: rpr += '<w:i/><w:iCs/>'
    rpr += f'<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{html.escape(text)}</w:t></w:r>'

# ---------------------------------------------------------------------------
# Arabic page: one centered bidi paragraph. Verses run continuously, separated
# only by the green ornament; the numeral (dark) follows the ornament. Sacred
# words inside the verse are emitted as their own green runs.
# ---------------------------------------------------------------------------
def build_arabic_page(verse_nums, verses):
    # Page break is the FIRST RUN of this paragraph (not a standalone empty
    # paragraph). This is the structure the human hand-fixed the reference to use
    # on its tallest spread, precisely because a standalone break paragraph after
    # a nearly-full English page produces a blank page. A break run inside a
    # content paragraph advances exactly one page from wherever the English ended
    # — whether English filled its page exactly or spilled a tail — and never
    # leaves a blank. Use it on every Arabic page for uniformity.
    runs = ['<w:r><w:br w:type="page"/></w:r>']
    for i, vn in enumerate(verse_nums):
        arabic = clean_source_arabic(verses[vn]['arabic'].strip())
        buf = []
        def flush():
            if buf:
                runs.append(_arabic_run(' '.join(buf) + ' ', C_ARABIC))
                buf.clear()
        for tok in arabic.split():
            if is_sacred(tok):
                flush()
                runs.append(_arabic_run(tok + ' ', C_GREEN))
            else:
                buf.append(tok)
        flush()
        # ornament with the verse number ENCLOSED inside it (Scheherazade New,
        # one run, no space — see _ornament_run), green.
        runs.append(_ornament_run(vn, C_GREEN))
        if i != len(verse_nums) - 1:
            runs.append(_arabic_run(' ', C_ARABIC))  # space before next verse
    ppr = ('<w:pPr><w:bidi/>'
           '<w:spacing w:before="431" w:after="431" w:line="276" w:lineRule="auto"/>'
           '<w:jc w:val="center"/></w:pPr>')
    return f'<w:p>{ppr}{"".join(runs)}</w:p>'

# ---------------------------------------------------------------------------
# English page: 5-column borderless table.
# grid: [verse#L | transliteration | spacer | verse#R | English]
# ---------------------------------------------------------------------------
def build_english_table(verse_nums, verses, page_break_before=False):
    tblpr = (
        '<w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
        '<w:tblBorders>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>'
        '</w:tblBorders>'
        '<w:tblCellMar><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tblCellMar>'
        '</w:tblPr>'
    )
    grid = ('<w:tblGrid>'
            '<w:gridCol w:w="300"/><w:gridCol w:w="3850"/><w:gridCol w:w="624"/>'
            '<w:gridCol w:w="300"/><w:gridCol w:w="3952"/></w:tblGrid>')

    def para(inner, brk=False):
        bb = '<w:pageBreakBefore/>' if brk else ''
        return (f'<w:p><w:pPr>{bb}<w:spacing w:after="180" w:line="276" w:lineRule="auto"/></w:pPr>'
                f'{inner}</w:p>')
    def cell(pct, inner, margin=None, brk=False):
        m = f'<w:tcMar>{margin}</w:tcMar>' if margin else ''
        return f'<w:tc><w:tcPr><w:tcW w:w="{pct}" w:type="pct"/>{m}</w:tcPr>{para(inner, brk)}</w:tc>'

    rows = []
    for idx, vn in enumerate(verse_nums):
        v = verses[vn]
        c1 = cell(168,  _latin_run(str(vn), C_TRANSLIT, bold=True, sz=SZ_VNUM),
                  brk=(idx == 0 and page_break_before))
        c2 = cell(2134, _latin_run(v['translit'].strip(), C_TRANSLIT, italic=True),
                  margin='<w:right w:w="144" w:type="dxa"/>')
        c3 = cell(347,  '')
        c4 = cell(168,  _latin_run(str(vn), C_ENGLISH, bold=True, sz=SZ_VNUM))
        c5 = cell(2182, _latin_run(v['english'].strip(), C_ENGLISH),
                  margin='<w:left w:w="144" w:type="dxa"/>')
        rows.append(f'<w:tr>{c1}{c2}{c3}{c4}{c5}</w:tr>')
    return f'<w:tbl>{tblpr}{grid}{"".join(rows)}</w:tbl>'

def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

# ---------------------------------------------------------------------------
# Document assembly + packaging
# ---------------------------------------------------------------------------
SECTPR = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
          'w:header="708" w:footer="708" w:gutter="0"/>'
          '<w:cols w:space="720"/></w:sectPr>')

def assemble(spreads, verses):
    body = []
    for si, (start, end) in enumerate(spreads):
        nums = [n for n in range(start, end + 1) if n in verses]
        if not nums:
            continue
        if si > 0:
            body.append(page_break())   # standalone break before later English
        body.append(build_english_table(nums, verses))
        body.append(build_arabic_page(nums, verses))   # leading break run inside
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body>{"".join(body)}{SECTPR}</w:body></w:document>')

def write_docx(document_xml, out_path):
    tmp = out_path + '.parts'
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.makedirs(os.path.join(tmp, 'word', '_rels'))
    os.makedirs(os.path.join(tmp, '_rels'))
    with open(os.path.join(tmp, 'word', 'document.xml'), 'w', encoding='utf-8') as f:
        f.write(document_xml)
    with open(os.path.join(tmp, '_rels', '.rels'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
                'Target="word/document.xml"/></Relationships>')
    with open(os.path.join(tmp, 'word', '_rels', 'document.xml.rels'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
    with open(os.path.join(tmp, '[Content_Types].xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                '</Types>')
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml first is conventional
        z.write(os.path.join(tmp, '[Content_Types].xml'), '[Content_Types].xml')
        for root, _, files in os.walk(tmp):
            for fn in files:
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, tmp)
                if arc == '[Content_Types].xml':
                    continue
                z.write(full, arc)
    shutil.rmtree(tmp)

# ---------------------------------------------------------------------------
# CSV loading with flexible header matching
# ---------------------------------------------------------------------------
def load_csv(path):
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in reader.fieldnames}
        def pick(*names):
            # 1. exact match on a known alias
            for n in names:
                if n in cols:
                    return cols[n]
            # 2. fallback: any column whose name CONTAINS an alias as a substring
            #    (covers e.g. 'english_saheeh_international', 'arabic_uthmani_text').
            for n in names:
                for low, orig in cols.items():
                    if n in low:
                        return orig
            raise SystemExit(f"CSV missing a column for one of: {names}. Found: {list(cols)}")
        ay = pick('ayah_number', 'ayah', 'verse', 'verse_number', 'number')
        ar = pick('arabic_uthmani', 'arabic', 'uthmani')
        tl = pick('transliteration', 'translit')
        en = pick('english', 'translation')
        verses = {}
        for row in reader:
            try:
                n = int(str(row[ay]).strip())
            except (ValueError, TypeError):
                continue
            verses[n] = {
                'arabic':   row[ar] or '',
                'translit': row[tl] or '',
                'english':  row[en] or '',
            }
    if not verses:
        raise SystemExit("No verses parsed from CSV.")
    return verses

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv', help='input spreadsheet (.csv)')
    ap.add_argument('-o', '--out', required=True, help='output .docx path')
    ap.add_argument('--spreads', help='JSON list of [start,end] inclusive verse ranges')
    args = ap.parse_args()

    verses = load_csv(args.csv)

    if args.spreads:
        spreads = json.loads(args.spreads)
    else:
        # structural smoke-test default ONLY: one verse per spread. Never final.
        nums = sorted(verses)
        spreads = [[n, n] for n in nums]
        print("WARNING: no --spreads given; using 1-verse-per-spread (smoke test only).",
              file=sys.stderr)

    doc = assemble(spreads, verses)
    write_docx(doc, args.out)

    # report sacred words for human confirmation
    green = []
    for vn in sorted(verses):
        toks = [t for t in verses[vn]['arabic'].split() if is_sacred(t)]
        if toks:
            green.append((vn, toks))
    print(f"Wrote {args.out} ({len(spreads)} spreads, {len(verses)} verses).")
    print(f"Green sacred words flagged in {len(green)} verses — CONFIRM on the render:")
    for vn, toks in green:
        print(f"  v{vn}: {' '.join(toks)}")

if __name__ == '__main__':
    main()
