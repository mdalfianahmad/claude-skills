# Claude Skills

A backup of the [Claude Skills](https://docs.claude.com) from my account. Each `.skill` file is a self-contained zip archive (containing a `SKILL.md` plus any scripts/references) that can be re-installed into Claude Desktop / Cowork.

## Installing a skill

Drag the `.skill` file into a Claude Desktop / Cowork chat, or add it via **Settings → Capabilities → Skills**.

## Skills

| Skill | Description |
|---|---|
| [`canvas-design`](skills/canvas-design.skill) | Creates original visual art (posters, static designs) as `.png`/`.pdf` using design philosophy principles. |
| [`consolidate-memory`](skills/consolidate-memory.skill) | Reflective pass over memory files — merges duplicates, fixes stale facts, prunes the index. |
| [`docx`](skills/docx.skill) | Creates, reads, edits, and manipulates Word documents — headings, TOCs, tables, tracked changes, images. |
| [`double-check`](skills/double-check.skill) | Decides whether to ask 1–3 clarifying questions before acting on an ambiguous or underspecified instruction. |
| [`frontend-ui-engineering`](skills/frontend-ui-engineering.skill) | Builds production-quality, non-generic-looking UI components, pages, and layouts. |
| [`higgsfield`](skills/higgsfield.skill) | Writes and refines Higgsfield AI video/image prompts — model choice, camera controls, motion presets, Soul ID. |
| [`pdf`](skills/pdf.skill) | PDF toolkit — extract text/tables, merge/split, rotate, watermark, fill forms, OCR. |
| [`pptx`](skills/pptx.skill) | Creates, edits, and extracts content from PowerPoint decks — layouts, speaker notes, templates. |
| [`prd-writer`](skills/prd-writer.skill) | Drafts structured Product Requirements Documents — goals, personas, requirements, success metrics. |
| [`quran-bilingual-layout`](skills/quran-bilingual-layout.skill) | Typesets a print-ready bilingual (Arabic/English/transliteration) Quran/surah layout from a spreadsheet of verses. |
| [`ranked-research`](skills/ranked-research.skill) | Multi-source web research with claims grouped and ranked by source credibility. |
| [`roast`](skills/roast.skill) | Anti-sycophancy decision council — stress-tests an idea through opposing personas plus a green/reshape/kill verdict. |
| [`schedule`](skills/schedule.skill) | Creates or updates recurring/one-off scheduled tasks. |
| [`setup-cowork`](skills/setup-cowork.skill) | Guided Cowork setup — installs role-matched plugins, connects tools, tries a skill. |
| [`skill-creator`](skills/skill-creator.skill) | Creates, edits, and benchmarks other Claude skills. |
| [`ui-reference-gatherer`](skills/ui-reference-gatherer.skill) | Gathers UI design reference screenshots / moodboards scoped by platform. |
| [`xlsx`](skills/xlsx.skill) | Excel spreadsheet creation, editing, and analysis — formulas, formatting, charts. |

## Not included

Two plugin-bundled skill sets aren't in this export: `desktop-commander:*` and `cowork-plugin-management:*`. They live inside installed plugins rather than the standalone skills store, so only their `SKILL.md` is readable individually — not the full bundle (scripts/references) — which would make an export incomplete. Export those via their plugin instead.
