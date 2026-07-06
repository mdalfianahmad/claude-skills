# Sacred-word coloring — Allah and Rabb

The Arabic page colors two kinds of words green (`008000`): the name **Allah**
and the word **Rabb** ("Lord") in all its forms. This is the user's rule for
this project. Nothing else is colored green except the ۝ ornament.

`build_docx.py` does this with `is_sacred(token)`. This file explains the
matching so it can be checked and extended.

## The matcher

Tokens are split on spaces. A token is sacred if it matches either pattern.
`HARAKAT` = any run of tashkīl marks (`\u064b`–`\u0652`, plus superscript alef
`\u0670`); `SHADDA` = `\u0651`.

**Allah** — match the `llāh` core (lām-lām-shadda-hā), which covers every
attached form (الله, لله, بالله, والله, لله…):
```
ل  HARAKAT  ل  SHADDA  HARAKAT  ه
```

**Rabb** — match rā then bā carrying SHADDA. The shadda (doubling) is what makes
it "Rabb" rather than an unrelated ر-ب sequence:
```
ر  HARAKAT  ب  SHADDA
```

## Why shadda-anchored — the false positive it prevents

A naïve "contains ر then ب" match colors `وَرَبَطنا` ("We made firm", verse 14)
green, which is wrong — that is a verb, not the divine name. The bā in
`وَرَبَطنا` has no shadda; the bā in `رَبَّنا` ("our Lord") does. Anchoring on
the shadda rejects the verb and keeps the Lord. Verified across all 110 verses
of Al-Kahf: every match is genuine, no false positives.

The Allah pattern likewise needs the shadda on the second lām, because the
lām-lām sequence with shadda is specific to the name; matching bare لل would
catch unrelated words.

## What it matched in Al-Kahf (reference)

- Allah (5 forms): اللَّهَ / اللَّهُ / اللَّهِ / بِاللَّهِ / لِلَّهِ
- Rabb (17 forms): رَبّي, رَبَّنا, رَبَّكَ, رَبِّكَ, رَبُّكَ, رَبُّكُم, رَبُّهُم,
  رَبُّهُما, بِرَبِّهِم, بِرَبّي, وَرَبُّكَ, رَبُّ, رَبِّهِ, رَبِّهِم, رَبِّكُم,
  رَبَّهُم, رَبُّنا

## Important limits — confirm on the render every time

This is sacred text. The matcher is good but not infallible across all surahs:

- Other surahs may contain a ر-ب-shadda word that is NOT "Lord" (e.g. forms of
  رَبَّى "to raise/nurture", or أَرْبَاب "lords/masters" plural). These would be
  colored green incorrectly.
- Conversely, an unusual orthography of the source could hide a shadda and miss
  a real Rabb.

Because of this, `build_docx.py` PRINTS every verse where it colored a word, and
the SKILL requires the human to confirm the green words on the rendered PDF. If
a word is wrongly colored (or missed), the fix is to adjust the source token or
extend the matcher — never to silently ship unconfirmed coloring on Quranic text.

## Extending

If the user later wants more sacred terms colored, add patterns the same way:
anchor on whatever feature unambiguously identifies the word (a shadda, a
specific letter sequence), keep them token-scoped, and re-verify against a full
surah for false positives before trusting them.
