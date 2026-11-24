---
name: competitor-analysis
description: Collect competitor Instagram posts (provided or browsed read-only), record each against the post-record schema, normalise metrics per account and format, find outliers and patterns. Use for "analyse competitors", "what's working for X", or report sections A and B.
---

# Competitor analysis

## Inputs
- `competitor-list` (tiers), `brand-profile` (category filter), optional posts/screenshots/links the user provides
- Scope: time window and accounts (default: all tier 1–2 accounts, last ~30 days or last 10–15 posts each)

## Steps
1. **Collect.** For each account: follower count, then recent posts in the scope. Browse read-only with Claude in Chrome; read pages as text where possible. Skip off-category posts (e.g. cat content from a dog+cat brand). If an account or post can't be accessed, record that; don't fill the gap.
2. **Record** each post with every field in [schemas/post-record.md](../../schemas/post-record.md). Visible numbers go in as seen; missing ones are `not available`.
3. **Normalise** (see [docs/metrics.md](../../docs/metrics.md)):
   - ER = (likes + comments) ÷ followers, when likes are visible
   - Reels: views ÷ followers
   - per-account **median** by format; flag **outliers** at ≥ 2× median
   - mark accounts with < ~10 posts in scope as **tentative**
4. **Read the comments** for buying intent (price, delivery area, suitability for a life stage or breed) and note the CTA type.
5. **Explain.** For outliers and underperformers, write *why it likely worked or didn't*, labelled `[inference]`, pointing to observable features (hook, first frame, theme, segment, audio, CTA).
6. **Pattern-find** across accounts and within formats: themes, hooks, formats, timing, caption styles and CTAs that consistently outperform. A pattern needs ≥ 2 accounts or ≥ 3 posts behind it; otherwise call it a single example.
7. **Flag claims.** Pass any health or efficacy claims to `claims-check`.

## Outputs
- Post records table (or sheet rows)
- **A. Performance summary:** top 5 and bottom 3 posts, with the pattern behind each
- **B. Patterns**
- Notes on coverage: accounts not reachable, tentative accounts, tier mix

## Stop conditions
- Login wall, CAPTCHA, rate-limit or "unusual activity" warning: stop and report; don't work around it.
- Never like, follow, comment, DM, save or post.
