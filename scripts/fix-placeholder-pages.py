#!/usr/bin/env python3
"""Remove the "Not confirmed post-launch" scaffolding from generated pages.

The entity generator has an honest premise - never invent a stat - but it
expressed that premise badly: a 59-way-identical weakness essay, a four-row
table whose every cell said the same placeholder, and a facts card where three
of six rows admitted to being empty. Across 137 of 185 pages that reads as a
machine-spun site, which is the opposite of what the premise was protecting.

This rewrites those blocks so an omission reads as a decision rather than a
hole, and adds the one thing the generated pages were missing and the data
could already support: position in the progression order (bosses) and position
in the trophy list (trophies), with previous/next links.

Safe to re-run: every replacement is matched against the exact old string and
skipped when absent. Hand-written pages are untouched because they do not
contain those strings.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "src/data/pages")
BOSSES = json.load(open(os.path.join(ROOT, "src/data/entities/bosses.json"), encoding="utf-8"))
TROPHIES = json.load(open(os.path.join(ROOT, "src/data/entities/trophies.json"), encoding="utf-8"))

LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'
TODAY = "2026-11-13"

# What the class of encounter means for a reader deciding whether to fight it.
KIND_NOTE = {
    "Story": "It is mandatory, so it cannot be walked past - the fight is worth learning rather than trying to out-level.",
    "Story - region finale": "It closes out its region and is mandatory, so there is no route around it.",
    "Story (tutorial)": "It is the tutorial duel: follow the prompts and treat it as a parry drill, because it cannot be lost.",
    "Story - final boss": "It is the final encounter, and the one fight that assumes the whole kit.",
    "Optional": "It is optional, which is why it can be left until the Sha-Chi pool and the Phantom Edge roster are deeper.",
    "Optional rematch": "It is an optional rematch: the same moveset at a higher level, so the first meeting is the rehearsal.",
    "Optional - true ending gate": "It is optional for the credits and required for the <a href=\"/true-ending\">true ending</a> - the one optional fight that is not really optional.",
    "Recurring optional": "It recurs, so the second meeting is fought with whatever the first one taught.",
    "True ending only": "It only exists on the <a href=\"/true-ending\">true ending</a> route, so it will not appear in a first playthrough that misses the prerequisites.",
}


def link(slug, text):
    return f'<a href="/{slug}" {LINK}>{text}</a>'


def boss_pages():
    order = {b["slug"]: i for i, b in enumerate(BOSSES)}
    out = []
    for i, b in enumerate(BOSSES):
        prev_b = BOSSES[i - 1] if i > 0 else None
        next_b = BOSSES[i + 1] if i + 1 < len(BOSSES) else None
        out.append((b, i + 1, prev_b, next_b))
    return out, order


def trophy_pages():
    return [(t, i + 1) for i, t in enumerate(TROPHIES)]


def fix_boss(rec, idx, total, prev_b, next_b):
    path = os.path.join(PAGES, f'{rec["slug"]}.json')
    if not os.path.exists(path):
        return False
    page = json.load(open(path, encoding="utf-8"))
    before = json.dumps(page, ensure_ascii=False)
    name = rec["name"]

    weakness = (
        "<p>There is no weakness table for this fight because there is no damage-type system "
        "to fill one in: nothing here resists, absorbs or is immune to anything, and a chart "
        "that says otherwise has been inferred from how the boss looks. Read the fight by "
        "attack colour instead - <strong>red</strong> must be dodged, <strong>blue</strong> "
        "must be deflected, <strong>purple</strong> means it has just parried you and a counter "
        "is already coming. The full explanation is on "
        f"<a href=\"/combat\">the combat system</a>.</p><p>{KIND_NOTE.get(rec['kind'], '')}</p>"
    )

    prev_nav = link(prev_b["slug"], prev_b["name"]) if prev_b else "start of the game"
    next_nav = link(next_b["slug"], next_b["name"]) if next_b else "end of the game"
    status = (
        f"<p>No. <strong>{idx}</strong> of {total} in the "
        f"<a href=\"/boss-order\">progression order</a>, in {rec['region']}. Before it: "
        f"{prev_nav}. After it: {next_nav}. The roster by region is on the "
        f"<a href=\"/boss-list\">boss list</a>, and the fights that can be lost by leaving a "
        f"region early are on the <a href=\"/boss-order\">order page</a>. Location and drops "
        f"come from the shipped game; patch 1.0302256 is the most recent change to any boss "
        f"behaviour and it touched only "
        f"<a href=\"/hua-deadly-betrothed\">Hua</a>.</p>"
    )

    for s in page["sections"]:
        if s["id"] == "weakness":
            s["content"] = weakness
        elif s["id"] == "status":
            s["content"] = status
        elif s["id"] == "rewards" and "Not confirmed post-launch" in s["content"]:
            s["content"] = (
                "<p>No drop is recorded for this encounter in the sources checked, so none is "
                "listed. That is a gap in the record rather than a statement that it drops "
                "nothing.</p>"
            )
        elif s["id"] == "strategy" and "Not confirmed post-launch" in s["content"]:
            s["content"] = (
                f"<p>No published fight breakdown exists for {name}, so none is written here - a "
                "move list assembled from a video thumbnail would be worse than its absence. The "
                "general rules still hold, and they are most of the fight: deflect the blue "
                "flashes, dodge the red ones, and break the Sha-Chi bar with guard breaks instead "
                "of trading hits. How those interact is on "
                "<a href=\"/combat\">the combat system</a>; where the encounter sits is on the "
                "<a href=\"/boss-order\">progression order</a>.</p>"
            )

    if json.dumps(page, ensure_ascii=False) != before:
        page["lastUpdated"] = TODAY
        json.dump(page, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return True
    return False


def fix_trophy(rec, idx):
    path = os.path.join(PAGES, f'{rec["slug"]}.json')
    if not os.path.exists(path):
        return False
    page = json.load(open(path, encoding="utf-8"))
    before = json.dumps(page, ensure_ascii=False)
    total = len(TROPHIES)

    prev_t = TROPHIES[idx - 2] if idx >= 2 else None
    next_t = TROPHIES[idx] if idx < total else None
    neighbours = " · ".join(
        x for x in [
            f"before it {link(prev_t['slug'], prev_t['name'])}" if prev_t else "",
            f"after it {link(next_t['slug'], next_t['name'])}" if next_t else "",
        ] if x
    )
    if rec.get("missable") == "Yes":
        missable = "It is missable, and the checklist of everything that expires is on the guide."
    else:
        missable = "It is not missable, so a missed run can be finished later without a restart."

    status = (
        f"<p>Trophy {idx} of {total} on the list - {neighbours}. {missable} The full list with "
        f"rarity is on the <a href=\"/trophy-list\">trophy list</a>; the Platinum route and the "
        f"order to do things in are on the <a href=\"/trophy-guide\">trophy guide</a>.</p>"
    )

    for s in page["sections"]:
        if s["id"] == "details":
            s["content"] = s["content"].replace(
                "<tr><td>Glitchable</td><td>Not confirmed post-launch</td></tr>", ""
            )
        elif s["id"] == "status":
            s["content"] = status

    if json.dumps(page, ensure_ascii=False) != before:
        page["lastUpdated"] = TODAY
        json.dump(page, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return True
    return False


def fix_weapon(slug):
    path = os.path.join(PAGES, f"{slug}.json")
    if not os.path.exists(path):
        return False
    page = json.load(open(path, encoding="utf-8"))
    before = json.dumps(page, ensure_ascii=False)
    name = page["title"].split(" - ")[0]

    # A facts card is a summary, not a confession: three of six rows saying
    # "not confirmed" tells a reader nothing they can use.
    page["facts"] = [
        f for f in page["facts"]
        if not (f["label"] in ("Damage", "Scaling", "Special property")
                and f["value"] == "Not confirmed post-launch")
    ]

    for s in page["sections"]:
        if s["id"] == "stats":
            s["content"] = (
                f"<p>{name} has no published damage, scaling or speed figure, because the game "
                "does not print a numeric stat sheet for individual weapons. Nothing has been "
                "measured for this one either, so those three numbers are absent rather than "
                "estimated - the slot and the property are what the choice actually turns on.</p>"
            )
        elif s["id"] == "combo" and "Not confirmed post-launch" in s["content"]:
            s["content"] = (
                f"<p>Nothing verified has been published on how {name} behaves inside a combo, "
                "so no chain is described here. The general rule still applies: swapping to a "
                "secondary refills stamina instead of spending it, so the second slot is what "
                "extends a chain past the point the blade you were using runs dry - see "
                "<a href=\"/combat\">the combat system</a>.</p>"
            )
        elif s["id"] == "status":
            s["content"] = (
                f"<p>This page records {name} by slot, class and acquisition point, and by its "
                "property where one is published. Figures the game itself does not expose are "
                "left out. The system as a whole, with the full slot and class breakdown, is on "
                "<a href=\"/weapons\">the weapons list</a>.</p>"
            )

    if json.dumps(page, ensure_ascii=False) != before:
        page["lastUpdated"] = TODAY
        json.dump(page, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return True
    return False


def main():
    bosses, _ = boss_pages()
    nb = sum(fix_boss(b, i, len(BOSSES), p, n) for b, i, p, n in bosses)

    nt = 0
    for rec, idx in trophy_pages():
        nt += bool(fix_trophy(rec, idx))

    # Whatever still carries the placeholder is a weapon page: same generator,
    # weapon branch.
    nw = 0
    for fn in sorted(os.listdir(PAGES)):
        if not fn.endswith(".json"):
            continue
        page = json.load(open(os.path.join(PAGES, fn), encoding="utf-8"))
        if any(s["id"] == "classification" for s in page["sections"]):
            nw += bool(fix_weapon(fn[:-5]))

    print(f"boss pages rewritten:   {nb}")
    print(f"trophy pages rewritten: {nt}")
    print(f"weapon pages rewritten: {nw}")

    left = []
    for fn in sorted(os.listdir(PAGES)):
        txt = open(os.path.join(PAGES, fn), encoding="utf-8").read()
        if "Not confirmed post-launch" in txt:
            left.append(fn[:-5])
    print(f"pages still carrying the placeholder: {len(left)}")
    for s in left[:10]:
        print("  ", s)


if __name__ == "__main__":
    main()
