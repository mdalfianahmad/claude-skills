# Encoding spec — the exact OOXML the build produces

This is the ground truth reverse-engineered from the approved reference output
(`Al_Kahfi_A_safe.docx`) and verified by rendering. `build_docx.py` implements
all of it; this file exists so a human (or a future edit) can check the script
against the spec without re-deriving it. If you change `build_docx.py`, update
this file too.

## Page / section

- A4 portrait: `<w:pgSz w:w="11906" w:h="16838"/>` (DXA).
- 1-inch margins: `top/right/bottom/left = 1440`, `header/footer = 708`.
- Single section, single column. One `<w:sectPr>` at the end of the body.

## Document order (per spread)

```
[English table]
[page break paragraph]        (only BEFORE spreads after the first)
[Arabic paragraph]            (page break is the FIRST RUN inside this paragraph)
```

So the body is: `EngTable, Arabic, break, EngTable, Arabic, break, EngTable, ...`
The Arabic paragraph leads with a hard page-break run; the break before each
later English table is a standalone break paragraph. See `references/layout-loop.md`
for *why* the break sits where it does (it is the fix for blank pages).

## English page — 5-column borderless table

- `<w:tblW w:w="5000" w:type="pct"/>`, all borders `none` (white).
- Cell margins: table-level `left/right = 10` dxa.
- Grid (DXA): `300 | 3850 | 624 | 154 | 4098`
  - col1 = transliteration verse number
  - col2 = transliteration text
  - col3 = empty spacer
  - col4 = English verse number
  - col5 = English text
- Per-row paragraph: `<w:spacing w:after="180" w:line="276" w:lineRule="auto"/>`.
- col2 has `<w:tcMar><w:right w:w="144"/></w:tcMar>`; col5 has `left=144`.

Run formatting (all Arial, `w:ascii/hAnsi/eastAsia/cs="Arial"`):

| element            | size (half-pt) | pt | color    | style        |
|--------------------|----------------|----|----------|--------------|
| translit verse #   | 24             | 12 | `374151` | bold         |
| transliteration    | 28             | 14 | `374151` | italic       |
| English verse #    | 24             | 12 | `000000` | bold         |
| English text       | 28             | 14 | `000000` | regular      |

Verse numbers carry NO trailing period ("26", never "26.").

## Arabic page — one centered bidi paragraph

Paragraph properties:
```xml
<w:pPr>
  <w:bidi/>
  <w:spacing w:before="431" w:after="431" w:line="276" w:lineRule="auto"/>
  <w:jc w:val="center"/>
</w:pPr>
```
The first run of this paragraph is the page break:
```xml
<w:r><w:br w:type="page"/></w:r>
```

### The CRITICAL font-slot detail

Every Arabic run uses Scheherazade New in ALL FOUR font slots:
```xml
<w:rFonts w:ascii="Scheherazade New" w:hAnsi="Scheherazade New"
          w:cs="Scheherazade New" w:eastAsia="Scheherazade New"/>
```
`w:cs` (complex-script) is the load-bearing one. For an `rtl` run, LibreOffice
selects the glyph font from the `cs` slot, NOT `eastAsia`. If `cs` is missing or
set to Arial, the Arabic — including the U+06DD ornament — falls back to a
substitute font and the ornament renders as an empty box (tofu), even when
Scheherazade New is installed. This was the silent failure mode. Do not remove
`cs`. `render.sh` verifies the font actually embedded via `pdffonts`.

Arabic run common rPr: `<w:b/><w:bCs/>`, `<w:sz w:val="52"/><w:szCs w:val="52"/>`
(= 26pt), `<w:rtl/>`, plus the color below.

### Verse layout inside the paragraph

Verses run continuously (not one per line). For each verse, in order:
1. The verse's Arabic text, emitted as dark runs (`color 1F2937`). Inline waqf
   (pause) marks from the source — ۖ ۗ ۚ ۜ ۞ — are kept verbatim inside these runs.
2. Sacred words found in the verse are split out into their own GREEN runs
   (`color 008000`). See `references/sacred-words.md`.
3. The end-of-ayah ornament `۝` (U+06DD) as a GREEN run (`008000`).
4. The verse number as Arabic-Indic digits (٠١٢…) in a DARK run (`1F2937`),
   with a trailing space except on the last verse of the page.

The ayah ornament + number is rendered as ONE Scheherazade New run: the U+06DD
ornament char immediately followed by the Arabic-Indic verse number, with NO
space between them, colored green (008000). In Microsoft Word, Scheherazade New's
U+06DD ENCLOSES the following digits inside the ornament (the proper mushaf look:
number centred in the ornament). This is confirmed against an approved Al-Kahf
output in Word.

Critical encoding rules (any of these broken => number drifts OUTSIDE the ornament):
- ornament char and digits in the SAME run
- NO space between the ornament and the digits
- one font throughout (Scheherazade New); do not switch the ornament to another font

ENGINE WARNING: LibreOffice (the render/QA engine) is INCONSISTENT about this
enclosure — the verification PDF may show the number beside the ornament, or the
ornament as an empty hexagon. That is a LibreOffice artifact, NOT a defect. Judge
the enclosure in WORD. (An earlier attempt to "fix" the LibreOffice appearance by
switching to the Amiri font was a mistake and was reverted — see word-deltas.md.)

IMPORTANT — source ornament stripping: some CSV sources already end each verse's
Arabic with ۝ (and sometimes a numeral). `build_docx.py` runs
`clean_source_arabic()` to strip any U+06DD and adjacent/trailing Arabic-Indic
numerals from the source, while PRESERVING inline waqf marks (ۖ ۗ ۚ ۜ ۞). Without
this, the output gets a DOUBLE ornament (one from the source text, one added by
the build) — a real bug seen on a Mulk CSV.

## Colors (hex, no #)

| token            | color    | used for                          |
|------------------|----------|-----------------------------------|
| dark             | `1F2937` | Arabic body text, Arabic numerals |
| green            | `008000` | ۝ ornament AND sacred words       |
| translit grey    | `374151` | transliteration + its verse #     |
| english black    | `000000` | English + its verse #             |

## Fonts that must exist in the render environment

- **Scheherazade New** (Regular + Bold) — Arabic. Installed by `setup_fonts.sh`.
- Arial — English/translit. LibreOffice maps to Liberation Sans; fine.
