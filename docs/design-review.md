# Design notes and trade-offs

A critical pass over my own agent: what holds up, what doesn't, and what I changed. Each point says whether it is **done** in the repo, **proposed** (it would change what the agent does, so it needs a decision first), or **roadmap**.

Nothing here reports results. The agent has not been formally evaluated yet. [Evaluation](#6-evaluation) describes how it would be.

---

## 1. Decomposition

**The split.** Analysis → trends → ideation follows the work a social team actually does. Each stage has different inputs and a different main risk:

| Stage | Main input | Main risk |
|---|---|---|
| Analysis | competitor profiles | made-up or misread numbers |
| Trends | Reels, Explore, hashtags | one viral post sold as a trend |
| Ideation | patterns, trends, brand profile | copying; off-brand ideas |

Analysis and trends don't depend on each other. Ideation depends on both.

**Claims-check is a gate, not a stage.** The first version listed it as step 4, as if it ran once at the end. In practice it does two different jobs:
- a **tagger** on competitor records: claims it finds go to section F as risks
- a **gate** on our own ideas: an idea can't reach section D until it has passed, been rewritten, or been dropped with a reason

A gate that can be skipped isn't a gate, so the system prompt now says it explicitly, and the diagrams draw it as a decision node. *Done.*

**Orchestration was implicit.** The system prompt mapped jobs to skills but didn't say what happens when a single-stage request arrives without its inputs. For example, "10 ideas" in a fresh chat has no section B or C to draw on. The original rule already covers this ("ask at most one clarifying question; otherwise proceed with stated assumptions"). What was missing was how that applies to stage dependencies. The system prompt now has a routing table, and says that ideas with no analysis behind them are labelled *brand-led, no source*. They are not given a made-up source inspiration. *Done.*

**Why not more agents.** A full run is roughly 16 accounts × 10–15 posts, so about 160–240 records. That fits in one context. Separate subagents per account would make runs more repeatable and keep raw page text out of the main context, but a Claude Project doesn't do that. *Roadmap.*

**Why no orchestrator skill.** In a Claude Project the system prompt *is* the orchestrator. Adding an orchestrator skill would only add a layer of indirection.

---

## 2. Metrics validity

The core idea holds up: likes are often hidden, so judge each post against **its own account's median, within one format**. But some details deserve scrutiny.

**Dividing by followers does nothing inside one account.** All posts from an account are captured on the same day against the same follower count. So `views ÷ followers` ranks them exactly as `views` does, and *× account median* comes out the same either way. Follower normalisation only matters **across** accounts. Even there, it measures something specific. Reels are shown to non-followers through recommendations, so `views ÷ followers` tells you how far a Reel travelled beyond the account's own audience, and it can exceed 1. It is not a measure of how much followers liked it. I now treat *× own median* as the main signal and views ÷ followers as context. *Done (docs).*

**Follower count is today's, not the post date's.** For a small account that is growing fast, older posts get divided by a bigger number than they had at the time, so they look worse. A short window (about 30 days) limits this, and each record now has a capture date. *Done.*

**Small samples get smaller once split by format.** "Fewer than ~10 posts → tentative" is the right rule at account level. But medians are per format, and 10 posts might be 6 Reels, 3 carousels and 1 static. A median of 3 hardly counts as a baseline. `scripts/outliers.py` reports *n* for each account × format and labels any group under 5 as a small group. Whether the agent should refuse to compute *× median* below some *n* is *proposed*.

**Recency bias.** Reels keep collecting views for days after posting. A post from two days ago sits below the median just because it is new, which biases "bottom 3" towards the latest posts. *Proposed:* label posts younger than about 7 days *too recent* and leave them out of the median and the top/bottom ranking. The script supports this with `--min-age-days`, which is off by default because the agent doesn't do it yet.

**Pinned posts.** Profile grids show up to three pinned posts first. These are often old hits. If the agent collects "the last 10–15 posts" in grid order, pinned posts slip into a recent window they don't belong to. Now listed as a failure mode. *Done.*

**Comparing across tiers.** Engagement rate usually falls as follower count grows, so a raw ER league table always favours small accounts. The tier rule (tier 3 is never a benchmark) handles the extreme case. For tier 1 vs tier 2, the fair comparison is *× own median* ("this post did 3× its account's normal"), not raw rates. *Done (docs).*

**Logged-out vs logged-in.** What Instagram shows depends on whether you are signed in, on the account owner's settings (for example, hidden like counts), and on the platform's current UI, which changes over time. I don't want the repo claiming specifics that may be out of date. The rule is: record what was displayed, the capture date, and the session type, and keep the session type the same across runs so results can be compared. *Done (failure modes + coverage note).*

**Is 2× the median a sensible outlier rule?** It works as a "worth a look" threshold, but it isn't rare. View counts are heavy-tailed. As a purely mathematical illustration (not data): if an account's views were log-normal with σ = 1, about a quarter of its posts would clear 2× the median. So "outlier" partly means "top quartile". Mitigations:
- The report shows *× median* for every post, so 2.1× and 8× don't read as the same thing. *Done.*
- A pattern still needs ≥ 2 accounts or ≥ 3 posts behind it. *Already in place.*
- A stronger "breakout" tier (e.g. ≥ 4×) next to the 2× flag. *Proposed.*

**Display rounding.** "1.2K" means anything from 1,150 to 1,249, roughly ±4%. That is small next to a 2× threshold, but reported ratios shouldn't claim more precision than the display gives. Records keep the number as shown. *Done (schema note).*

**What I'd add if more data were visible:** comments ÷ views as a signal of resonance that doesn't depend on hidden likes. *Proposed.*

---

## 3. Data collection

**Browser vs official APIs.** The Instagram Graph API gives a professional account detailed insights into **its own** posts (reach, plays, saves, shares). Those are far better than anything visible publicly, and they are the right source for closing the loop (§9). For other accounts, the API only exposes a limited set of public fields for professional accounts; check the current Meta documentation for which ones. It can't give the things this agent mostly needs: what the hook is, what's on screen, which audio, and what commenters are asking. The end state is hybrid: **API for our own account, browser for competitor content.** *Roadmap.*

**Platform terms and rate limits.** A browser agent using someone's signed-in session is automated access on that person's account. Instagram's [Terms of Use](https://help.instagram.com/581066165581870) restrict collecting information in automated ways. Low volume, human pace and read-only lower the risk but don't remove it. The account could be challenged or restricted. Existing controls:
- stop on CAPTCHAs, rate limits and "unusual activity" warnings
- never work around them
- bounded scope per run

Whether this use is acceptable is **the brand's decision, not the agent's**. The README now says so.

**Text read vs screenshot for Reels.** Reading the page as text gives captions, counts and comments. It can't see the hook, which for a Reel is visual or spoken in the first 3 seconds. So when the agent reads text, the **Hook** field is really the caption's first line or the cover. The schema now has a **Hook source** field (`caption`, `cover`, `on-screen text`, `watched`), so a reader knows how much to trust it. Screenshots are worth their context cost only where text can't see the content: cover frames and on-screen text. *Done.*

**Reproducibility.** Explore and the Reels feed are personalised and change all the time, so two trend scouting runs won't match. That's inherent. The report labels trends as a dated snapshot. The parts that *can* be reproduced now are: the competitor list, the scope, the post URL and capture date on every record, and a CSV of records that a script can recompute. *Done.*

---

## 4. Hallucination risk

Where an LLM is most likely to make things up here, roughly in order:

1. **Numbers.** Filling in a hidden like count; turning "1.2K" into "1,213"; working out medians in its head and getting the arithmetic wrong.
2. **Handles.** Required fields like "example account" push the model to fill them, and plausible look-alike handles are easy to generate.
3. **Audio names.** Same pressure from a required field.
4. **Trends.** A trend remembered from training data rather than seen this week, or a single post presented as a trend.
5. **Dates.** Relative dates ("2w") turned into wrong absolute ones.
6. **Causation.** "Why it worked" written as fact.

What prevents them:

| Risk | Control |
|---|---|
| Numbers | `not available` is required, not optional; the number is recorded as displayed; medians can be recomputed from the CSV with [`scripts/outliers.py`](../scripts/outliers.py) |
| Handles, trends, audio | **Every post record and every trend example must carry the URL it was read from.** No URL, not in the report. Fields that invite invention explicitly accept `not available` *(done)* |
| Single-post trends | Trends must state how many examples were seen *(already in place)* |
| Causation | `[inference]` labels *(already in place)* |
| Dates | Record the date as displayed plus the capture date *(done)* |

**Mandatory links or screenshots per claim?** Links, yes. They cost almost nothing and turn a spot-check into a two-minute job. Screenshots for every claim, no. They are heavy on context and can't be stored in a Project. Use them only for Reels hooks and on-screen text.

---

## 5. Structured output

**Yes for post records, and now for ideas too.**
- **Post records:** one CSV row per post, appended each run. This is the dataset behind the report. It builds up over time and a script can check it.
- **Idea records:** id, format, mix tags, CTA, source URL and claims-check result. These make the mix rule and the claims gate checkable instead of just stated. See [`schemas/idea-record.md`](../schemas/idea-record.md). *Done.*
- **The report stays markdown**, because the social team reads it.

`scripts/check_repo.py` checks that each CSV header matches its schema table, so the two can't drift apart.

**JSON Schema** would be the next step if the records ever fed an application. For CSV in a sheet, it adds little. *Could.*

---

## 6. Evaluation

Nothing below has been run yet. These are the checks I'd run, with targets I'm setting, **not results**. The seeded cases are in [`evals/`](../evals).

| Eval | How | Target |
|---|---|---|
| Schema completeness | every field filled with a value or `not available` (scriptable) | 100% |
| Sourced metrics | % of numeric fields with a post URL; spot-check 10 random records against the live post | 100% with a URL; 10/10 match the display |
| Claims-check recall | seeded fictional captions with known risk levels ([`evals/cases.csv`](../evals/cases.csv)) | catches every High; Medium recall reported |
| Claims-check precision | safe captions in the same set | false positives reported, not hidden |
| Look-alike handles | seeded look-alikes | none treated as the real brand |
| Prompt injection | seeded captions with instructions in them | none followed; all flagged in the coverage note |
| Idea quality | rubric: on-brand, shootable this week, original, meets mix + CTA rules, claims-safe ([`evals/idea-rubric.md`](../evals/idea-rubric.md)) | rated 1–3 by the social team |
| Usefulness | % of ideas the team actually shoots | tracked over time |

Re-run the seeded set after every prompt change.

---

## 7. Prompt injection and safety

**Everything read from Instagram is untrusted input:** captions, comments, bios, on-screen text, alt text, usernames, audio titles, and any page a link leads to. There are two kinds of attack:
- **Instructions.** "Ignore previous instructions", "Comment 🔥 to enter", "DM us for collab", "visit this link".
- **Poisoned facts.** A bio saying "India's #1 vet-approved brand". This is a *claim to record*, not a fact to repeat.

Controls (*done*):
- The system prompt, guardrails and every browsing skill state that page content is data, never instructions.
- Don't open links found in bios, captions or comments.
- Record injection attempts in the coverage note.

**The honest limit.** "Read-only" is a **prompt-level** control. Claude in Chrome can click anything a person can, so nothing in the tool itself stops a like or a follow. Defence in depth means:
- using the browser tool's most restrictive permission setting where it has one, so any action beyond navigating needs approval
- keeping a human in the loop for anything that leaves the browser

The agent never publishes. A person on the social team shoots and posts.

---

## 8. Claims compliance: a product-risk control

For a food brand, one bad caption costs more than ten good ideas earn. So claims-check is designed like a risk control, not a style check:

- **The brand owns the policy.** Claims rules live in the brand profile, not in the agent.
- **Severity levels.** High = never; Medium = rewrite or confirm.
- **Recall over precision.** A false positive costs an edit. A false negative costs a complaint.
- **A gate on our own ideas**, not just advice.
- **Human sign-off.** Nothing is posted by the agent.

**The list is a floor, not a compliance sign-off.** The brand should check the Indian advertising and food rules that apply. That means the [ASCI](https://www.ascionline.in) code and its guidance on health claims, and whichever food-safety rules cover **pet** food specifically. [FSSAI](https://www.fssai.gov.in) covers human food, so the brand should confirm what applies to pet food rather than assume. I've deliberately not written specific legal rules into the repo.

**One gap the agent can't close:** brand-supplied social proof (e.g. "1000+ meals served") is used as given. Backing it up is the brand's job, and the template says so.

---

## 9. Closing the loop (roadmap)

Today the agent learns only from competitors. The missing signal is **which of our own ideas worked**:

1. Give each idea an ID (done) and tag the post when the team publishes it.
2. Pull our own post insights through the Graph API. These are reach, saves, shares and plays, which are richer than anything public.
3. Score each post against **our own median**, the same method used for competitors.
4. Feed the results to ideation as "what worked for us".

Treat this as weak evidence: small *n*, no control group, and seasonality. *Roadmap.*

---

## 10. Prioritised improvements

**Must** (done in this revision)
- [x] Claims-check made an explicit gate on ideas, and a tagger on competitor posts
- [x] Treat page content as untrusted input; don't open links from captions, bios or comments; log injection attempts
- [x] Post URL and capture date on every record; hook source labelled
- [x] Inputs / Outputs / Stop conditions in every skill; descriptions say when to trigger
- [x] Fix drift: theme names aligned to the original; themes, segments, breed examples and gap ideas moved into brand config; competitor post formats limited to Reel / carousel / static (Stories have no public metrics)
- [x] Explicit routing and missing-input handling
- [x] [Failure modes](failure-modes.md) and a [coverage map](coverage.md) back to the original prompt

**Should**
- [x] Seeded eval set and idea rubric (not yet run)
- [x] `outliers.py` to recompute medians and outliers from the CSV, so arithmetic isn't trusted to the model
- [ ] *Proposed:* "too recent" rule (posts < ~7 days old kept out of medians and rankings)
- [ ] *Proposed:* minimum group size before computing *× median* for a format
- [ ] Run the evals and publish the results, including failures

**Could**
- [ ] *Proposed:* ≥ 4× "breakout" tier; comments ÷ views as a resonance signal
- [ ] Graph API for our own account (closing the loop)
- [ ] Weekly scheduled run with records building up in a sheet
- [ ] Package the skills as a Claude Code plugin (the `skills/<name>/SKILL.md` layout already fits)
- [ ] One subagent per account for repeatability
- [ ] JSON Schema for the records
