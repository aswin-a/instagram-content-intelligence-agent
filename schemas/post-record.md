# Post record schema

One row per competitor post. CSV headers: [post-record.template.csv](post-record.template.csv). The **Field** column below matches the CSV headers exactly. [`scripts/check_repo.py`](../scripts/check_repo.py) fails if the two drift apart.

Rules that apply to every field:
- **Record what was displayed.** "1.2K" stays "1.2K"; don't expand it to a precise number.
- Anything hidden, unreadable or not reached is `not available`. Never estimate.
- A row without a **Post URL** doesn't go in the report.

| Field | Values / notes |
|---|---|
| Account | handle, as shown on the profile |
| Tier | 1–4 from competitor-list |
| Followers | as displayed on the profile, at capture time |
| Post URL | the permalink the record was read from (required) |
| Date | post date as displayed (absolute date if shown; otherwise the relative label, e.g. "2w") |
| Captured at | date the record was captured (YYYY-MM-DD) |
| Format | Reel / carousel / static. Stories aren't recorded: they expire and have no public metrics |
| Hook | first 3 seconds (Reel) or first line (caption / slide 1) |
| Hook source | where the hook was read from: `caption` / `cover` / `on-screen text` / `watched` |
| Segment | one of the brand profile's **segments** |
| Theme | one of the brand profile's **themes** |
| Visual style | e.g. talking head, POV, overhead kitchen, UGC, motion text |
| Language | e.g. English / Tamil / Tanglish |
| Caption length & CTA | short / medium / long + CTA type: WhatsApp, link in bio, free sample, DM, none |
| Hashtags | as posted |
| Audio | original / trending (name only if visible) / none / `not available` |
| Likes | as displayed, or `not available` (hidden) |
| Comments | as displayed, or `not available` |
| Views | as displayed, or `not available` |
| Engagement rate | (likes + comments) ÷ followers, or `not available` |
| Views / followers | Reels only, or `not available` |
| x account median | this post's metric ÷ the account's median for the same format, or `not available` |
| Buying-intent comments | count + examples (paraphrased, never quoted with usernames) |
| Claims flagged | anything passed to claims-check, or `none` |
| Why it likely worked | **[inference]**, tied to observable features |

Run-level facts (session type logged-in / logged-out, scope, accounts not reached) go in the report's coverage note, not in each row.
