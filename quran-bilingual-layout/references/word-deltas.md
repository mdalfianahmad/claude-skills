# Word vs LibreOffice deltas

The loop calibrates against LibreOffice (the available render engine). The
deliverable opens in Microsoft Word, which wraps Arabic slightly differently.
This file records confirmed, repeatable differences so the loop's defaults can
compensate. It starts empty on purpose.

When the user reports a difference between what the verification PDF showed and
what Word displayed, add a dated entry: what differed, on which spread/surah,
and what adjustment fixed it. Over time these entries tune the fill band and
grouping defaults in `references/layout-loop.md`.

## Confirmed deltas

### 2026-06 — ayah-number enclosure in the U+06DD ornament
- Observed: with Scheherazade New, when the ornament char U+06DD is immediately
  followed by the verse-number digits in the SAME run with NO space, WORD renders
  the number ENCLOSED inside the ornament (correct mushaf look). LibreOffice (our
  QA render engine) is inconsistent — it often shows the number BESIDE the
  ornament in the verification PDF, and sometimes as an empty hexagon.
- Context: confirmed against an approved Al-Kahf output opened in Word (number
  108 sat inside the ornament). The verification PDF from LibreOffice for the same
  encoding did not always enclose it.
- Fix applied: keep Scheherazade New for the ornament; encode ornament+digits as a
  single run, no space (`_ornament_run` in build_docx.py). Do NOT switch fonts or
  split into two runs. An earlier attempt to "fix" the LibreOffice appearance by
  switching the ornament to Amiri was a mistake — it chased a LibreOffice artifact
  that does not exist in Word, the real target.
- Generalized into loop defaults? Yes — the ornament encoding is fixed in the
  build. IMPORTANT consequence for QA: the LibreOffice verification PDF may show
  the ayah number beside the ornament; this is an ENGINE artifact, not a defect.
  Judge ornament-number enclosure in WORD, not in the verification PDF.

## Format for new entries

```
### YYYY-MM-DD — <short description>
- Observed: <what Word did vs the LibreOffice PDF>
- Context: <surah, spread/verse range, fill % measured>
- Fix applied: <regroup / band change / manual delete in Word>
- Generalized into loop defaults? <yes/no — what changed>
```
