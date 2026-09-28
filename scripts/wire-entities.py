#!/usr/bin/env python3
"""Wire generated entity pages into the site.

Usage: python3 scripts/wire-entities.py <data-file> <topic-label> [--pages p1,p2,...]

- links every entity name in the listed index pages to its own page
- appends the entities to a navbox topic in src/lib/nav-topics.ts

Linking is a single combined-regex pass per text node: replacements are never
rescanned, so a short name can no longer match inside the HTML just written for
a longer one.
"""
import json
import os
import re
import sys

PAGES = "src/data/pages"
NAV = "src/lib/nav-topics.ts"
DEFAULT_PAGES = [
    "Enemies", "enemy-weaknesses", "boss-guide", "boss-order", "bosses-by-area",
    "boss-drops", "walkthrough", "walkthrough-act-1", "trophy-guide",
    "side-quests", "interactive-map", "guide", "locations", "best-pictos",
    "weapons-locations", "weapons-tier-list", "best-weapons", "best-builds",
    "tier-list", "characters", "camp-guide", "damage-mechanics",
]

SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "code", "pre"}


def link_text(html, names, current_slug):
    tokens = re.split(r"(<[^>]+>)", html)
    stack = []
    out = []
    pattern = re.compile(
        r"(?<![>\w-])(" + "|".join(re.escape(n) for n, _ in names) + r")(?![\w-])",
        re.I,
    )
    lookup = {n.lower(): s for n, s in names}

    for token in tokens:
        if token.startswith("<"):
            m = re.match(r"<\s*(/?)\s*([a-zA-Z][\w]*)", token)
            if m:
                closing, tag = m.group(1) == "/", m.group(2).lower()
                if tag in SKIP_TAGS:
                    if closing:
                        if tag in stack:
                            stack.remove(tag)
                    elif not token.endswith("/>"):
                        stack.append(tag)
            out.append(token)
            continue

        if stack or not token.strip():
            out.append(token)
            continue

        def replace(match):
            slug = lookup[match.group(1).lower()]
            if slug == current_slug:
                return match.group(1)
            return (
                f'<a href="/{slug}" style="color:var(--accent);'
                f'text-decoration:underline;text-underline-offset:2px">{match.group(1)}</a>'
            )

        out.append(pattern.sub(replace, token))

    return "".join(out)


def wire_pages(records, page_list):
    names = sorted([(r["name"], r["slug"]) for r in records], key=lambda x: -len(x[0]))
    total = 0
    for page in page_list:
        path = os.path.join(PAGES, f"{page}.json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path))
        added = 0
        for section in data["sections"]:
            before = len(re.findall(r'href="/', section["content"]))
            section["content"] = link_text(section["content"], names, page)
            added += len(re.findall(r'href="/', section["content"])) - before
        if added:
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
            total += added
            print(f"  {page:22s} +{added}")
    return total


def wire_nav(records, label):
    src = open(NAV).read()
    entries = "".join(
        f'  {{ slug: "{r["slug"]}", title: "{r["name"]}" }},\n'
        for r in records
        if f'"{r["slug"]}"' not in src
    )
    if not entries:
        print(f"  nav-topics: {label} already complete")
        return 0

    if f'label: "{label}"' in src:
        s = src.index(f'label: "{label}"')
        arr_start = src.index("pages: [", s)
        close = src.index("]", arr_start)
        src = src[:close] + entries + "    " + src[close:]
    else:
        block = (
            "  {\n"
            f'    label: "{label}",\n'
            "    pages: [\n"
            + "".join("    " + line for line in entries.splitlines(True))
            + "    ],\n"
            "  },\n"
        )
        anchor = "export const TOPICS: NavTopic[] = [\n"
        src = src.replace(anchor, anchor + block)
    open(NAV, "w").write(src)
    return entries.count("slug")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)

    data_file, label = args[0], args[1]
    page_list = DEFAULT_PAGES
    if "--pages" in sys.argv:
        page_list = sys.argv[sys.argv.index("--pages") + 1].split(",")

    records = json.load(open(data_file))
    print(f"Wiring {len(records)} records as topic '{label}'")
    linked = wire_pages(records, page_list)
    added = wire_nav(records, label)
    print(f"\n{linked} internal links added, {added} nav entries added")


if __name__ == "__main__":
    main()
