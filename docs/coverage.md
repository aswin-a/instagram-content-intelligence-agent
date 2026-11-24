# Coverage: original prompt → repo

The repo was built from one self-contained prompt, [original-prompt.md](../examples/dhees-pet-company/original-prompt.md), which is the ground truth for what the agent does. This table maps each requirement to where it lives now, so nothing was lost in the split.

| Original requirement | Where it lives |
|---|---|
| Identity: brand, site, handle, Chennai delivery | [brand-profile](../examples/dhees-pet-company/brand-profile.md) § Identity |
| Dogs only; no cat content, recipes or hashtags | [system prompt](../agent/system-prompt.md) (generic), brand-profile § Identity, [guardrails](guardrails.md) §6 |
| Product: fresh, small-batch, human-grade; no preservatives or fillers; lab-tested; nutritionist-formulated; 55 km radius | brand-profile § Identity, § Product range |
| Range: Chicken, Beef, Puppy bowls with prices and roles | brand-profile § Product range |
| Calories and macro split shown; ingredients named plainly | brand-profile § Product range |
| Audience + neighbourhoods | brand-profile § Audience |
| Conversion path; social proof | brand-profile § Conversion path |
| Tone; English with Tamil/Tanglish | brand-profile § Tone and language |
| Differentiators | brand-profile § Differentiators |
| Claims: no prevent/treat/cure or longer life | system prompt § Claims guardrails, guardrails §1, [claims-check](../skills/claims-check/SKILL.md) High |
| Claims: no unverified "vet approved" / "clinically proven" | same + brand-profile § Claims rules |
| Claims: competitor health claims are a risk, not a tactic | claims-check tagger mode, brand-profile § Claims rules |
| Claims: prefer showable claims; customer results only with permission | claims-check § Safe claims, guardrails §1 |
| Competitor list in project doc "competitor-list" | system prompt § Sources, [competitor template](../config/competitors.template.md) |
| Tiers: Chennai/TN, India fresh, reach context, global benchmarks (all handles) | [competitor-list](../examples/dhees-pet-company/competitor-list.md) |
| @thefarmersdogpub is not The Farmer's Dog | competitor-list § Notes, [failure modes](failure-modes.md) |
| Dog+cat brands: dog content only | competitor-list § Notes, competitor-analysis step 1 |
| Likes hidden → judge Reels by views ÷ followers and vs own median | system prompt, [metrics](metrics.md), competitor-list § Notes |
| Job 1: competitor analysis (provided or browsed posts) | system prompt § Your jobs, [competitor-analysis](../skills/competitor-analysis/SKILL.md) |
| Job 2: trend scouting (Reels, hashtags, Explore, dog/pet/food/Chennai creators) | [trend-scouting](../skills/trend-scouting/SKILL.md), brand-profile § Trend scouting focus |
| Job 3: ideas; never copy, recreate the idea with our angle | [content-ideation](../skills/content-ideation/SKILL.md) § Adapt, don't copy |
| ER = (likes + comments) ÷ followers; Reels views ÷ followers | metrics, system prompt, competitor-analysis step 3 |
| Compare within format | metrics § Rules |
| Outliers ≥ 2× own median | metrics § Rules, [outliers.py](../scripts/outliers.py) |
| Buying-intent comments (price?, delivery to Porur?, good for puppies?) | system prompt, competitor-analysis step 4, post-record field |
| CTA type (WhatsApp, link in bio, free sample, DM, none) | post-record "Caption length & CTA" |
| < ~10 posts → tentative | metrics, competitor-analysis step 3, outliers.py |
| Never invent metrics; "not available" | system prompt, metrics, [post-record](../schemas/post-record.md) |
| 16 post fields (Account … Why it likely worked) | post-record schema (all 16, plus Tier, Followers, Post URL, Captured at, Hook source, Views / followers, x account median, Buying-intent comments, Claims flagged) |
| 12 themes | brand-profile § Content taxonomy (original names); post-record "Theme" points there |
| Dog segments | brand-profile § Content taxonomy |
| A. top 5 / bottom 3 with pattern | [output format](output-format.md), competitor-analysis § Outputs |
| B. patterns: themes, formats, hooks, timing, captions, CTAs | output format, competitor-analysis step 6 |
| C. trend: what, example account, why, Easy/Medium/Hard for a phone team in Chennai | output format, trend-scouting § For each trend |
| D. 10 ideas with 8 fields | output format, content-ideation, [idea-record](../schemas/idea-record.md) |
| D. CTA usually WhatsApp or free sample | brand-profile § Conversion path, content-ideation field 6 |
| D. mix: ≥ 2 puppy/life-stage, ≥ 2 education/trust, ≥ 2 customer-proof, ≥ 1 breed-specific (Rottweiler, Beagle, Labrador, Indie) | brand-profile § Content taxonomy, content-ideation § Required mix |
| E. gaps (neighbourhood, Tamil, live kitchen, macros, Indie breeds) | brand-profile § Gap angles, content-ideation § E |
| F. risk flags | claims-check § Outputs |
| Rule: label facts vs inferences | system prompt § Rules, guardrails §2, output format |
| Rule: don't copy captions, scripts, visuals | system prompt, guardrails §3, content-ideation |
| Rule: don't fabricate; say if not accessed | system prompt, guardrails §2, failure modes |
| Rule: no like, follow, comment, DM, post | system prompt, guardrails §4, every browsing skill's stop conditions |
| Rule: specific and ready to shoot | system prompt, content-ideation |
| Rule: at most one clarifying question | system prompt, guardrails §7 |

## Added beyond the original (all tighten, none loosen)
- Source URL and capture date on every record; hook source
- claims-check as a gate on ideas, and Medium-risk tier (implied outcomes, before/after, testimonials without permission, audio licensing)
- Untrusted-content / prompt-injection rule; don't open links from page content
- Stop on login walls, CAPTCHAs, rate limits; human pace; "save" added to the read-only list
- Stories excluded from competitor records (no public metrics)
- Coverage note at the end of every report
