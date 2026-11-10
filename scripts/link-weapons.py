#!/usr/bin/env python3
"""Wire the weapon entity pages into the pages that already mention them.

Three passes, each idempotent:
  1. /weapons  - the acquisition table gets a link on every weapon name.
  2. weapon pages - a boss drop gains a link back to the boss that drops it.
  3. boss pages - the rewards list gains a link to the weapon's own page.

Matching is by name, so a drop that has no weapon entity is left as plain text
rather than pointed at a guess.

Usage: python3 scripts/link-weapons.py
"""
import json
import os
import re

PAGES = "src/data/pages"
ENTITIES = "src/data/entities"
L = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'


def bare(name):
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def load(name):
    return json.load(open(os.path.join(ENTITIES, f"{name}.json"), encoding="utf-8"))


def main():
    weapons = load("weapons")
    bosses = load("bosses")

    by_name = {bare(w["name"]): w["slug"] for w in weapons}
    by_slug = {w["slug"]: w for w in weapons}

    # name fragment -> boss slug, for "defeat X" acquisition cells
    def boss_for(text):
        low = text.lower()
        for b in bosses:
            stem = bare(b["name"]).lower()
            head = stem.split(",")[0].strip()
            if head and head in low:
                return b
        return None

    linked_table = linked_back = linked_drop = 0

    # 1) /weapons acquisition table
    path = os.path.join(PAGES, "weapons.json")
    page = json.load(open(path, encoding="utf-8"))
    for section in page["sections"]:
        if section["id"] != "every-weapon-and-where-to-find-it":
            continue
        for name, slug in by_name.items():
            # Blade table cells wrap the name in <strong>; edge table cells do not.
            cell = re.search(
                rf"<td><strong>({re.escape(name)}(?:\s*\([^)]*\))?)</strong></td>",
                section["content"],
            )
            if cell:
                section["content"] = section["content"].replace(
                    cell.group(0),
                    f'<td><strong><a href="/{slug}" {L}>{cell.group(1)}</a></strong></td>',
                    1,
                )
                linked_table += 1
        for name, slug in by_name.items():
            if f'href="/{slug}"' in section["content"]:
                continue
            cell = re.search(rf"<td>({re.escape(name)}(?:\s*\([^)]*\))?)</td>", section["content"])
            if cell:
                section["content"] = section["content"].replace(
                    cell.group(0), f'<td><a href="/{slug}" {L}>{cell.group(1)}</a></td>', 1
                )
                linked_table += 1
    json.dump(page, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 2) weapon page -> the boss that drops it
    for slug, w in by_slug.items():
        path = os.path.join(PAGES, f"{slug}.json")
        if not os.path.exists(path):
            continue
        d = json.load(open(path, encoding="utf-8"))
        obtained = w.get("obtained", "")
        target = boss_for(obtained)
        if not target:
            continue
        for section in d["sections"]:
            if section["id"] != "acquisition":
                continue
            if f'href="/{target["slug"]}"' in section["content"]:
                break
            extra = (
                f'<p>Dropped by <a href="/{target["slug"]}">{bare(target["name"])}</a> - '
                "see that page for the fight itself, and "
                '<a href="/boss-drops">boss drops</a> for the reverse list.</p>'
            )
            section["content"] = section["content"].replace(
                "</p>", "</p>" + extra, 1
            ) if "</p>" in section["content"] else section["content"] + extra
            linked_back += 1
            break
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 3) boss page rewards -> weapon page
    for b in bosses:
        path = os.path.join(PAGES, f'{b["slug"]}.json')
        if not os.path.exists(path):
            continue
        d = json.load(open(path, encoding="utf-8"))
        for section in d["sections"]:
            if section["id"] != "rewards":
                continue
            content = section["content"]
            for item in b.get("drops", []):
                for piece in [p.strip() for p in item.split(",") if p.strip()]:
                    slug = by_name.get(bare(piece))
                    if not slug or f'href="/{slug}"' in content:
                        continue
                    old = f"<li>{piece}</li>"
                    if old in content:
                        content = content.replace(
                            old, f'<li><a href="/{slug}" {L}>{piece}</a></li>', 1
                        )
                        linked_drop += 1
            section["content"] = content
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"weapons table links: {linked_table}")
    print(f"weapon -> boss links: {linked_back}")
    print(f"boss -> weapon links: {linked_drop}")


if __name__ == "__main__":
    main()
