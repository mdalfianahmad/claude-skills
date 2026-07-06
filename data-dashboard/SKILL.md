---
name: data-dashboard
description: Turn any tabular dataset (CSV, Excel, TSV, exported logs) into a cleaned dataset plus a self-contained interactive HTML dashboard. Trigger whenever the user uploads or references a data file and wants analysis, visualisation, charts, a dashboard, a breakdown, stats, trends, or a summary of the data — even if they never say "dashboard". Phrases like "analyse this", "visualise this", "what does this data show", "build me charts", "clean this up", "how many X per Y" on a tabular file all count. Domain-agnostic — works for event logs, financial exports, scores, attendance, call logs, sales, or any other tabular topic. Do NOT trigger for single-value lookups inside a file, or when the deliverable is a spreadsheet (use xlsx skill) or a Word report (use docx skill).
---

# Data Dashboard

Convert a raw tabular dataset into (1) a cleaned dataset and (2) a single self-contained HTML dashboard. Process rules below are non-negotiable regardless of dataset topic.

## Stage 1 — Inspect before touching

Never clean or chart data you haven't inspected. First action on any dataset:

1. Load and report: row count, column names and types, date/time range if present, unique-key candidates.
2. Report anomalies: duplicate IDs, null-heavy columns, rows outside the expected date window, obvious test/placeholder values (e.g. TEST*, 999*, rows dated before the event/period), mixed formats within one column.
3. Ask the user which ID column (if any) is the unique key, if not obvious.

Present findings as a short summary. Do not proceed to cleaning until anomalies are surfaced.

## Stage 2 — Cleaning gates

**Never silently drop or preserve suspect rows.** For each class of suspect data (test rows, out-of-window rows, duplicates), state what was found and the proposed treatment, then get confirmation before applying. Lesson learned: preserving a test row as a "separate event" instead of dropping it was wrong; so is dropping without asking.

Deduplication defaults:
- One output row per unique ID after merging.
- For repeated rows of the same ID over time (retries, re-calls, re-submissions): use cluster-aware merging — rows within a configurable time-gap threshold (default 10 minutes) are one event; beyond it, treat as reuse and merge to a single row spanning first-start to last-end unless the user says otherwise.
- Report the final unique count and ask the user to confirm it matches their expectation before building charts.

Timestamps:
- Always parse with explicit UTC anchoring, then convert to the user's timezone (default `Asia/Singapore`): `pd.to_datetime(col, utc=True).dt.tz_convert(tz)`.
- Never naive-parse timestamps into hour buckets. Naive parsing has produced wrong hourly groupings before.

Deliverables from this stage: a cleaned CSV saved alongside the dashboard. The user always gets the cleaned data, not just charts.

## Stage 3 — Dashboard build

Output: **one self-contained HTML file.**

Hard rules:
- **Zero external dependencies.** No CDN scripts, no external fonts, no fetch calls. Inline CSS and vanilla JS only. CDN-dependent dashboards have failed to render in this environment before.
- Charts as inline SVG built by reusable JS functions (e.g. one `lineChart()`, one `barChart()` reused across cards) — never per-chart copy-pasted rendering code.
- Line charts are the default for time series. Bar charts for categorical comparison. No pie charts unless asked.
- Each chart in its own card. Cards should be removable/rearrangeable in code without breaking others.
- Headline stat row at top: totals, medians/means, peak values — computed from the cleaned data, stated with units.
- A clickable/expandable breakdown table where per-item detail exists (categories, IDs, merchants, students — whatever the domain's row unit is).
- Numbers in the dashboard must reconcile with the cleaned CSV. Verify totals match before delivery.

Build the data-processing in Python (pandas via bash heredoc for multi-step logic), then inject computed aggregates into the HTML as inline JSON. The HTML never processes raw data itself.

## Stage 4 — Revisions

- Patch the existing HTML with targeted `str_replace` edits or scoped `re.sub(..., count=1, flags=re.S)` on specific JS/HTML blocks. **Never rewrite the whole file** to change one chart — full rewrites have corrupted working chart logic before.
- When adding a chart type that exists elsewhere in the file, reuse the existing chart function.
- When the user removes a chart, delete the card and its data block; leave shared functions intact.
- Re-verify headline stats after any data-affecting change.

## Verification checklist before delivery

- [ ] Cleaned CSV row count matches confirmed expectation
- [ ] No test/out-of-window rows remain (per confirmed treatment)
- [ ] Timezone conversion applied; spot-check one known timestamp
- [ ] HTML opens with no console errors and no network requests
- [ ] Headline stats reconcile with cleaned CSV
- [ ] Both files delivered: dashboard HTML + cleaned CSV
