#!/usr/bin/env python3
"""Link every name in the /boss-list roster tables to its entity page.

The tier-2 index has to point at the tier-3 pages, otherwise the entity pages are
orphans that only the sitemap knows about. Names are matched exactly against
`src/data/entities/bosses.json`, and cells that already contain a link are left
alone, so running this twice is safe.
"""
import json
import os
import re

ENTITIES = "src/data/entities/bosses.json"
PAGE = "src/data/pages/boss-list.json"


def main():
    records = json.load(open(ENTITIES, encoding="utf-8"))
    by_name = {r["name"]: r["slug"] for r in records}
    page = json.load(open(PAGE, encoding="utf-8"))

    linked = 0
    for section in page["sections"]:
        content = section.get("content", "")
        if "<table" not in content:
            continue

        def fix_row(match):
            nonlocal linked
            row = match.group(0)
            cell = re.match(r"(<tr>\s*)<td>(.*?)</td>", row, re.S)
            if not cell:
                return row
            inner = cell.group(2)
            if "<a " in inner:
                return row
            name = re.sub(r"<[^>]+>", "", inner).strip()
            slug = by_name.get(name)
            if not slug:
                return row
            linked += 1
            return f'{cell.group(1)}<td><a href="/{slug}">{inner}</a></td>' + row[cell.end():]

        section["content"] = re.sub(r"<tr>.*?</tr>", fix_row, content, flags=re.S)

    json.dump(page, open(PAGE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    total = len(records)
    print(f"{linked}/{total} roster rows linked to entity pages")

    missing = [r["name"] for r in records if r["name"] not in json.dumps(page, ensure_ascii=False)]
    if missing:
        print("  not present in the roster table:", ", ".join(missing))


if __name__ == "__main__":
    main()
