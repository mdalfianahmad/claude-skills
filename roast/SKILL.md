---
name: roast
description: Anti-sycophancy decision council. Honestly stress-tests an idea or decision through a council of opposing personas (contrarian, expansionist, first-principles, deep researcher, buyer) plus a separate judge that returns a green/reshape/kill verdict and the cheapest 48-hour test. Use before any real decision — product idea, offer, pricing, niche, architecture, or strategy — where the risk is the model just agreeing with your framing. Skip for trivial tasks.
---

# Claude Roast — anti-sycophancy decision council

Claude (and every LLM) tends to agree with you. This skill makes it honestly stress-test your idea or decision through a council of opposing personas plus a **separate judge** — before you build anything.

## When to use
Before any real decision: product idea, offer, pricing, niche, architecture, strategy. Skip for trivial tasks.

## How it works
Spin up personas in parallel, each attacking from a different angle:
- **Contrarian** — find the single fatal flaw.
- **Expansionist** — maximum upside, glass-half-full.
- **First-principles** — pure logic, no outside context.
- **Deep researcher** — pull real market data and competitor pricing from the web.
- **Buyer** — roleplay the actual target customer: would I pay, how much, what stops me, what I use now.

Then a **Judge** — a *separate* persona, not the author — merges everything into one verdict:
🟢 green / 🟡 reshape / 🔴 kill, plus the cheapest **48-hour test** to validate before writing a line of code.

**Key principle: worker ≠ judge.** The agent never declares itself right; a different persona judges the output. This directly fixes sycophancy (the model agreeing with its own/your framing).

## Output format
```
Idea/decision: <name>
For:        <2-3 strongest arguments>
Against:    <2-3 real risks>
Buyer:      <would buy / wouldn't + main reason>  (product/commercial decisions only)
Verdict:    🟢 / 🟡 / 🔴  + concrete next step or alternative
Cheapest 48h test: <one action that shows in 2 days whether to continue>
```

## Install
**Claude Code:** copy `SKILL.md` to `~/.claude/skills/claude-roast/SKILL.md`. It loads automatically.

**Any other agent:** paste `SKILL.md` into your system prompt / rules.

## Credit
The "roast" / persona-council approach (5 personas + judge, worker≠judge, cheap 48h test) comes from **Nate Herk** (channel *Nate Herk | AI Automation*): https://www.youtube.com/watch?v=iTY8Q449YNQ

This repo is my implementation of that approach as a reusable, drop-in skill for Claude Code and other AI agents. Method and persona framework credit to Nate Herk.

## License
MIT © Sergei Chaplygin
