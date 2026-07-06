# Claude Roast 🔥 — make Claude stop yes-manning you

A drop-in skill for Claude Code (and other AI agents) that forces honest evaluation of your ideas and decisions instead of polite agreement.

LLMs are sycophantic by default — they optimize for making you feel good, not for telling you the truth. Research (the ELEPHANT study) found models fail to challenge a user's framing ~88% of the time. The longer you work with memory/personalization on, the more it just tells you what you want to hear.

**Claude Roast** fixes that with a council of opposing personas and a separate judge.

## What you get
- **Contrarian** — hunts the fatal flaw
- **Expansionist** — finds the real upside
- **First-principles** — pure logic, no fluff
- **Deep researcher** — pulls real market data & competitor prices
- **Buyer** — roleplays your actual customer (would they pay?)
- **Judge** — a *separate* persona delivers the verdict 🟢/🟡/🔴 + the cheapest 48-hour test

Core principle: **worker ≠ judge.** The model never grades its own homework.

## Install
**Claude Code:** copy `SKILL.md` to `~/.claude/skills/claude-roast/SKILL.md` — loads automatically.
**Other agents (Cursor, etc.):** paste `SKILL.md` into your system prompt.

Then just ask it to "roast" any idea, offer, or decision before you build it.

## Credit
Approach by **Nate Herk** (*Nate Herk | AI Automation*): https://www.youtube.com/watch?v=iTY8Q449YNQ
This is my reusable skill implementation of his persona-council method.

## License
MIT © Sergei Chaplygin
