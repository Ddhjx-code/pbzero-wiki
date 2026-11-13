#!/usr/bin/env python3
"""Build the summary pages that the entity data can support but nobody wrote.

Two pages come out of this:

  boss-order.json  - one table, all 60 encounters, in the order you meet them.
                     /boss-list groups by region and /bosses-by-class groups by
                     type, so neither answers "what order do I fight these in".

  locations.json   - the existing 544-word page gets the region tables it was
                     missing. It said "eight maps" and listed names in Chinese
                     but never showed region -> boss counts.

Both are generated from src/data/entities/bosses.json so the numbers cannot
drift away from the boss pages. Re-run after editing that file.
"""
import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENT = os.path.join(ROOT, "src/data/entities/bosses.json")
PAGES = os.path.join(ROOT, "src/data/pages")

LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'

# The order the game actually hands these to you. bosses.json is already
# stored in progression order; this list only names the blocks for prose.
BLOCK_NOTE = {
    "Prologue & Weeping Creek Valley": "Tutorial ground. The first duel teaches parry timing and cannot be lost.",
    "Crimson Manor & Crimson Forest": "First real difficulty step. Two acolytes and a secret boss hide here.",
    "Village of Lu": "Puppet-heavy. The well drops you into a story fight you cannot walk past.",
    "Pangzhen": "The hub. Most optional fights in the game branch off its bells.",
    "Mandate Encampment": "Story-dense, almost no optional content.",
    "Meigu Lake": "Optional-heavy. One fight here gates the true ending.",
    "Mountain of Imprisonment": "Story run with two shrine fights tucked in.",
    "Mirage Estate": "Short block, two story bosses and one optional.",
    "Mount Soulrend & endgame": "Point of no return. Optional fights left undone expire on the climb.",
}


def load_bosses():
    with open(ENT, encoding="utf-8") as fh:
        return json.load(fh)


def is_story(boss):
    return boss["kind"].startswith("Story")


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def boss_link(b):
    name = esc(b["name"])
    return f'<a href="/{b["slug"]}" {LINK}>{name}</a>'


def table(headers, rows):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def build_boss_order(bosses):
    total = len(bosses)
    story = [b for b in bosses if is_story(b)]
    optional = [b for b in bosses if not is_story(b)]
    blocks = OrderedDict()
    for b in bosses:
        blocks.setdefault(b["act"], []).append(b)

    rows = []
    for i, b in enumerate(bosses, 1):
        rows.append([i, boss_link(b), esc(b["kind"]), esc(b["act"]), esc(b["location"])])
    master = table(["#", "Boss", "Type", "Region", "Where you meet it"], rows)

    block_rows = []
    cursor = 1
    for name, group in blocks.items():
        s = sum(1 for b in group if is_story(b))
        span = f"{cursor}–{cursor + len(group) - 1}"
        block_rows.append([f'{cursor}–{cursor + len(group) - 1}', esc(name), s, len(group) - s])
        cursor += len(group)
    block_table = table(["Boss #", "Region", "Story", "Optional"], block_rows)

    optional_rows = []
    for b in optional:
        optional_rows.append([esc(b["name"]), esc(b["act"]), esc(b["location"])])
    optional_table = table(["Optional fight", "Region", "How it opens up"], optional_rows)

    sections = [
        {
            "id": "at-a-glance",
            "title": "Boss order at a glance",
            "content": (
                f"<p>Phantom Blade Zero has <strong>{total} named encounters</strong> once you count "
                f"optional and recurring fights: <strong>{len(story)} story bosses</strong> that gate the "
                f"story and <strong>{len(optional)} optional, recurring or rematch fights</strong>. "
                f"You cannot miss a story boss; you can very easily miss the optional ones, because several "
                f"expire at the Mount Soulrend climb.</p>"
                f"<p>The game is wide-linear rather than open world - each region is a hand-built map with a "
                f"story spine and optional branches hanging off its bells. That means the order below is not a "
                f"choice: region {len(blocks)} is the last one, and the four bosses before the credits are fixed. "
                f"What you actually decide is <em>when</em> to detour, since an optional boss you skip in "
                f"Pangzhen is usually still available later, while one you skip in Meigu Lake may not be.</p>"
                f"<p>If you want the short version: fight every story boss in the order it appears, and take the "
                f"optional fights in the region where you find them. The only optional encounter that is genuinely "
                f"worth planning around is Blizzard Blademaster, which gates a true-ending branch.</p>"
            ),
        },
        {
            "id": "full-order",
            "title": f"Full boss order - all {total}, in the order you meet them",
            "content": (
                f"<p>Numbered by progression, not by difficulty. Encounter names link to their own pages, which "
                f"carry the fight itself, the drops and whether the encounter can be missed.</p>{master}"
                f"<p>Rematches and recurring fights keep their own row because they behave differently from the "
                f"first meeting - The Gold-Masked One returns five times, and Yucong comes back later in the "
                f"story with a different move set.</p>"
            ),
        },
        {
            "id": "by-region",
            "title": "The same list, region by region",
            "content": (
                f"<p>Useful when you are standing in a region and want to know how much is left. The counts are "
                f"of the {total} entries above, so a region with a high optional count is one where you can "
                f"lose track of what you have already cleared.</p>{block_table}"
                f"<p>Pangzhen carries the most fights of any block, and Meigu Lake has five optional encounters "
                f"against a single story boss - which is why players routinely arrive at the endgame underlevelled "
                f"and over-supplied at the same time.</p>"
            ),
        },
        {
            "id": "optional",
            "title": "Every optional fight, and what opens it",
            "content": (
                f"<p>Optional encounters are not random wandering: each one is attached to a bell, a scarecrow, "
                f"a side route or a collectible gate. The table below is the unlock condition as recorded for "
                f"each fight.</p>{optional_table}"
                f"<p>Two of these are not really optional. Blizzard Blademaster sits inside the Illusion at "
                f"Whiteshadow's Fall and is one of the gates on the true ending, and The Gold-Masked One has to be "
                f"beaten five separate times at the Lóng Pillar trials before the chain counts as done.</p>"
            ),
        },
        {
            "id": "endgame",
            "title": "The last five, and where the credits actually fall",
            "content": (
                "<p>The endgame is fixed and short. Mount Soulrend is the point of no return: once you start the "
                "ascent, optional fights you left in earlier regions are gone, which is the single most common way "
                "people lose the true ending on a first run.</p>"
                "<p>Leng Tu and Herald of the Veil come first, then Meng Hua at the peak - and Meng Hua is a "
                "true-ending checkpoint rather than a required fight. Zuo Shang, The True Long is the final boss. "
                "If the true-ending conditions were met, The Last Battle triggers immediately after Zuo Shang "
                "without a return to the hub; if they were not, the game ends at Zuo Shang and The Last Battle "
                "stays unplayed for that save.</p>"
                "<p>Saw and the Crusher is the one optional encounter that sits after all of this, which makes it "
                "the last thing you can do in the game.</p>"
            ),
        },
        {
            "id": "method",
            "title": "How this list was built",
            "content": (
                "<p>Every entry comes from the site's boss database, which is the same source the individual boss "
                "pages render from, so the numbers here and the numbers on /boss-list come from one file rather "
                "than from two people counting separately.</p>"
                "<p>Two limits worth stating. First, the count of "
                f"{total} is a count of <em>entries</em>, not of unique characters: recurring fights and rematches "
                "are listed separately, and S-GAME's own public figure has been \"50 or more\" rather than an exact "
                "number. Second, phase counts and per-fight strategy are only recorded for a handful of encounters "
                "so far - where those fields are empty on a boss page it means the fight has not been documented "
                "here yet, not that the boss has no phases.</p>"
            ),
        },
    ]

    return {
        "title": f"Phantom Blade Zero Boss Order - All {total} Bosses in Progression Order",
        "description": (
            f"Every Phantom Blade Zero boss in the order you fight them: {total} encounters, "
            f"{len(story)} story and {len(optional)} optional, from the Zuo Shang prologue duel to the true-ending "
            f"finale on Mount Soulrend - with the region each one sits in and the unlock condition for every "
            f"optional fight."
        ),
        "keyword": (
            "phantom blade zero boss order, phantom blade zero bosses in order, phantom blade zero boss "
            "progression, how many bosses phantom blade zero, phantom blade zero first boss, "
            "phantom blade zero final boss"
        ),
        "facts": [
            {"label": "Total encounters", "value": f"{total} - {len(story)} story, {len(optional)} optional, recurring or rematch"},
            {"label": "Progression blocks", "value": f"{len(blocks)} - from the Weeping Creek Valley prologue to Mount Soulrend"},
            {"label": "First boss", "value": "Zuo Shang - a prologue duel that works as a tutorial"},
            {"label": "Final boss", "value": "Zuo Shang, The True Long - then The Last Battle on a true-ending run"},
            {"label": "Point of no return", "value": "The Mount Soulrend ascent - optional fights left undone expire here"},
            {"label": "Counting rule", "value": "Every entry in the boss database; rematches and recurring fights keep their own row"},
        ],
        "sections": sections,
        "lastUpdated": "2026-11-13",
    }


def build_locations(bosses):
    path = os.path.join(PAGES, "locations.json")
    with open(path, encoding="utf-8") as fh:
        page = json.load(fh)

    blocks = OrderedDict()
    for b in bosses:
        blocks.setdefault(b["act"], []).append(b)

    rows = []
    for name, group in blocks.items():
        story = sum(1 for b in group if is_story(b))
        named = ", ".join(boss_link(b) for b in group[:3])
        more = f" and {len(group) - 3} more" if len(group) > 3 else ""
        rows.append([esc(name), story, len(group) - story, named + more])
    region_table = table(["Region", "Story bosses", "Optional", "You will meet"], rows)

    order_rows = []
    cursor = 1
    for name, group in blocks.items():
        order_rows.append([
            f"{cursor}–{cursor + len(group) - 1}",
            esc(name),
            esc(BLOCK_NOTE.get(name, "")),
        ])
        cursor += len(group)
    order_table = table(["Boss #", "Region", "What this block is for"], order_rows)

    new_sections = [
        {
            "id": "regions-and-bosses",
            "title": "Every region, and what is actually in it",
            "content": (
                f"<p>Region names are the ones the boss data uses, which is also how the walkthrough and the boss "
                f"pages are grouped. Counts are encounters, not characters - a region with eight optional fights "
                f"does not mean eight strangers standing around.</p>{region_table}"
                f"<p>The imbalance is the point. Pangzhen carries {len(blocks['Pangzhen'])} encounters because it is "
                f"the hub players return to, while Mirage Estate carries {len(blocks['Mirage Estate'])} and is over "
                f"almost before it starts.</p>"
            ),
        },
        {
            "id": "region-order",
            "title": "The order you pass through them",
            "content": (
                f"<p>The regions are sequential, with light backtracking through bells rather than free travel "
                f"across the whole map. Numbering below follows the boss order, so you can tell at a glance how "
                f"much of the game is still ahead.</p>{order_table}"
                f"<p>Mount Soulrend is the point of no return - the ascent locks out optional content behind you, "
                f"which matters more for region completion percentage than for the story itself. See the "
                f'<a href="/boss-order" {LINK}>full boss order</a> for the encounter-by-encounter list.</p>'
            ),
        },
    ]

    # Insert directly after "The named regions" so the prose list is followed by
    # the tables instead of the reader hitting "Two official names" in between.
    idx = next(
        (i for i, s in enumerate(page["sections"]) if s["id"] == "regions"),
        len(page["sections"]) - 1,
    )
    page["sections"][idx + 1:idx + 1] = new_sections

    page["title"] = "Phantom Blade Zero Locations - Every Region, Map Order & Bosses"
    page["description"] = (
        "Phantom Blade Zero's regions in order, from Weeping Creek Valley to Mount Soulrend: how many story and "
        "optional bosses sit in each, what the bell network connects, and why it is wide-linear rather than open "
        "world."
    )
    page["keyword"] += (
        ", phantom blade zero regions in order, phantom blade zero how many areas, "
        "phantom blade zero wide linear"
    )
    page["lastUpdated"] = "2026-11-13"
    return page


def main():
    bosses = load_bosses()

    order = build_boss_order(bosses)
    with open(os.path.join(PAGES, "boss-order.json"), "w", encoding="utf-8") as fh:
        json.dump(order, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    loc = build_locations(bosses)
    with open(os.path.join(PAGES, "locations.json"), "w", encoding="utf-8") as fh:
        json.dump(loc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"boss-order.json: {len(order['sections'])} sections, {len(bosses)} rows")
    print(f"locations.json:  {len(loc['sections'])} sections")


if __name__ == "__main__":
    main()
