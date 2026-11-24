# How "performs better" is judged

Raw likes are misleading on Instagram. Big accounts get more of everything, likes are often hidden, and Reels reach people who don't follow the account. So the agent normalises and compares like with like.

| Metric | Formula | Used for |
|---|---|---|
| **x account median** | post metric ÷ that account's median for the same format | **The main signal.** Outliers; fair comparison across account sizes |
| View rate | views ÷ followers | Reels: how far a Reel travelled beyond the account's base (can exceed 1) |
| Engagement rate (ER) | (likes + comments) ÷ followers | All formats, when likes are visible |

The post metric is views for Reels, and likes + comments for carousels and statics when both are visible. With no usable metric, a post is analysed qualitatively and labelled as such.

## Rules
- **Compare within a format.** Reels vs Reels, carousels vs carousels.
- **Outlier = ≥ 2× the account's own median** for that format. Every post shows its multiple, so 2.1× and 8× don't look the same.
- **Small samples:** fewer than ~10 posts from an account in scope → its conclusions are marked *tentative*.
- **Tier-aware:** tier 3 (reach-context) accounts are never used as a metric benchmark for peers. Across tiers 1–2, compare *x account median*, not raw ER: ER naturally falls as follower count grows.
- **Never estimate.** Hidden or unreadable numbers are `not available`. Displayed numbers are kept as shown ("1.2K").
- **Intent beats vanity.** Buying-intent comments (price, delivery area, suitability) and the CTA type are recorded with every post and weighed in patterns.

## What counts as a pattern
A feature (theme, hook type, format, CTA, timing, caption style) that shows up in outperforming posts across **≥ 2 accounts or ≥ 3 posts**. Anything less is reported as a single example.

## Known limits
Within one account, dividing by followers doesn't change the ranking. Follower counts are captured on the day, not the post date. Recent Reels haven't finished collecting views. 2× is a "worth a look" bar, not a rare event.

[design-review.md §2](design-review.md#2-metrics-validity) covers each of these and the proposed fixes, which are not applied yet. [`scripts/outliers.py`](../scripts/outliers.py) recomputes medians and outliers from a post-record CSV, so the arithmetic doesn't depend on the model.
