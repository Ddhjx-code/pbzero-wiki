#!/usr/bin/env python3
"""Add the Mirage Estate roster to /boss-list.

The eight regions the page shipped with skip Mirage Estate entirely, which left
Lei Dang, Qiu Feng and Mo Yuan without a row. This inserts the missing section in
campaign order (after the Mountain of Imprisonment, before Mount Soulrend) and is
idempotent - running it twice does not duplicate the table.
"""
import json

PAGE = "src/data/pages/boss-list.json"
TITLE = "Mirage Estate"

ROWS = [
    ("Lei Dang", "Story", "Mirage Estate", "Tiger Cannon"),
    ("Qiu Feng, the Crimson Boneblade (赤骨刀 邱风)", "Story", "Mirage Estate", "Not documented"),
    ("Mo Yuan (莫渊)", "Optional", "Mirage Estate", "Soul Tempering material"),
]


def build_table(rows):
    head = "<table><thead><tr><th>Boss</th><th>Type</th><th>Where</th><th>Drop</th></tr></thead><tbody>"
    body = "".join(
        f"<tr><td>{n}</td><td>{k}</td><td>{w}</td><td>{d}</td></tr>" for n, k, w, d in rows
    )
    return head + body + "</tbody></table>"


def main():
    page = json.load(open(PAGE, encoding="utf-8"))
    sections = page["sections"]
    if any(s["title"] == TITLE for s in sections):
        print("Mirage Estate already present, nothing to do")
        return

    intro = (
        "<p>Mirage Estate sits between the Mountain of Imprisonment and the Mount Soulrend "
        "climb. It is the region most often left out of published rosters, which is why the "
        "boss count in circulation drifts between 50 and 62.</p>"
    )
    note = (
        "<p>Lei Dang is the only required fight here and is the source of the Tiger Cannon. "
        "Mo Yuan is optional and tied to Soul Tempering materials rather than a weapon drop, "
        "so skipping him costs upgrades rather than story.</p>"
    )
    new = [
        {"id": "mirage-estate", "title": TITLE, "content": intro + build_table(ROWS) + note}
    ]

    order = [s["id"] for s in sections]
    anchor = order.index("mount-soulrend-endgame") if "mount-soulrend-endgame" in order else len(sections) - 4
    sections[anchor:anchor] = new

    # Refresh the headline count so the page does not claim the old total.
    for s in sections:
        if s["id"] == "short-answer":
            s["content"] = s["content"].replace("56 bosses", "59 bosses").replace("56 ", "59 ")
        if s["id"] == "how-many-bosses-really":
            s["content"] = s["content"].replace("56", "59")

    page["lastUpdated"] = "2026-11-10"
    json.dump(page, open(PAGE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"inserted {TITLE} with {len(ROWS)} bosses at index {anchor}; total sections {len(sections)}")


if __name__ == "__main__":
    main()
