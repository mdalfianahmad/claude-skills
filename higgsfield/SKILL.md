---
name: higgsfield
description: >
  Use this skill whenever the user asks anything about Higgsfield AI — writing or
  refining video/image prompts, choosing a model (Kling, Sora, Veo, Seedance, Soul,
  Nano Banana, Flux, etc.), camera controls, motion presets, Soul ID consistency,
  Cinema Studio, Vibe Motion, failed generations, credit optimization, or any mention
  of higgsfield.ai. Also trigger on generic "write me a video/image prompt" when
  Higgsfield is the platform. CONTINUATION TRIGGER: this skill must ALSO fire on every
  image/video generation or revision request in a conversation or project that has
  already used Higgsfield, even when the message never says "Higgsfield" and uses only
  shorthand — e.g. "shot 3", "next shot", "regenerate", "change the angle", "animate
  it", "the angle/outfit is wrong", any Soul ID reference, or any generate_image /
  generate_video / show_characters call. If a Higgsfield tool was used earlier in the
  conversation, route every later visual-generation or revision request through this
  skill before prompting.
user-invocable: true
metadata:
  tags: [higgsfield, video, image, prompt, cinematic, AI, filmmaking, motion, camera]
  version: 3.8.0
  updated: 2026-06-19
  author: O-Side Media
  license: MIT
---

# Higgsfield AI Prompt Skill

**Language rule:** Reply in whatever language the user writes in.

---

## MANDATORY WORKFLOW — do these in order, every time

For ANY Higgsfield-related request, follow this contract:

1. **Route the request.** Match the user's ask to the routing table in the "Route to the Right Skill" section below, and open the matching sub-skill file(s) with the read tool BEFORE writing any prompt or advice. Do not rely on prior knowledge — platform vocabulary, preset names, and model parameters must be read fresh from the skill files, because this platform's lineup changes between releases.
2. **Apply MCSLA** (Model · Camera · Subject · Look · Action) to every video prompt unless the user explicitly opts out. Full definition lives in `skills/higgsfield-prompt/reference.md`.
3. **Use named platform vocabulary only.** Camera names, motion presets, and style tokens must come from `vocab.md` or the relevant sub-skill. Do not invent terms the platform doesn't recognize — invented names silently degrade generations without warning.
4. **Append shared negative constraints** from `skills/shared/negative-constraints.md` before delivering any prompt.
5. **On the first Higgsfield response in a conversation**, state ONE short line naming which sub-skill you're routing to. Example: "Routing to higgsfield-prompt + higgsfield-camera for a cinematic chase." One line only, then proceed with the work.
6. **OFFER MCSLA OPTIONS WHEN UNCERTAIN — do not guess.** If any MCSLA element (Model · Camera · Subject · Look · Action) is ambiguous or under-specified for the shot, do NOT silently pick one and generate. Present the user a short labelled menu of concrete options drawn from the skill vocabulary and let them choose before generating. This applies especially to Camera (shot size + angle + movement) and Model selection, where a wrong silent guess wastes a generation. Format: name the element, give 2–4 named options with a one-line effect each, ask the user to pick. Skip the menu only when the user already specified that element or the choice is unambiguous from context. Burning credits on a guessed camera angle the user then rejects is the failure this rule prevents.

## HARD RULES (do not skip under any circumstances)

- NEVER write a Higgsfield prompt without reading at least `skills/higgsfield-prompt/reference.md` first in the current conversation.
- **RE-ENTRY GATE (per-request, not per-conversation):** The file-read requirement is NOT satisfied "once per chat." Before EVERY individual generation or revision request — including shorthand follow-ups like "shot 3", "fix the angle", "regenerate", "animate it" — confirm the relevant sub-skill is loaded in the CURRENT context window. In long iterative sessions the earlier read may have scrolled out of context; if you cannot see the sub-skill content right now, re-read it before prompting. Do not prompt from memory of a file you read 20 turns ago.
- **IMAGE PROMPTS REQUIRE `skills/higgsfield-image-shots/reference.md`.** For any still-image generation or any request to change framing, camera angle, shot size, or composition, read the image-shots sub-skill FIRST and lead the prompt with its named shot/angle keywords (e.g. "Side profile medium shot, eye-level"). Burying camera position in descriptive prose instead of using the named keyword is the #1 cause of ignored-angle failures. Camera/angle/shot-size direction goes at the FRONT of the prompt as a keyword, never as a paragraph of geometry.
- **ITERATION ANCHOR RULE:** When revising one variable (e.g. camera angle) on an approved frame, changing the `medias` anchor or re-rolling the whole scene will drift character, environment, and composition simultaneously. Change ONE variable per generation. If the angle is the target, hold everything else by anchoring on the agreed base frame; if the anchor itself is fighting the requested change (e.g. a new camera position the reference can't support), DROP the anchor and rely on the Soul ID + named shot keyword instead — do not keep re-anchoring on frames that contradict the requested change.
- NEVER substitute generic video-prompt vocabulary for named Higgsfield presets.
- NEVER skip MCSLA structure on video prompts.
- NEVER invent model versions, camera presets, or motion preset names. If the user names one you don't see in the skill files, say so and ask for clarification.
- If you find yourself thinking "I already know how to do this from training" — stop. Read the file. Your training data for this platform is stale.

---

## What Is Higgsfield?

Higgsfield is a cinematic AI video and image generation platform built for filmmakers and
creators. Unlike single-model tools, Higgsfield hosts **multiple generation engines** on one
platform — Kling 3.0/3.0 Omni/3.0 Motion Control, Sora 2, Google Veo 3.1/3.1 Lite, Wan 2.7/2.6/2.5,
Seedance 2.0/Pro, Minimax Hailuo 2.3/02, Higgsfield DoP (Lite/Standard/Turbo) for video; Soul 2.0, Soul Cinema Preview,
Soul Cast, Nano Banana Pro/2, Kling Image 3.0/Omni, Seedream 4.0, GPT Image 1.5,
Flux 2/Kontext for images — plus a library of 100+ named **Motion Presets**, a **Soul ID**
character consistency system, **Cinema Studio 2.5**, **Cinema Studio 3.0** (Business/Team plan), and **Cinema Studio 3.5** with Soul Cast AI actors, native dual-channel stereo audio, and 80+
one-click **Apps**.

---

## Workflow

### Fast Path — Simple Creative Requests

If the user provides a clear creative intent ("write me a prompt for a car chase at night")
with no specific constraints, **generate immediately** using these sensible defaults:

> **Fast Path still requires reading `skills/higgsfield-prompt/reference.md` first — Fast Path means skip clarifying questions, NOT skip the file read.**

| Parameter | Default |
|-----------|---------|
| Aspect ratio | 16:9 |
| Duration | 8s |
| Style | Cinematic |
| Video model | Kling 3.0 (character-focused) or Sora 2 (action/scale) |
| Image model | Soul 2.0 (portrait) or Nano Banana 2 (everything else) |

Do not ask clarifying questions. Deliver a ready-to-paste prompt. Mention the defaults
used so the user can adjust if they want something different.

> If you did not read `skills/higgsfield-prompt/reference.md` earlier in this conversation, read it now before writing the prompt.

### Full Path — Production Requests

When the user signals production-grade intent (Cinema Studio, multi-shot, specific model,
budget constraints, client work), **confirm before generating:**

**Required:**
- **Generation type**: Image / Video / App (one-click)
- **Video duration**: 5s / 10s (image-to-video clips are 3–5s; text-to-video up to 10s+)
- **Aspect ratio**: 16:9 / 9:16 / 1:1 / 4:5 / 4:3 / 2.35:1 (default: 16:9)
- **Model preference** (or ask Claude to recommend — see `skills/higgsfield-models/reference.md`)

**Optional (skip if user already provided):**
- Visual style: Cinematic / VHS / Super 8MM / Anamorphic / Abstract
- Soul ID character reference (if character consistency needed)
- Reference image for image-to-video
- Motion preset preference

> Ask everything in one message — do not split across multiple rounds.

---

### Route to the Right Skill

| User wants | Route to |
|------------|----------|
| User unsure which workspace/tool fits, or asks "what should I use for X" | `higgsfield-workspaces` |
| Write or improve a prompt | `higgsfield-prompt` + relevant sub-skills |
| Cinematic still image prompt (shot framing, angles) | `higgsfield-image-shots` |
| Choose the right model | `higgsfield-models` |
| Camera movement guidance (video) | `higgsfield-camera` |
| Named motion preset (Explosion, Werewolf, etc.) | `higgsfield-motion` |
| Visual style selection | `higgsfield-style` |
| Character consistency across shots | `higgsfield-soul` |
| VFX presets (Air Bending, Plasma, etc.) | `higgsfield-motion` |
| One-click App workflow | `higgsfield-apps` |
| Genre recipe (action, horror, ad, etc.) | `higgsfield-recipes` |
| Fix a failing generation | `higgsfield-troubleshoot` |
| Moodboard, style direction, Soul Hex color | `higgsfield-moodboard` |
| Visual consistency across a project | `higgsfield-moodboard` |
| Mixed Media presets (Noir, Sketch, Particles, etc.) | `higgsfield-mixed-media` |
| Artistic style transformation, preset stacking | `higgsfield-mixed-media` |
| Higgsfield Assist (GPT-5 copilot) | `higgsfield-assist` |
| Credit optimization, plan selection, budget strategy | `higgsfield-assist` |
| Cinema Studio 2.5 / Cinema Studio 3.0 / Cinema Studio 3.5 / multi-shot sequence workflow / Soul Cast | `higgsfield-cinema` |
| Optical physics, camera bodies, lenses, Hero Frame | `higgsfield-cinema` |
| Elements system (@Characters/@Locations/@Props) | `higgsfield-cinema` |
| Director Panel, Speed Ramp, shot modes, Popcorn | `higgsfield-cinema` |
| Cinema Studio 3.0 Smart mode, @ references, native audio | `higgsfield-cinema` |
| Cinema Studio 3.5 — three-pill UI, Style Settings, Camera Settings, Manual Style, AI director toggle | `higgsfield-cinema` |
| Multi-shot workflow, chaining tools, full production pipeline | `higgsfield-pipeline` |
| Short film, branded content, Popcorn → video → assembly | `higgsfield-pipeline` |
| Vibe Motion, motion graphics, kinetic typography, brand animation | `higgsfield-vibe-motion` |
| Animated text, logo animation, Remotion-based output | `higgsfield-vibe-motion` |
| Pre-generation memory check, apply past failure fixes | `higgsfield-recall` |
| Audio design, dialogue cues, SFX, ambient sound | `higgsfield-audio` |
| Cinematic Seedance film prompt, grounded motion, emotional close-up, driving/intimacy/action scene, weather interaction, shot continuity | `higgsfield-seedance-cinematic` |
| Seedance 2.0 / Pro prompt, flagged prompt, credit waste on Seedance | `higgsfield-seedance` |

---

### Check Templates for Genre Match

Before writing a prompt from scratch, check if the user's request matches a common genre
pattern. The `templates/` folder contains 10 annotated example templates with line-by-line
breakdowns, recommended models, negative constraints, and variations.

| User request matches | Check template |
|---------------------|----------------|
| Chase, pursuit, action, parkour | `templates/01-cinematic-action-chase.md` |
| Product, commercial, ad, UGC | `templates/02-product-ugc-showcase.md` |
| Horror, scary, creepy, dread | `templates/03-horror-atmosphere.md` |
| Fashion, editorial, lookbook | `templates/04-fashion-editorial.md` |
| Sci-fi, cyberpunk, VFX, space | `templates/05-sci-fi-vfx.md` |
| Portrait, character intro, close-up | `templates/06-portrait-character-intro.md` |
| Landscape, nature, establishing shot | `templates/07-landscape-establishing-shot.md` |
| Comedy, social media, TikTok, skit | `templates/08-comedy-social-media.md` |
| Romance, intimate, couple, wedding | `templates/09-romantic-intimate.md` |
| Dance, music, performance, concert | `templates/10-dance-music-performance.md` |

Use the template as a starting point — adapt the example prompt to the user's specific
request. The annotations explain WHY each element works, helping you make informed
substitutions.

---

### Build the Prompt Using the MCSLA Formula

Full MCSLA definition and prompt structure → `skills/higgsfield-prompt/reference.md`

Quick summary — five layers, every prompt:

| M | C | S | L | A |
|---|---|---|---|---|
| Model | Camera | Subject | Look | Action |

**Core rules:**
- Be specific — name camera presets, describe VFX concretely
- Keep prompts under 200 words
- Subject → Action → Camera → Style is the most reliable order

---

### Output Format

**Single prompt:**
```
**Model**: [model name]
**Aspect ratio**: [ratio]  **Duration**: [Xs]  **Style**: [style]

[Prompt]

**Camera**: [camera control name]
**Motion preset** (if used): [preset name]
```

**Two versions (when style varies):**
```
### Version 1 — [Style Name]
[Prompt]

---
### Version 2 — [Style Name]
[Prompt]
```

**Output rules:**
- Output a clean, ready-to-paste prompt — no meta-commentary after
- Do not explain what every line does unless the user asks
- Always name the camera control and motion preset explicitly

---

## @ Reference Rules

- User uploads image: use `[reference image]` or describe it as "the provided reference"
- For Soul ID character: note "using Soul ID character reference" in the prompt
- For video extension: note "extend from [reference video], continue with..."
- For style transfer: note "match the visual style of [reference image]"

---

## Shared Resources

| Resource | What it contains | When to use |
|----------|-----------------|-------------|
| `skills/shared/negative-constraints.md` | All generation artifacts + prevention phrases, by category | Check before every prompt — append relevant constraints |
| `templates/` | 10 annotated genre templates with examples, models, annotations, variations | When user request matches a common genre — use as starting point |

---

## Sub-Skills (auto-loaded as needed)

| Skill | Trigger |
|-------|---------|
| `higgsfield-workspaces` | User is choosing a workspace / asking "what should I use for X" / hasn't picked a tool yet |
| `higgsfield-prompt` | Any prompt writing or refinement request |
| `higgsfield-image-shots` | Cinematic image prompts — shot framing, angles, composition |
| `higgsfield-models` | "Which model should I use?" / model comparison |
| `higgsfield-camera` | Camera movement questions (video) |
| `higgsfield-motion` | Named preset requests (Explosion, Werewolf, VFX, etc.) |
| `higgsfield-style` | Visual style / aesthetic questions |
| `higgsfield-soul` | Character consistency / Soul ID |
| `higgsfield-apps` | One-click app recommendations |
| `higgsfield-recipes` | Genre scene templates |
| `higgsfield-troubleshoot` | Failed generations / quality issues |
| `higgsfield-moodboard` | Moodboard / Soul Hex / project-level style consistency |
| `higgsfield-mixed-media` | Artistic preset overlays (Noir, Sketch, Particles, etc.) |
| `higgsfield-assist` | Higgsfield Assist copilot / credit optimization / plan selection |
| `higgsfield-cinema` | Cinema Studio 2.5 + 3.0 + 3.5 / Soul Cast / color grading / optical physics / multi-shot / Elements / Smart mode / @ references / Style Settings / Camera Settings / Manual Style |
| `higgsfield-pipeline` | Multi-shot workflow / tool chaining / full production pipeline |
| `higgsfield-vibe-motion` | Vibe Motion / motion graphics / kinetic typography / brand animation |
| `higgsfield-recall` | Pre-generation memory check / apply past failure fixes |
| `higgsfield-audio` | Audio design, dialogue, SFX, ambient sound for audio-capable models |
| `higgsfield-seedance-cinematic` | Cinematic Seedance 2.0 film prompts — grounded motion, restrained performance, observer camera, environmental force, multi-shot continuity |
| `higgsfield-seedance` | Seedance 2.0 / Pro prompt director + content-filter preflight linter |

> Full vocabulary in `vocab.md`
> Full motion preset library in `skills/higgsfield-motion/reference.md`
> Model comparison in `model-guide.md`
> Example prompts in `prompt-examples.md`
> Shared negative constraints in `skills/shared/negative-constraints.md`
> Genre-specific annotated templates in `templates/`
