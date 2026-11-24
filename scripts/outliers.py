#!/usr/bin/env python3
"""Recompute per-account, per-format medians and >= 2x outliers from a post-record CSV.

The agent does this arithmetic in chat; this script is the deterministic check.
Standard library only.

Metric per post (as in docs/metrics.md):
  Reel             -> Views
  carousel/static  -> Likes + Comments (only if both are visible)
Values of "not available" (or blank) are ignored, never estimated.
Displayed abbreviations are parsed: "12.3K" -> 12300, "1.2M" -> 1200000, "1,234" -> 1234.

Usage:
  python3 scripts/outliers.py schemas/post-record.template.csv
  python3 scripts/outliers.py scripts/sample-post-records.FICTIONAL.csv [--min-age-days 7]

Lines starting with '#' are ignored (used to label sample files).
"""
import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import date
from statistics import median

OUTLIER_X = 2.0          # original rule: >= 2x the account's own median
TENTATIVE_POSTS = 10     # original rule: < ~10 posts per account -> tentative
SMALL_GROUP = 5          # per-format group size below which the median is labelled small


def parse_count(raw):
    """Parse a displayed count. Returns None for 'not available', blank or unparseable."""
    if raw is None:
        return None
    s = raw.strip().lower().replace(",", "")
    if not s or s in {"not available", "n/a", "na", "-"}:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([km]?)", s)
    if not m:
        return None
    mult = {"": 1, "k": 1_000, "m": 1_000_000}[m.group(2)]
    return float(m.group(1)) * mult


def parse_iso(raw):
    try:
        return date.fromisoformat((raw or "").strip())
    except ValueError:
        return None


def post_metric(row):
    fmt = row.get("Format", "").strip().lower()
    if fmt == "reel":
        return parse_count(row.get("Views")), "views"
    likes, comments = parse_count(row.get("Likes")), parse_count(row.get("Comments"))
    if likes is None or comments is None:
        return None, "likes+comments"
    return likes + comments, "likes+comments"


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def fmt_num(x):
    return "n/a" if x is None else (f"{x:,.0f}" if x >= 100 else f"{x:.2f}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv")
    ap.add_argument("--min-age-days", type=int, default=0,
                    help="PROPOSED rule, off by default: keep posts younger than N days "
                         "(Captured at - Date) out of the median and outlier call")
    args = ap.parse_args(argv)

    rows = read_rows(args.csv)
    if not rows:
        print(f"{args.csv}: no post records (header only). Nothing to compute.")
        return 0

    posts_per_account = defaultdict(int)
    groups = defaultdict(list)  # (account, format) -> list of post dicts
    for i, row in enumerate(rows, 1):
        acct = row.get("Account", "").strip() or "<unknown>"
        fmt = row.get("Format", "").strip() or "<unknown>"
        posts_per_account[acct] += 1
        value, kind = post_metric(row)
        too_recent = False
        if args.min_age_days:
            d, cap = parse_iso(row.get("Date")), parse_iso(row.get("Captured at"))
            if d and cap and (cap - d).days < args.min_age_days:
                too_recent = True
        groups[(acct, fmt)].append({
            "row": i, "url": row.get("Post URL", "").strip() or "<no URL>",
            "value": value, "kind": kind, "too_recent": too_recent,
        })

    print("== Groups (account x format) ==")
    print(f"{'account':28} {'format':9} {'posts':>5} {'w/ metric':>9} {'median':>10}  notes")
    outliers, no_metric, recent = [], 0, 0
    for (acct, fmt), posts in sorted(groups.items()):
        usable = [p["value"] for p in posts if p["value"] is not None and not p["too_recent"]]
        med = median(usable) if usable else None
        notes = []
        if posts_per_account[acct] < TENTATIVE_POSTS:
            notes.append(f"TENTATIVE (account has {posts_per_account[acct]} posts < {TENTATIVE_POSTS})")
        if len(usable) < SMALL_GROUP:
            notes.append(f"small group (n={len(usable)} < {SMALL_GROUP})")
        if not usable:
            notes.append("no usable metric: qualitative only")
        print(f"{acct:28} {fmt:9} {len(posts):>5} {len(usable):>9} {fmt_num(med):>10}  {'; '.join(notes)}")
        for p in posts:
            if p["value"] is None:
                no_metric += 1
                continue
            if p["too_recent"]:
                recent += 1
                continue
            if med:
                x = p["value"] / med
                p["x"] = x
                if x >= OUTLIER_X:
                    outliers.append((acct, fmt, p))

    print(f"\n== Outliers (>= {OUTLIER_X:g}x own median, same format) ==")
    if not outliers:
        print("none")
    for acct, fmt, p in sorted(outliers, key=lambda t: -t[2]["x"]):
        print(f"{acct:28} {fmt:9} {p['kind']:15} {fmt_num(p['value']):>10}  {p['x']:.1f}x  {p['url']}")

    print(f"\nPosts with no usable metric (not available): {no_metric}")
    if args.min_age_days:
        print(f"Posts excluded as too recent (< {args.min_age_days} days): {recent}")
    print("Note: counts are parsed from displayed values (e.g. '12.3K'), so ratios carry display rounding.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
