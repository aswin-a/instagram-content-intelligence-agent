#!/usr/bin/env python3
"""Repo checks: SKILL.md frontmatter, relative links (and #anchors), schema <-> CSV header drift.

Standard library only. Exit code 1 if anything fails.
Usage: python3 scripts/check_repo.py
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
errors = []


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    out = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        key, sep, val = line.partition(":")
        if not sep or line.startswith((" ", "\t")):
            errors.append(f"frontmatter line not a simple 'key: value': {line!r}")
            continue
        out[key.strip()] = val.strip()
    return out


def check_skills():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for path in skills:
        rel = path.relative_to(ROOT)
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rel}: missing or unterminated frontmatter")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{rel}: invalid name {name!r}")
        if name != path.parent.name:
            errors.append(f"{rel}: name {name!r} != directory {path.parent.name!r}")
        if not desc or len(desc) > 1024:
            errors.append(f"{rel}: description empty or > 1024 chars ({len(desc)})")
        if "use when" not in desc.lower() and "use on" not in desc.lower():
            errors.append(f"{rel}: description doesn't say when to use it")
        extra = set(fm) - ALLOWED_KEYS
        if extra:
            errors.append(f"{rel}: unexpected frontmatter keys {sorted(extra)}")
        body = path.read_text(encoding="utf-8")
        for section in ("## Inputs", "## Outputs", "## Stop conditions"):
            if section not in body:
                errors.append(f"{rel}: missing section '{section}'")
        print(f"  ok  {rel}: name={name}, description={len(desc)} chars")
    return len(skills)


def slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md_path):
    text = re.sub(r"```.*?```", "", md_path.read_text(encoding="utf-8"), flags=re.S)
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", text, flags=re.M)}


def check_links():
    count = 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z]+:", target):
                continue  # http(s), mailto
            count += 1
            path_part, _, frag = target.partition("#")
            dest = (md.parent / path_part).resolve() if path_part else md
            rel = md.relative_to(ROOT)
            if not dest.exists():
                errors.append(f"{rel}: broken link -> {target}")
            elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                errors.append(f"{rel}: missing anchor -> {target}")
    return count


def schema_fields(md_path):
    fields, in_table = [], False
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Field |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            cell = line.split("|")[1].strip()
            if set(cell) <= set("-: "):
                continue
            fields.append(cell.strip("`*"))
    return fields


def check_schemas():
    pairs = [("post-record.md", "post-record.template.csv"), ("idea-record.md", "idea-record.template.csv")]
    for md, csv_name in pairs:
        fields = schema_fields(ROOT / "schemas" / md)
        with open(ROOT / "schemas" / csv_name, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        if fields != header:
            errors.append(f"schemas/{md} fields != schemas/{csv_name} header\n    md:  {fields}\n    csv: {header}")
        else:
            print(f"  ok  schemas/{md} matches {csv_name} ({len(header)} fields)")


def main():
    print("SKILL.md frontmatter:")
    n_skills = check_skills()
    print("Schemas:")
    check_schemas()
    n_links = check_links()
    print(f"Relative links checked: {n_links}")
    if errors:
        print(f"\nFAIL ({len(errors)}):")
        for e in errors:
            print("  - " + e)
        return 1
    print(f"\nPASS: {n_skills} skills, {n_links} links, 2 schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
