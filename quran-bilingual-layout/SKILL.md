---
name: quran-bilingual-layout
description: >
  Build a print-ready bilingual Quran document from a spreadsheet of verses —
  alternating spreads where each English+transliteration page faces a matching
  Arabic page. Use this whenever the user wants to lay out, typeset, format, or
  produce a bilingual (Arabic + English + transliteration) Quran or surah as a
  Word/docx or PDF from a CSV/Excel of ayat, or mentions a "bilingual mushaf",
  "surah layout", "Quran spread", facing Arabic/English pages, Scheherazade New
  Arabic typesetting, green ayah ornaments, or laying out a surah like Al-Kahf.
  Trigger even if they don't name the format precisely — if the input is a table
  of verse number / Arabic / transliteration / translation and the goal is a
  formatted bilingual document, this skill applies.
license: Proprietary.
---

# Bilingual Quran layout

Turn a spreadsheet of verses into a print-ready bilingual document: for each
spread, an English + transliteration page (a 5-column table) faces a matching
Arabic page (Scheherazade New, green end-of-ayah ornaments, green sacred words).
Deliver the `.docx` plus a verification PDF.

This skill renders the user's Arabic text VERBATIM. It never alters, re-vocalizes,
or "corrects" the sacred text — whatever vocalization is in the spreadsheet is
what ships. The only things the skill adds to the Arabic are the end-of-ayah
ornament, the verse numeral, and color.

One exception, for correctness: if the source Arabic already contains end-of-ayah
ornaments (U+06DD ۝) and/or ayah numerals, the build strips those first so it can
add exactly one ornament+numeral per verse — otherwise the output shows a double
ornament. Inline waqf/pause marks (ۖ ۗ ۚ ۜ ۞) are preserved. This only removes
ayah-end markup, never the Quranic text itself.

## Input

A CSV/Excel with one row per ayah and these columns (header names are matched
case-insensitively; a `surah_number` column, if present, is ignored):

- verse number — `ayah_number` / `ayah` / `verse`
- Arabic — `arabic_uthmani` / `arabic`
- transliteration — `transliteration` / `translit`
- English — `translation` / `english`

## Output

- `<name>.docx` — the deliverable, A4, opens in Word and LibreOffice.
- `<name>.pdf` — the LibreOffice verification render the loop checked. Always
  give the user both; Word wraps Arabic slightly differently (see below).

## Environment

These scripts assume LibreOffice, poppler (`pdftotext`, `pdftoppm`, `pdffonts`),
Python with Pillow, and curl are available. `setup_fonts.sh` installs
Scheherazade New. In a fresh sandbox, install Pillow first:
`pip install Pillow --break-system-packages`.

`render.sh` invokes LibreOffice through the office helper's `run_soffice`,
foreground with a timeout — this is the only reliable way in the sandbox. If
rendering hangs or the font appears missing intermittently, see
`references/troubleshooting.md` (these failure modes are handled by the scripts,
but the notes explain what is happening).

## Workflow

Do these in order. The heart is the build → render → measure → regroup loop;
read `references/layout-loop.md` before starting it.

1. **Install the font.** `bash scripts/setup_fonts.sh`. Without Scheherazade New
   the Arabic silently falls back and the ornament renders as a box.

2. **Read the input.** Confirm the four columns and the verse range.

3. **Pick an initial grouping.** A JSON list of `[start, end]` inclusive verse
   ranges, one per spread. Start generous: ~5–7 short verses per spread, ~3–4 if
   verses are long. (For a first structural check only, you can omit `--spreads`
   and the script uses one verse per spread — never ship that.)

4. **Build.** `python scripts/build_docx.py INPUT.csv -o OUT.docx --spreads '[[1,7],[8,14],...]'`
   The script prints every verse where it colored a sacred word green — keep
   this list for the human confirmation step.

5. **Render + verify font.** `bash scripts/render.sh OUT.docx OUTDIR`. This
   converts to PDF, rasterizes pages, and FAILS LOUDLY if Scheherazade New did
   not embed (meaning the Arabic used a substitute — never trust that render).

6. **Measure.** `python scripts/measure_fill.py OUTDIR/OUT.pdf`. It classifies
   each page (English / Arabic / blank), reports fill % as INFORMATION, and flags
   the two real defects: BLANK pages and SPLIT ARABIC (two Arabic pages in a row,
   meaning a spread's Arabic overflowed). It prints CLEAN only when there are no
   blanks and no splits. Fill % is NOT a pass/fail — the reference legitimately
   ranges 59–94%.

7. **Regroup and repeat.** For each BLANK or SPLIT, the offending spread has too
   many verses: move its last verse into the next spread, then rebuild → render →
   measure. The moved verse cascades, so the next spread may need its own fix —
   keep iterating until CLEAN. Long verses can force a spread down to 2 verses;
   that is correct. Don't regenerate already-good spreads — preserve approved
   layout verbatim. Full reasoning: `references/layout-loop.md`. On Al-Kahf this
   converges in ~3–4 iterations.

8. **Human QA — keep the user in the loop.** Show the user the rendered PDF (or
   key page images) and the list of green sacred words. Ask them to confirm the
   words and the layout. Act on feedback like "combine these pages" by regrouping
   and rebuilding — don't hand-edit the docx in ways the next rebuild would lose.

9. **Deliver.** Present both the `.docx` and the verification `.pdf`.

## Two things to tell the user at hand-off

- **Word vs LibreOffice.** The loop is calibrated in LibreOffice; Word may wrap
  Arabic slightly differently. If a blank page appears in Word that wasn't in the
  PDF, the quick fix is to delete the empty paragraph(s) at the top of that blank
  page in Word so the previous section pulls up. Record any consistent
  difference in `references/word-deltas.md` so the loop improves.
- **Sacred text.** The Arabic is rendered exactly as supplied. If they want
  different vocalization, they change the spreadsheet — the skill won't generate
  or alter harakat.

## Reference files

- `references/encoding-spec.md` — exact OOXML: fonts (incl. the critical `cs`
  font-slot fix), colors, sizes, run structure, page layout. Read before editing
  `build_docx.py`.
- `references/sacred-words.md` — the Allah/Rabb matcher, why it's shadda-anchored,
  the false-positive it avoids, and its limits on other surahs.
- `references/layout-loop.md` — grouping judgment, the fill band, why blank pages
  happen, the regroup fix, and the Word hand-off.
- `references/word-deltas.md` — log of confirmed Word-vs-LibreOffice differences;
  starts empty, grows from user feedback.
- `references/troubleshooting.md` — render/font/environment failure modes and how
  the scripts handle them. Read if rendering misbehaves.

## Scripts

- `scripts/setup_fonts.sh` — install Scheherazade New (idempotent).
- `scripts/build_docx.py` — CSV + `--spreads` → docx. Owns all Arabic encoding.
- `scripts/render.sh` — docx → PDF + page JPEGs; verifies font embedding.
- `scripts/measure_fill.py` — classify pages, measure fill, flag blanks and
  out-of-band Arabic pages; the loop's self-correction signal.
