---
name: ranked-research
description: Conducts multi-source web research on any topic, evaluates each claim's credibility based on corroboration and source authority, and outputs findings as a markdown file with claims grouped and ranked by reliability tier. Use this whenever the user mentions doing research, fact-checking, "looking into" something, due diligence, comparing what sources say, gathering info on a topic, investigating a claim, "checking what people say about" something, or pastes a question/topic expecting multiple sources weighed. Trigger even if the word "research" is absent — phrases like "find out about", "what's the deal with", "is X true", "compile info on", "look up everything on" all count. Skip only for single-fact lookups where one authoritative answer is all that's needed (e.g. "capital of France", "today's USD-SGD rate").
---

# Ranked Research

Web research with per-claim credibility ranking. Output saved as a markdown artifact.

## Definition

- **Name:** ranked-research
- **Scope:** Conducts multi-source web research, groups findings by claim, ranks each claim's credibility based on corroboration + source authority, and saves results as a markdown file. Does NOT: do single-fact lookups, access paywalled academic databases, conduct primary research (interviews, surveys, experiments), access private/internal docs, or produce original opinion/analysis beyond synthesis.
- **Context:** Fires when the user mentions doing research, fact-checking, due diligence, comparing source claims, investigating, "looking into" or "checking on" a topic, or pastes a claim/question expecting multi-source weighing. Skip for trivial factual lookups with no need for ranking.

## When to use

- "Research [topic]" / "look into [topic]" / "investigate [topic]".
- User wants to know what multiple sources say.
- User is fact-checking a claim or doing due diligence.
- User pastes a topic/question expecting a weighed multi-source answer.

## Inputs to elicit

Block on context and scope before searching. Ask narrowing question only if topic is too broad.

### 1. Context (purpose of the research)

Use `ask_user_input_v0`. Estimate 3 purposes from the topic. Add an "Other" option that triggers a free-text follow-up.

```
Question: What's this research for?
Type: single_select
Options:
- [estimated purpose 1 — e.g. "Academic / professional report"]
- [estimated purpose 2 — e.g. "Personal decision-making"]
- [estimated purpose 3 — e.g. "Article / content writing"]
- Other (I'll describe)
```

If "Other" → ask in chat for the purpose. Context affects:
- Tone of summary (formal / casual).
- Rigor: academic/professional → bias against opinions tier; flag weak claims more cautiously.
- Recency bias: medical / tech / legal / news → favor sources from last 2 years. Historical / philosophical → no recency filter.

### 2. Scope (which source types to include)

Use `ask_user_input_v0`, multi_select:

```
Question: Which source types should I include?
Type: multi_select
Options:
- Journals, gov, edu, established institutions
- News and established publications
- Blogs and independent sites
- Forums, Reddit, social media
```

Default if user doesn't care: all four. Lower-credibility sources are still collected — they get ranked, not omitted.

### 3. Topic narrowing

If topic is too broad to research in 20 sources (e.g. "AI", "climate change", "Islam"), ask one narrowing question before searching. Don't guess at scope.

## Algorithm

### Step 1 — Collect

Aim for ~20 sources across the agreed scope. Use multiple search queries with varied phrasing. Don't stop at the first page.

For each source, record:
- URL, title
- Source type (journal / gov / edu / news / blog / wiki / forum / social)
- Date (if visible and topic is time-sensitive)
- Key claims relevant to the topic

#### Search strategy by source tier

`web_search` favors mainstream/SEO-optimized results by default and underrepresents forums, comments, and social. To get a representative spread, allocate searches deliberately:

**For high-authority sources (journals, gov, edu)** — search with formal terminology:
- "[topic] systematic review", "[topic] meta-analysis", "[topic] clinical trial"
- "[topic] study journal", "[topic] PMC", "[topic] pubmed"
- Add the scientific/medical/technical term if one exists (e.g. "Phoenix dactylifera" for dates).

**For news and established publications** — search with the journalist framing:
- "[topic] research findings", "[topic] expert", "[topic] [year]"

**For forums, comments, social media** — search like a user posts, not like a journalist writes:
- First-person phrasings: "I've been [doing X]", "anyone else notice", "my experience with", "tried [X] for [duration]"
- Question phrasings: "is [X] worth it", "does [X] actually work", "[X] vs [Y] which better"
- Anecdotal markers: "honestly", "tbh", "real talk", "no bs"
- Platform names as keywords: "[topic] reddit thread", "[topic] quora", "[topic] stack exchange", "[topic] forum discussion"
- If the topic has a niche community, name it: "[topic] [community name] forum"

**If scope includes forums/social, budget at least 4–5 searches specifically for first-person and platform-targeted phrasings.** Generic searches will not surface these — they have to be hunted explicitly.

**Platforms to consider for the Opinions tier:**
- Reddit (search by phrasing — `site:reddit.com` operator is unreliable in `web_search`)
- Quora, Stack Exchange family (StackOverflow, Cross Validated, etc., for technical topics)
- YouTube comment sections (search the video title + "comment")
- Niche forums (Discourse-based communities, subject-specific boards)
- Blog comment sections of popular blog posts on the topic
- X/Twitter discussions (limited indexing — search distinctive phrasings)
- Facebook group discussions (limited; usually only public posts surface)

**If a search returns nothing for the Opinions tier, note that in the final output.** A thin Opinions section is a finding, not a failure — it means the topic doesn't have organic public discussion, which is itself meaningful context.

**For social-heavy research (e.g. user sentiment, product reviews, lived experience, cultural reactions), invert the budget**: spend more searches on first-person/platform queries and fewer on formal-source queries. The tiers will still apply — they just sort differently when the corpus shifts.

### Step 2 — Group claims

Bundle claims that say the same thing across sources. Each unique idea = one claim. Contradicting claims stay separate — do NOT merge them.

### Step 3 — Score each source's authority

Authority weight `S`:

| Source type | S |
|---|---|
| Peer-reviewed journal, gov site (.gov), official org docs on its own subject, top-tier edu (.edu research pages) | 1.0 |
| Established news with editorial standards (Reuters, BBC, AP, major national papers), industry publications, textbooks, recognized expert orgs | 0.6 |
| Mainstream blogs, Wikipedia, recognized industry blogs, well-established personal expert sites | 0.4 |
| Small blogs, Medium posts, niche sites, low-traffic news | 0.2 |
| Reddit, X/Twitter, Facebook, TikTok, YouTube comments, forum posts, news article comments | 0.1 |

Adjust S down if the source is off-topic for the claim (e.g. a medical journal making a financial claim → treat as 0.4, not 1.0). Authority is topical, not generic.

### Step 4 — Tier each claim

For each unique claim:
- `n` = number of distinct sources backing it
- `r` = number of those sources with S ≥ 0.6
- `s_max` = highest S among them

Apply in order:

1. **Authentic** — if `r ≥ 1` AND `n ≥ 2`. (At least one reputable source + at least one corroborator of any tier.)
2. **Good** — if `r = 0` AND `n ≥ 5`. (Widely repeated, no reputable backing.)
3. **Opinions** — if `s_max ≤ 0.1` AND `n ≤ 4`. (Only forums/social, low volume.)
4. **Weak** — everything else. (Includes: reputable source standing alone; mid-tier sources with few corroborators; low-tier with moderate corroboration but not many.)

### Step 5 — Flag contradictions

When two or more **Authentic** claims contradict each other, surface this in a dedicated "Contradictions" section. Don't pick a side. Show both claims with sources.

Lower-tier contradictions: only flag if they materially affect the answer.

## Output format

Save as markdown file via `create_file` → `present_files`. Template:

```markdown
# Research: [topic]

**Purpose:** [context the user gave]
**Scope:** [source types included]
**Date:** [today]
**Sources consulted:** [n]

## Summary

[2–4 paragraph plain-language overview. Mention which tiers most claims fell into. Note if research was thin or if scope limited results.]

## Findings

### Authentic
- **[Claim, one sentence.]** Sources: [1, 3, 7]
- **[Claim.]** Sources: [2, 9, 14]

### Good
- **[Claim.]** Sources: [...]

### Weak
- **[Claim.]** Sources: [...]

### Opinions
- **[Claim.]** Sources: [...]

## Contradictions

- **Claim A** (Authentic, sources 3, 7) vs **Claim B** (Authentic, sources 11, 14).
  [One-line note on what's at stake.]

## Sources

1. [Title](url) — Type: gov — Authority: 1.0
2. [Title](url) — Type: news — Authority: 0.6
3. ...
```

Omit any section that has no entries (e.g. no contradictions → drop the section).

## Edge cases

- **No reputable sources found.** Output still produced — everything will tier as Good / Weak / Opinions. Note this clearly in the summary.
- **Research is primarily social/sentiment-based** (e.g. "what do users say about [product]", "how do people feel about [topic]"). The Opinions and Good tiers become the main signal, not the noise. Apply the algorithm normally but lead the summary with what the social corpus reveals. Authentic-tier reputable sources may be sparse — that's expected and fine.
- **Topic is time-sensitive and sources are stale.** Flag in summary. Don't downrank a claim just for age — note it as context.
- **A single source dominates** (e.g. one Wikipedia article cites all the same upstream studies). Treat citation chain as one source, not many. Avoid corroboration inflation.
- **User pushes back on a tier.** They can. Adjust if their reasoning holds. Don't fight over the algorithm.
- **Paywalled source.** Note the URL, mark as "not fully verified" in the source list, exclude from corroboration count.
- **Non-English sources.** Include if relevant; translate the claim. Note original language in the source list.
- **Topic is sensitive (medical, legal, financial, religious).** Still produce the research. Don't add disclaimers unless the user asked for advice — this skill outputs findings, not recommendations.

## Notes

- Authority weights are heuristic, not absolute. State them transparently in the output so the user can audit.
- The tier is for the *claim*, not the source. Same source can produce one Authentic and one Weak claim depending on what's being said and what corroborates it.
- Don't omit low-credibility findings. Less credible ≠ less true. Rank, don't filter.
- If the user asks for "just the answer", produce the markdown file anyway but lead the chat reply with the top Authentic claims as a 3-bullet TL;DR.
