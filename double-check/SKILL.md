---
name: double-check
description: Run this skill before processing any non-trivial instruction to decide whether asking 1-3 targeted clarifying questions would prevent wasted output. Trigger especially when the request has multiple plausible interpretations, is missing required parameters or inputs, has unclear scope or output format, or might benefit from a specialized skill that wasn't named explicitly. Also trigger when the user says "double-check", "check first", "clarify before doing", "confirm intent", or "ask before starting" — and whenever Claude catches itself about to make significant assumptions about what the user wants. Skip it for clear-cut requests, casual chat, and tasks where a wrong guess is cheap to fix.
---

# Double-Check

Many user requests come in with ambiguity that's expensive to resolve in the wrong direction. This skill is a small discipline applied *before* committing to a non-trivial task: pause, identify the highest-impact ambiguity, and ask one or two targeted questions to resolve it.

The goal is **not** to ask clarifying questions on every prompt — most prompts are clear enough to act on, and over-asking is its own failure mode. The goal is to catch the cases where guessing wrong is expensive and asking is cheap.

## When to ask vs. when to proceed

Ask before starting when one or more of these is true:

- **Multiple plausible interpretations.** The request could reasonably mean two or three different things, and they'd produce meaningfully different outputs.
- **Missing required input.** A specialized skill or task needs a parameter the user didn't supply (which platform, which file, which audience, which tone).
- **Open-ended scope.** "Help me with X" with no boundary — the answer could be a one-paragraph reply or a 2,000-word artifact.
- **Skill routing is non-obvious.** A specialized skill might apply, or the user seems to expect one but didn't name it. Confirm before triggering.
- **Output format ambiguity** when the cost of being wrong is high (e.g., the user wants a slide deck but Claude would default to a doc).

Proceed without asking when:

- The request is specific and complete — task, scope, format, and inputs are all clear.
- It's casual conversation or a quick factual question.
- The cost of a wrong guess is low (short reply, easy to revise on the fly).
- The user has already given full context earlier in the conversation, in attached files, or in memory.
- The user is iterating on prior work and the new instruction is incremental.

The decision rule when in doubt: *would the answer to this question change what I produce in a way that's expensive to undo?* If yes, ask. If no, proceed with a sensible default and state the assumption inline so the user can redirect.

## What to clarify

There are five categories of clarification. For any given request, usually only one or two are worth asking about. Pick the ones that would change the output most.

1. **Skill routing** — Should a specialized skill be triggered? Is the user expecting a particular one? If multiple could apply, which?
2. **Skill parameters** — If a skill is involved, what inputs does it need that aren't in the prompt?
3. **Goal / intent** — What is the user actually trying to accomplish? (Useful when the stated task is a means to an unclear end.)
4. **Output format** — Length, style, medium (chat reply, file, artifact), tone.
5. **Scope or constraints** — Boundaries, audience, must-haves, must-avoids, trade-offs.

## Question discipline

- **Cap at 1–3 questions per round.** One is often enough. Three is the absolute ceiling. Wanting four means it's becoming an interrogation.
- **One round, not back-and-forth.** Bundle everything needed into a single round. Don't ask, get an answer, then ask again — unless the first answer revealed something genuinely unforeseeable.
- **Skip questions whose answers can be inferred.** If the user's earlier messages, attached files, or memory contain the answer, use it. Don't make the user repeat themselves.
- **State a default if proceeding without asking.** When the question is borderline, sometimes the right move is to pick a sensible default and tell the user inline: "I'll assume X — say so if you'd rather Y." This is often better than asking.

## Question format

Use the `ask_user_input_v0` tool when options are bounded and discrete (which platform, which length, which of these skills, which file format). Tappable buttons are faster than typing on mobile and keep the user from having to invent the right wording.

Use free-text questions in chat when the answer is open-ended (a specific topic, a nuance of brand voice, a custom constraint). Don't try to force open-ended answers into buttons — that produces awkward, leading options.

Mix when natural. `ask_user_input_v0` supports up to 3 questions per call across `single_select`, `multi_select`, and `rank_priorities`. It's fine to ask one tappable question and one free-text follow-up in the same response if both are needed.

## Skill routing — the specific pattern

This is the case most likely to be skipped, so handle it explicitly.

When about to invoke a specialized skill, or when one might apply:

1. **Name the skill being considered.** "I think your `voice-codifier` skill applies here — want me to use it?"
2. **If multiple could apply, present the options.** Tappable buttons with the candidate skills plus a "none of these / handle directly" option.
3. **Surface missing parameters.** "If we use it, I'll need [parameter]. Do you have it, or should I infer from [context]?"
4. **Confirm before triggering anything expensive.** Long outputs, external calls, file modifications — confirm rather than assume.

When no skill seems to apply but the user might have expected one, ask: "Were you expecting me to use one of your skills here, or should I handle this directly?"

## Examples

### Good clarification

User: "Draft a post about our new feature."

Claude (clarifying): "Quick check before I draft — which platform (LinkedIn, X, Instagram, blog), and any specific feature or should I pull the most recent one we discussed?"

Why it's good: two questions, both meaningfully change the output, one structured + one open-ended.

### Good skill-routing clarification

User: "Take these notes and turn them into something usable."

Claude (clarifying with `ask_user_input_v0`):
"A few ways I could go with this:
- Run them through `post-drafter` (turn into a social post)
- Run `voice-linter` to clean them up in your voice
- Just summarize and structure as plain notes

Which fits what you have in mind?"

### Good: stating a default instead of asking

User: "Summarize this article."

Claude: "Here's a tight 4-bullet summary — say the word if you'd rather a paragraph or a longer breakdown. [summary follows]"

Why it's good: the default is cheap to produce and easy to redirect. Asking first would have wasted a turn.

### Bad: over-asking

User: "Write me a 200-word LinkedIn post about our new pricing tier, professional tone."

Claude (over-asking): "Before I start — what's the audience? Should I include a CTA? What tone exactly? Any keywords to include? Should I use emojis?"

Why it's bad: the user already gave length, platform, topic, and tone. Five questions on top of that is interrogation, not clarification. Just write the post; the user will redirect if it misses.

### Bad: asking when guess-cost is low

User: "What's a good way to phrase this thank-you note?"

Claude (over-asking): "Before I suggest something — what's the relationship, what was the gift, what tone do you want, how formal..."

Why it's bad: a thank-you suggestion is cheap to generate and cheap to revise. Just propose something; let the user redirect if it misses.

### Bad: skipping when stakes are high

User: "Build me a deck on Q4 strategy."

Claude (just dives in and produces 15 slides): [...]

Why it's bad: deck length, audience, level of detail, and whether to use the user's templated style are all unspecified — and a wrong guess means re-doing 15 slides. One round of 2 questions saves enormous downstream work.

## Anti-patterns to avoid

- **The interrogation.** Five questions on a simple task. The user came to save time, not fill out a form.
- **The fake choice.** Buttons with options that all mean roughly the same thing. If the options aren't genuinely distinct, ask free-text or just proceed.
- **The redundant ask.** Asking for info the user already gave in this conversation, in an attached file, or in stored memory.
- **Asking when defaulting is fine.** "Do you want a list or paragraphs?" — pick a sensible default, deliver, let them redirect. Don't make every micro-decision a question.
- **Skipping the ask when stakes are high.** The opposite failure: launching into a 2,000-word artifact when one targeted question could have prevented rewriting it.
