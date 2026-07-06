# double-check

A Claude skill that pauses before processing a non-trivial instruction and asks 1–3 targeted clarifying questions — but only when the answer would meaningfully change the output. The goal is to spend a few tokens asking instead of many tokens producing the wrong thing.

## What it does

When Claude is about to act on an instruction, this skill prompts a quick judgment call:

- Is the request specific and complete? → just proceed.
- Are there multiple plausible interpretations, missing inputs, unclear scope, or a specialized skill that might apply? → ask a small, focused round of questions first.

It's deliberately *not* a "always ask before doing anything" skill. Over-asking is its own failure mode. The skill is built around one decision rule:

> Would the answer to this question change what I produce in a way that's expensive to undo?

If yes, ask. If no, proceed with a sensible default and state the assumption inline.

## What it covers

Five categories of clarification, with guidance on which to pick for any given request:

1. **Skill routing** — Should a specialized skill be triggered? Is the user expecting a particular one?
2. **Skill parameters** — What inputs does the skill need that aren't in the prompt?
3. **Goal / intent** — What is the user actually trying to accomplish?
4. **Output format** — Length, style, medium, tone.
5. **Scope or constraints** — Boundaries, audience, must-haves, must-avoids.

A dedicated section walks through the skill-routing pattern specifically — naming the candidate skill, presenting alternatives if multiple apply, surfacing missing parameters, and confirming before triggering anything expensive.

## Question format

The skill prescribes a mix:

- **Tappable buttons** (`ask_user_input_v0`) when options are bounded and discrete — platform, length, file format, which-of-these-skills.
- **Free-text** in chat when the answer is open-ended — a specific topic, a brand-voice nuance, a custom constraint.

It caps questions at three per round and pushes for a single round, not back-and-forth.

## Installation

Place the `SKILL.md` file in Claude's skills directory:

```
~/.claude/skills/double-check/SKILL.md
```

Or, on Claude.ai, upload it as a custom skill via the skills interface.

## Usage

Once installed, the skill triggers automatically when its description matches the situation. You can also invoke it explicitly:

> "Double-check what I want before you start."
>
> "Clarify before doing this."
>
> "Confirm intent first."

## Files

- `SKILL.md` — the skill itself (this is what Claude loads)
- `README.md` — this file

## Design notes

The skill leans heavily on examples — both good clarifications and bad ones — because the failure modes are subtle. A skill that always asks is annoying; a skill that never asks burns tokens producing the wrong artifact. The sweet spot is judgment-heavy, so the skill teaches the judgment rather than enforcing rigid rules.

The trigger boundary ("Claude judges case-by-case") is the most likely thing to need tuning over time. If Claude under-triggers (still diving in when it should pause) or over-triggers (asking when it should default), the description is where to adjust.
