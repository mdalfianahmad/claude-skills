# The layout loop — grouping, fill, and blank pages

This is the judgment part of the skill, the thing that can't be hardcoded. It
decides how many verses go on each spread, and it self-corrects by rendering and
measuring. Read this before running the loop.

## The atomic rule

The **Arabic page is the atomic unit**: one spread's verses occupy exactly one
Arabic page. Never split a spread's Arabic across two pages. English flows
freely and MAY spill onto a second page — a short English tail (even a single
word on its own page) is correct and expected, not a defect. Never split a
spread in two just to keep English on one page; that manufactures half-empty
pages, which was the original mistake this whole approach exists to avoid.

## Grouping is driven by Arabic fill, not English

Group verses generously, aiming to fill the **Arabic** page. Verse counts per
spread are irregular by nature — long verses mean fewer per page, short verses
more. In Al-Kahf the reference ranges from 2 to 7 verses per spread. Do not aim
for a fixed verse count.

## Fill is informational — defects are blanks and splits

There is NO tight fill band. Measured against the approved reference output, the
Arabic pages legitimately range from ~59% to ~94% full (median ~77%), purely
because verse lengths vary. A 60%-full page with two long verses is just as
correct as an 85%-full page with five short ones. Do not chase a target
percentage and do not "fix" a page for being under some floor — that just churns
the layout.

`measure_fill.py` reports each page's fill % as INFORMATION, plus the two things
that are actual defects:

- **BLANK page** — a page with no content. Hard defect. Caused by the Arabic
  page of the PRECEDING spread being so full it pushes the following page break
  onto a blank. Fix by regrouping that spread smaller.
- **SPLIT ARABIC** — two Arabic pages in a row, meaning one spread's Arabic
  overflowed onto a second page. Hard defect (violates the atomic rule). Fix by
  regrouping that spread smaller.
- **very full (>90%)** — reported as a RISK note, not a failure. Such a page is
  fine as long as no blank or split actually appeared next to it.

You cannot predict any of this from character or line counts — Arabic shaping in
the real font is the only truth. Build, render, and read the measure summary.
The tool prints `CLEAN` only when there are no blanks and no splits.

Why a little slack still helps: Word wraps Arabic slightly differently from
LibreOffice (the engine we calibrate against). A page rendered at ~94% in
LibreOffice is the kind most likely to behave differently in Word, so when a
spread is right at the edge, prefer moving one verse out.

## Why blank pages happen — and the correct fix

When an Arabic page renders near the printable limit, the page break that
follows it spills onto a blank page. The blank is a **symptom of too many verses
on that Arabic page**, not a break-logic bug. Chasing it by moving page breaks
around just relocates the blank.

The correct fix is to **regroup the offending spread smaller** — move its last
verse (or last couple) into the next spread — then rebuild and re-measure.
Proven on Al-Kahf: the 7-verse spread `[8,14]` rendered its Arabic at ~94% and
produced a blank; regrouping to `[8,13]` (with `14` rolling into the next
spread) removed the blank.

The build already places the page break as the first run *inside* the Arabic
paragraph (not as a standalone empty paragraph) — see `references/encoding-spec.md`.
That structure prevents blanks caused by a full *English* page. The remaining
blank cause is a full *Arabic* page, which only regrouping cures.

## The loop

1. Pick an initial grouping (generous; ~5–7 short verses or ~3–4 long ones).
2. `build_docx.py … --spreads '<JSON ranges>'`
3. `render.sh` → PDF + page images (also verifies the font embedded).
4. `measure_fill.py PDF` → read the summary.
5. For each flagged defect:
   - **BLANK page** → the spread whose Arabic page precedes the blank has too
     many verses; move its last verse into the next spread.
   - **SPLIT ARABIC** (two Arabic pages in a row) → that spread's Arabic
     overflowed; move its last verse into the next spread.
   - Moving a verse out cascades it into the next spread, which may then need its
     own adjustment — keep iterating. Long verses (e.g. Al-Kahf v17, v19) may
     force a spread down to 2 verses; that is correct, not a problem.
6. Rebuild, re-render, re-measure. Repeat until the summary says CLEAN
   (no blanks, no over-full Arabic).
7. Show the human the PDF and the list of green sacred words for confirmation.

Keep changes minimal between iterations — move one verse at a time near the
boundary. Don't regenerate already-good spreads from scratch; that drifts the
layout. Preserve spreads the human has already approved verbatim.

## The Word hand-off (operating model)

The deliverable is the **.docx**. We calibrate the loop against LibreOffice
because that is the engine available for rendering; the human opens the result
in Microsoft Word, which wraps Arabic slightly differently.

- Always deliver the LibreOffice-rendered **verification PDF alongside** the
  docx, so the human can see exactly what the loop checked.
- If a blank still appears in Word that wasn't in the LibreOffice render, the
  human's quick fix is to **delete the empty paragraph(s) at the top of the
  blank page in Word**, letting the previous section pull up to fill it. This is
  expected last-mile cleanup, not a failure of the skill.
- When the human reports a consistent Word-vs-LibreOffice difference (e.g. "Word
  always needs one less verse per Arabic page"), record it in
  `references/word-deltas.md` and adjust the loop's defaults. The skill improves
  over time this way.
