"""Generate src/data/pages/news.json from src/data/news.json.

The news file is the source of truth; the page is derived, so adding a dated
entry and rerunning this keeps the feed and the guide in step. Each entry lists
the wiki pages it changed under `affects`, and this script refuses to write when
one of those slugs does not exist - a changelog pointing at a page that was never
built is worse than no changelog.

    python3 scripts/gen-news-page.py
"""

from __future__ import annotations

import json
import os
import re
import sys

DATA = os.path.join("src", "data", "news.json")
OUT = os.path.join("src", "data", "pages", "news.json")
PAGES = os.path.join("src", "data", "pages")

STATUS_LABEL = {
    "confirmed": "Confirmed",
    "corrected": "Corrects earlier info on this site",
    "unconfirmed": "Unconfirmed",
    "reported": "Press-reported, not confirmed by the publisher",
}


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")[:40]


def para(text: str) -> str:
    return f"<p>{text}</p>"


def main() -> int:
    news = json.load(open(DATA, encoding="utf-8"))
    # Newest first regardless of how the data file was edited.
    entries = sorted(news["entries"], key=lambda e: e["date"], reverse=True)
    pages = {f[:-5] for f in os.listdir(PAGES) if f.endswith(".json")}

    broken = sorted(
        {a for e in entries for a in e.get("affects", []) if a != "autolink" and a not in pages}
    )
    if broken:
        for slug in broken:
            print(f"  affects 引用了不存在的页面: /{slug}", file=sys.stderr)
        return 1

    sections = [
        {
            "id": "overview",
            "title": "What this page tracks",
            "content": (
                "<p>Official Phantom Blade Zero news, newest first, each entry dated and attributed. "
                "Before the game released on 29 October 2026 the useful question was usually what had "
                "<em>not</em> been confirmed yet, so every entry is marked "
                f"{STATUS_LABEL['confirmed'].lower()}, "
                f"{STATUS_LABEL['corrected'].lower()}, "
                f"{STATUS_LABEL['reported'].lower()} or "
                f"{STATUS_LABEL['unconfirmed'].lower()} rather than presented as settled. "
                f"&quot;Press-reported&quot; means one or more outlets stated it but the publisher has not "
                f"confirmed it; &quot;Unconfirmed&quot; means we found no source at all.</p>"
                + para(
                    "Where the guide pages on this site disagreed with newer information, the newer "
                    "information won and the entry says so. The affected pages are linked at the end "
                    "of each item."
                )
                + para(news["note"])
            ),
        }
    ]

    for e in entries:
        items = "".join(f"<li>{f}</li>" for f in e["facts"])
        affects = [a for a in e.get("affects", []) if a != "autolink"]
        links = (
            " · ".join(f'<a href="/{a}">{a.replace("-", " ").title()}</a>' for a in affects)
            if affects
            else "no guide page changed"
        )
        sections.append(
            {
                "id": f"{e['date']}-{slugify(e['title'])}",
                "title": f"{e['date']} — {e['title']}",
                "content": (
                    f'<p class="text-sm text-amber-400">{STATUS_LABEL[e["status"]]}</p>'
                    + para(e["summary"])
                    + f"<ul>{items}</ul>"
                    + f'<p class="text-sm">Source: <a href="{e["url"]}" rel="noopener nofollow" '
                    f'target="_blank">{e["source"]}</a></p>'
                    + f'<p class="text-sm">Updates: {links}</p>'
                ),
            }
        )

    corrections = [e for e in entries if e["status"] == "corrected"]
    rows = "".join(
        f"<tr><td>{e['date']}</td><td>{e['title']}</td></tr>" for e in corrections
    )
    sections.append(
        {
            "id": "corrections",
            "title": "Corrections applied to this wiki",
            "content": (
                "<p>Items where this site had published something that newer sourcing contradicted, "
                "and the guide page has been rewritten to match.</p>"
                + (f"<table><thead><tr><th>Date</th><th>Correction</th></tr></thead><tbody>{rows}</tbody></table>" if rows else para("None yet."))
            ),
        }
    )

    page = {
        "title": "Phantom Blade Zero News & Official Updates",
        "description": (
            "Dated, sourced Phantom Blade Zero news before the 29 October 2026 release: difficulty modes, "
            "weapon totals, demo status, pre-order editions and PC details, with the guide pages each item changed."
        ),
        "keyword": "phantom blade zero news, phantom blade zero updates, pbz announcement, phantom blade zero release news",
        "lastUpdated": news["updated"],
        "facts": [
            {"label": "Game", "value": "Phantom Blade Zero"},
            {"label": "Developer", "value": "S-Game"},
            {"label": "Publisher", "value": "Kepler Interactive"},
            {"label": "Release date", "value": "October 29, 2026 (Oct 28 in US and select regions)"},
            {"label": "Platforms", "value": "PlayStation 5, PC (Steam, Epic Games Store)"},
            {"label": "Entries tracked", "value": str(len(entries))},
            {"label": "Last news update", "value": news["updated"]},
        ],
        "sections": sections,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(page, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(
        f"wrote {OUT}: {len(entries)} entries, {len(sections)} sections, "
        f"{len(corrections)} correction(s), all affects-links resolve"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
