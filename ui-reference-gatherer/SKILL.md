---
name: ui-reference-gatherer
description: Gathers UI design reference screenshots for a project, scoped by platform (web, mobile web, or mobile app). Use whenever the user wants design inspiration, UI references, a moodboard, look-and-feel examples, competitor UI scans, or design direction for an app/site/feature/screen they are building — even if they never say "reference" or "inspiration." Trigger on phrases like "find UI ideas for," "gather designs for," "show me dashboard examples," "what could this screen look like," "I need inspiration for a [type] app/site," or any request to collect existing interface examples before designing. Always delivers an inline image gallery; a downloadable PDF of screenshots is possible ONLY when the sandbox has open network egress (see Environment reality).
---

# UI Reference Gatherer

Collects 15-20 UI design references for a project. Always returns an inline gallery. Returns a screenshot PDF only if the network allows image downloads; otherwise falls back.

## Definition

- **Name:** ui-reference-gatherer
- **Scope:** Surfaces existing UI screenshots scoped by platform and aesthetic, and presents them. Primary output is an inline `image_search` gallery. Secondary output is a PDF — a real screenshot contact sheet when network egress is open, or a links-and-patterns brief when it is not. Does NOT: scrape Pinterest/Dribbble/template sites directly, attach reliable source links to individual images, design original UI, generate mockups, or critique the user's design.
- **Context:** Fires when the user wants to collect interface examples before or during a design phase. Triggered by requests for UI inspiration, references, moodboards, "examples of [screen type]," competitor scans, or "what could this look like." Use even when "reference"/"inspiration" is absent — gathering existing interface examples is the signal.

## When to use

- User is starting a design and wants to see how others did it.
- User asks for examples of a specific screen (dashboard, onboarding, checkout, settings).
- User pastes a project brief and wants visual direction.
- User says "show me," "find me," or "gather" + any UI/screen/app/site term.

## Inputs needed

Collect before searching. If project type or platform is missing, ASK — do not guess.

- **Project** — what is being built (e.g. "budgeting app for students," "NGO donation site").
- **Platform** — `web` / `mobile web` / `mobile app`. Required. Drives query tokens, layout, and aspect ratio.
- **Key screens/features** — optional; improves precision (e.g. "onboarding, donation, impact stats").
- **Aesthetic** — ALWAYS ask if not given. Offer steers: minimal, dark mode, glassmorphic, brutalist, neumorphic, playful/illustrative, corporate/clean, editorial.
- **Count** — default 15-20.

If only a vague project + platform is given, infer 3-5 likely screens, state them in one line, and proceed unless corrected.

## Steps

1. Confirm project + platform. Ask for whichever is missing. Never assume platform.
2. Ask for aesthetic if not provided.
3. If screens weren't given, infer and state them ("Searching for: onboarding, dashboard, settings — adjust?"). Proceed unless corrected.
4. Build queries with the formula below.
5. Run `image_search` (max 4/call) until 15-20 distinct references are gathered. Present inline, grouped by screen/theme with a one-line label per group. THIS ALWAYS WORKS and is the core deliverable.
6. Decide on the PDF: run the network preflight (PDF output section). Branch to contact-sheet mode or brief mode based on the result. Tell the user which mode you're in and why.
7. Present the file.

## Query construction

Formula: `[screen/feature] + [platform token] + [aesthetic] + UI`

Lessons from use:
- Do NOT lead with source tokens like `dribbble` or `behance` — they frequently return ZERO results. Treat source names as rare optional spice at the end, never the spine of the query.
- For `web` platform, append `website` or `web` to every query. The image index otherwise injects mobile-app UI kits into web searches.
- If a query returns nothing, broaden by dropping tokens in this order: source token, then aesthetic token.

Platform tokens: web -> `website` / `dashboard` / `landing page`; mobile web -> `responsive mobile website`; mobile app -> `mobile app` / `iOS app screen` / `android app screen`.

Examples (web): `nonprofit donation page website UI`, `charity homepage clean website design`, `analytics dashboard web app dark mode`.

Run varied angles so the set isn't 15 versions of one layout.

## PDF output

The PDF cannot be assembled from the inline gallery. `image_search` displays images to the user but returns NO bytes or URLs to Claude — there is nothing to collate. PDF images must be sourced and downloaded separately, which requires open network egress.

### Preflight (always run before attempting an image PDF)

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://example.com
```

`200` -> network open, use contact-sheet mode. `403` with body `Host not in allowlist` (or any non-200) -> network locked, use brief mode. Do not retry mid-session; allowlist changes apply only at session start, so a locked result means locked for this whole chat.

### Mode A — screenshot contact sheet (network open)

1. `web_search` for example sites and roundup articles for the project domain.
2. `web_fetch` each promising page as markdown; extract image URLs (`![...](url)`, `og:image`, etc.). NOTE: `web_fetch` cannot fetch image URLs directly — it errors "Image content is not supported." Use it only to read pages and harvest URLs.
3. Download each image with `bash` curl/wget to disk.
4. Convert as needed (webp/avif -> png via Pillow; reportlab embeds png/jpg cleanly).
5. Build a grid with reportlab `Image` flowables — 3 cols for landscape/web, 4 for portrait/mobile. Caption each cell with its theme/source.
6. Degrade gracefully: skip any image that 403s or fails to decode; continue. Report included-vs-dropped count at the end. Expect a drop rate — some hosts block hotlinking even with open egress.

### Mode B — links-and-patterns brief (network locked)

Build a text PDF with reportlab: title page (project, platform, aesthetic, date), recurring design patterns for the domain, a table of clickable links to live exemplar sites and roundups, and template/starter sources. No embedded images. This is the honest fallback when screenshots can't be downloaded.

## Environment reality (read before promising a PDF)

Tested facts about this sandbox type:
- `image_search` -> shows images inline to the user; returns only result titles to Claude. No URLs, no bytes. Cannot feed a PDF.
- `web_fetch` on an image URL -> rejected: "Image content is not supported." Pages only.
- `bash` network -> governed by an allowlist. Locked default permits package registries (pypi, npm, github) but returns `403 Host not in allowlist` for image CDNs and general web.
- Network allowlist changes take effect at SESSION START, not mid-conversation.

Consequence: in a locked sandbox the skill delivers the inline gallery and, at most, a Mode B brief. The screenshot PDF (Mode A) needs a session that booted with open egress. State this to the user rather than promising a contact sheet you can't build.

## Edge cases

- **Platform not stated** -> ask. Changes query tokens and PDF layout.
- **Project too vague to infer screens** ("an app") -> ask what it does before searching.
- **Query returns zero** -> drop source token, then aesthetic token.
- **All results identical** -> switch the screen term (e.g. "transaction list" -> "activity feed").
- **User insists on a screenshot PDF but network is locked** -> explain the session-start constraint; offer Mode B now or a fresh open-network session for Mode A.
- **User wants per-image source links** -> out of scope; image-to-source matching is unreliable.

## Notes

- The inline gallery is the dependable product. Treat the screenshot PDF as conditional, not guaranteed.
- No fabricated source links. Don't invent URLs.
- Search index != the actual design sites. Coverage of Dribbble/Pinterest depends on indexing; some design-host images are filtered out.
- This skill collects references only. It does not produce mockups or design work.
