---
name: prd-writer
description: Use this skill whenever the user wants to create, write, draft, or generate a Product Requirements Document (PRD) for a software project, feature, app, tool, or system. Trigger on phrases like "PRD", "product requirements document", "product spec", "feature spec", "requirements doc", "write requirements for...", or any request to formally document business goals, user personas, functional requirements, user flows, success metrics, or user stories for something being built. Also trigger when the user describes a product/feature idea and asks to "document it", "spec it out", "formalize the requirements", or "write it up for the dev team". Use even when the user does not say the literal phrase "PRD" — if the intent is to produce a structured product requirements document, this skill applies.
---

# PRD Writer

Generate a comprehensive Product Requirements Document (PRD) in Markdown for a software project or feature.

## Gate: previous PRD status

Before drafting a new PRD, ask the user: what is the 48-hour test for your previous PRD, or has it been explicitly killed? Do not draft until answered.

## Output contract

- Output a single `prd.md` file in valid Markdown.
- If the user has not specified a save location, suggest one and ask for confirmation before writing the file.
- Do not produce tasks, action items, or implementation code as part of this skill — only the PRD.
- Do not add a conclusion, footer, sign-off, or horizontal rules / dividers. The user stories section is the last section.
- Use sentence case for all headings except the document title, which uses title case.
- When referring to the project inside the doc, use conversational terms like "the project" or "this tool" rather than a formal product name.

## Before writing — pressure test the concept

For products with real technical, business, or UX risk, do a quick architectural sanity check before drafting the PRD. Skip for trivial requests (toy demos, internal scripts, well-understood patterns). For everything else:

1. **Multi-perspective review.** Walk through the concept from several angles: an **engineer** (what breaks, what's actually hard, what the chosen mechanism really does at the OS or framework level), an **executive** (build vs buy — what already exists in this space, what would justify rolling your own), a **UX researcher** (where users break the intended flow, where friction earns its keep vs annoys), and where relevant a **security or threat-model lens** (what is being defended against, who is the adversary, what is explicitly out of scope). When stakes warrant it, surface this review to the user as a separate response before writing the PRD.

2. **Pressure test the central technical mechanism.** Identify what specifically blocks/syncs/computes/enforces, then check it against the user's actual targets — not the trivial demo case. Common traps:
   - Mechanisms that work for `example.com` but fail on CDN-hosted, Anycast, or rotating-IP targets.
   - Mechanisms that have hidden entitlement, approval, or distribution requirements (Network Extensions, Family Controls, Screen Time, Bluetooth backgrounding, Mac App Store sandboxing).
   - Mechanisms that have deprecated successors and may break on the next OS version.
   - Mechanisms that conflate two different communication boundaries (e.g., "XPC between A, B, and C" can hide that A↔B is free-form XPC while B↔C is an OS-mediated typed configuration write).

   Verify the mechanism is appropriate before locking it into the PRD. A wrong mechanism wastes more time than the review takes.

3. **Calibrate claims to capability.** If the product makes guarantees it cannot fully deliver, name the gap now. "Non-bypassable against an admin user," "real-time on a polling backend," "private from the OS itself" — overclaims that survive into the PRD set up disappointment and rework. The honest framing belongs in the opening paragraph and in the relevant user stories.

## Before writing — gather context

Read the user's request and extract: what is being built, who it's for, what problem it solves, and any constraints already mentioned. If critical context is missing (target users, core use case, platform, or scope), ask up to 3 focused questions before writing. Do not interrogate — fill reasonable gaps with stated assumptions instead.

## Document structure

Use exactly these top-level sections, in this order:

1. **Product overview** — include a document title/version line and a product summary paragraph. If the product is self-binding, voluntary, or otherwise makes guarantees it cannot fully enforce, state that calibration up front in plain language.

2. **Goals** — subsections: business goals, user goals, non-goals. Non-goals should include things the product explicitly will not try to defend against, solve, or compete with.

3. **User personas** — subsections: key user types, basic persona details, role-based access. For single-user products with an internal privilege boundary (e.g., main app + privileged daemon + system extension), document the privilege boundary here even though there is only one human role.

4. **Functional requirements** — list each requirement with a priority label (e.g., P0 / P1 / P2 or High / Medium / Low). Be consistent within one document.

5. **User experience** — subsections: entry points, core experience, advanced features, UI/UX highlights.

6. **Narrative** — exactly one paragraph written from a representative user's perspective.

7. **Success metrics** — subsections: user-centric metrics, business metrics, technical metrics.

8. **Technical considerations** — subsections: integration points, data storage / privacy, scalability / performance, potential challenges. When relevant, also add:
   - **Rejected alternatives.** For each major architectural choice, list one or two alternatives that were considered and rejected, with the specific reason. This stops reviewers from re-proposing them and forces deliberate thinking.
   - **Known limitations / known bypass routes.** For products that make claims they cannot fully deliver, list the gaps explicitly: what bypasses the protection, what scenarios fall outside the design, what's deferred to a later version. Owning gaps is better than being caught.

9. **Milestones & sequencing** — subsections: project estimate, team size, suggested phases. **Separate development time from external dependencies.** If the product depends on third-party approval (Apple entitlements, app-store review, partner API access, government licensing), call that out as a distinct gating item with its own (often unbounded) timeline. "Ship date" is not "feature-complete date" when an external party controls part of the path.

10. **User stories** — the comprehensive list (see rules below). This is the final section.

Add subheadings where useful within each section. Keep language clear, specific, and consistent. Provide concrete numbers and metrics wherever the request allows it (don't fabricate hard data — use ranges or "TBD" if unknown).

## User stories rules

The user stories section must be exhaustive enough that a dev team could build the entire application from it alone.

For each story:

- Assign a unique ID with prefix `US-` and zero-padded number (e.g., `US-001`, `US-002`, ...). IDs are stable identifiers — do not reuse or renumber mid-document.
- Format each story as:
  - **ID**
  - **Title**
  - **Description** — written in the form: *As a [persona], I want to [action], so that [benefit].*
  - **Acceptance criteria** — a bulleted list of clear, testable conditions.

Coverage requirements:

- Include primary happy-path stories, alternative paths, and edge cases.
- If the product involves user identification, accounts, restricted areas, or any access control, include at least one story specifically for secure access / authentication / authorization.
- Every story must be testable. Every acceptance criterion must be specific enough that a tester or developer knows when it's satisfied.

Cross-story consistency:

- Acceptance criteria across stories must not contradict each other. If US-A says "X cannot happen" and US-B describes a path where X happens, one is wrong.
- If the product makes a guarantee, every story that touches that guarantee must respect it or explicitly note the scope where it doesn't apply.
- If a guarantee cannot hold in some scenario (reboot, sleep, crash, external API failure, network partition), the relevant stories must acknowledge the limit rather than paper over it.

## Pre-delivery checklist

Before returning the PRD, silently verify:

- [ ] Every user story is testable.
- [ ] Acceptance criteria are specific, not vague.
- [ ] Stories collectively cover enough surface area to build a fully functional version.
- [ ] Authentication / authorization is covered if the product needs it.
- [ ] Cross-story consistency: no two stories contradict each other on the same scenario.
- [ ] Product rhetoric is calibrated to actual capability — no overclaiming in the overview, narrative, or stories.
- [ ] The central technical mechanism is appropriate for the actual use case, not the trivial demo case.
- [ ] Rejected alternatives are documented if the architecture has meaningful trade-offs.
- [ ] Known limitations or bypass routes are documented if relevant.
- [ ] External dependencies (approvals, entitlements, third-party access) are separated from the dev timeline.
- [ ] All 10 sections are present and in order.
- [ ] No horizontal rules, no footer, no conclusion.
- [ ] Headings follow the sentence-case rule (title is the only exception).
- [ ] Grammar and proper-noun casing are clean.

Fix anything that fails the checklist before presenting the file.

## Common failure patterns to avoid

Patterns that have produced bad PRDs in practice. Check the draft against these before delivery:

- **Conflating different inter-component communication mechanisms.** A single phrase like "XPC between components" can hide that one boundary is free-form RPC and another is a typed configuration write mediated by the OS. Name each mechanism specifically and verify it matches the framework's actual model.
- **Auto-recovery that defeats the core guarantee.** If a product is "hard mode" but auto-clears on helper failure, the trivial bypass is to wedge the helper. Manual, documented recovery preserves the guarantee.
- **Recovery instructions that depend on the broken thing.** A README hosted online is useless when the product is blocking the README's host. Ship recovery docs locally, surface them at install, and write them to logs.
- **Timer or expiry math against the wrong clock.** Wall-clock is user-controllable. Monotonic clocks reset at reboot. Pick deliberately and document what each protects against.
- **Privilege boundaries that don't match the data paths.** A root daemon writing to `~/Library/...` is wrong. Split system-owned state from user-owned preferences by path, or have the unprivileged side own all persistence and pass config to the privileged side over a typed channel.
- **Optimistic timelines that ignore external gates.** "Six weeks to ship" when entitlement approval is a four-week wait is misleading. Separate dev time from gating items, and surface the gating item early so it can run in parallel.
- **Recommending a mechanism without checking its constraints.** Many capable mechanisms have hidden gates: Apple entitlements, App Store sandbox rules, OS-version requirements, deprecated successors. Check before recommending.
- **Single-pass PRDs for non-trivial products.** A first draft is rarely correct on the architecture. Expect at least one review round; bake honesty about uncertainty into the v0.1 so the review can be productive rather than corrective.

## Formatting reminders

- Markdown only. No HTML, no front-matter inside the `prd.md` itself.
- Use consistent numbering and indentation for nested lists.
- Do not insert "---" dividers between sections.
- Code fences only if the PRD genuinely needs to show a payload, schema, or example string.
