#!/usr/bin/env python3
"""Wire generated entity pages into the site.

Usage:
  python3 scripts/wire-entities.py src/data/entities/bosses.json --type boss
  python3 scripts/wire-entities.py <data-file> <topic-label> [--pages p1,p2,...]

With --type, the navbox topic and the host pages that should link the entity
names come from the table below, so launch day is one command per type instead
of a hand-tuned argument list. --type is also inferred from the data filename.

Linking is a single combined-regex pass per text node: replacements are never
rescanned, so a short name cannot match inside the HTML just written for a
longer one.
"""
import json
import os
import re
import sys

PAGES = "src/data/pages"
NAV = "src/lib/nav-topics.ts"

# Host pages per entity type. Only pages that exist in src/data/pages are wired;
# quests and trophies hubs are listed because they land on launch day, and are
# skipped silently until then.
TYPES = {
    "boss": {
        "label": "Bosses",
        "pages": ["boss-guide", "boss-video-guides", "guide", "faq", "release-date"],
    },
    "weapon": {
        "label": "Weapons",
        "pages": ["weapons", "combat", "guide", "faq", "difficulty-modes"],
    },
    "character": {
        "label": "Characters",
        "pages": ["characters", "protagonist", "guide", "faq", "endings"],
    },
    "quest": {
        "label": "Quests",
        "pages": ["quests", "guide", "how-long-to-beat", "faq", "endings"],
    },
    "trophy": {
        "label": "Trophies",
        "pages": ["trophies", "how-long-to-beat", "guide", "faq"],
    },
}

FILENAME_HINTS = {
    "boss": "boss",
    "bosses": "boss",
    "bosses-prelaunch": "boss",
    "weapon": "weapon",
    "weapons": "weapon",
    "character": "character",
    "characters": "character",
    "quest": "quest",
    "quests": "quest",
    "trophy": "trophy",
    "trophies": "trophy",
}

SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "code", "pre"}


def link_text(html, names, current_slug):
    """Linkify entity names outside tags we must not touch.

    Matching is case-sensitive on purpose: a proper noun like Soul must not
    capture the ordinary word soul in running prose.
    """
    tokens = re.split(r"(<[^>]+>)", html)
    stack = []
    out = []
    pattern = re.compile(
        r"(?<![>\w-])(" + "|".join(re.escape(n) for n, _ in names) + r")(?![\w-])"
    )
    lookup = {n: s for n, s in names}

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
            slug = lookup[match.group(1)]
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
            print(f"  {page:22s} - (页不存在，跳过)")
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
    src = open(NAV, encoding="utf-8").read()
    entries = "".join(
        f'  {{ slug: "{r["slug"]}", title: "{r["name"]}" }},\n'
        for r in records
        if f'"{r["slug"]}"' not in src
    )
    if not entries:
        print(f"  nav-topics: {label} 已完整")
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
        assert anchor in src, f"{NAV} 结构变化，找不到 TOPICS 锚点"
        src = src.replace(anchor, anchor + block)
    open(NAV, "w", encoding="utf-8").write(src)
    return entries.count("slug")


def infer_type(data_file):
    stem = os.path.basename(data_file)[:-5]
    return FILENAME_HINTS.get(stem)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)

    data_file = args[0]
    kind = None
    if "--type" in sys.argv:
        kind = sys.argv[sys.argv.index("--type") + 1]
        if kind not in TYPES:
            print(f"unknown --type {kind!r}; available: {', '.join(sorted(TYPES))}")
            sys.exit(1)
    else:
        kind = infer_type(data_file)

    if kind:
        label = TYPES[kind]["label"]
        default_pages = TYPES[kind]["pages"]
    elif len(args) >= 2:
        label = args[1]
        default_pages = []
        print("  (未识别类型，按传统模式使用显式参数)")
    else:
        print(__doc__)
        sys.exit(1)

    if len(args) >= 2 and "--type" not in sys.argv:
        label = args[1]
    if "--pages" in sys.argv:
        page_list = sys.argv[sys.argv.index("--pages") + 1].split(",")
    else:
        page_list = default_pages

    records = json.load(open(data_file, encoding="utf-8"))
    wired = [r for r in records if os.path.exists(os.path.join(PAGES, f'{r["slug"]}.json'))]
    missing_pages = [r["slug"] for r in records if r not in wired]
    if missing_pages:
        print(f"  跳过 {len(missing_pages)} 条未生成页面的记录（避免造出死链）: {missing_pages}")
    if not wired:
        print("没有可接入的记录，请先运行 gen-entity-pages.py")
        sys.exit(1)

    print(f"Wiring {len(wired)} records as topic '{label}' (type={kind or 'explicit'})")
    linked = wire_pages(wired, page_list)
    added = wire_nav(wired, label)
    print(f"\n{linked} internal links added, {added} nav entries added")


if __name__ == "__main__":
    main()
