"""Regenerate tier-2 category index pages from src/data/entities/*.json.

Huiji rule: an index page is never hand-maintained, because a hand-maintained
list is always out of date. The roster tables below are rebuilt from the entity
data on every run, so adding a weapon or boss updates every index that lists it.

Run after any entity rebuild:
    python3 scripts/gen-index-pages.py
"""

import json
import os
import sys

ENTITIES = "src/data/entities"
PAGES = "src/data/pages"
UPDATED = "2026-11-10"
L = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'


def load(name):
    path = os.path.join(ENTITIES, f"{name}.json")
    if not os.path.exists(path):
        return []
    return json.load(open(path, encoding="utf-8"))


def row(cells):
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"


def table(headers, records, project):
    """project(rec) -> list of cell values. Empty state is explicit, not silent."""
    if not records:
        return (
            "<p>No entries have been recorded yet. This table is generated from "
            "<code>src/data/entities/</code>, so it fills itself as each entity is verified "
            "against the shipped game - nothing here is hand-typed and nothing is estimated.</p>"
        )
    body = "".join(row(project(r)) for r in sorted(records, key=lambda x: x["name"]))
    return (
        "<table><thead><tr>"
        + "".join(f"<th>{h}</th>" for h in headers)
        + "</tr></thead><tbody>"
        + body
        + "</tbody></table>"
    )


def link(rec, label=None):
    return f'<a href="/{rec["slug"]}" {L}>{label or rec["name"]}</a>'


def write_page(page):
    slug = page["slug"]
    path = os.path.join(PAGES, f"{slug}.json")
    existing = {}
    if os.path.exists(path):
        existing = json.load(open(path, encoding="utf-8"))
    # Preserve hand-authored sections the generator does not own.
    generated_ids = {s["id"] for s in page["sections"]}
    kept = [s for s in existing.get("sections", []) if s["id"] not in generated_ids]
    order = {sid: i for i, sid in enumerate(page["section_order"])}
    merged = page["sections"] + kept
    merged.sort(key=lambda x: order.get(x["id"], len(order)))
    page["sections"] = merged
    json.dump(page, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return slug


# ---------------------------------------------------------------- weapons


def build_blades():
    weapons = load("weapons")
    blades = [w for w in weapons if w.get("slot") == "Primary"]
    order = ["One-handed", "Dual-wield", "Two-handed"]

    groups = ""
    for cls in order:
        subset = [w for w in blades if w.get("category") == cls]
        if not subset:
            continue
        groups += f"<h3>{cls} ({len(subset)})</h3>" + table(
            ["Blade", "How to obtain", "Property"],
            subset,
            lambda w: [
                link(w),
                w.get("obtained", "Not recorded"),
                w.get("property") or "-",
            ],
        )

    return {
        "slug": "blades",
        "title": f"Blades in Phantom Blade Zero - the {len(blades)} With a Recorded Location",
        "description": (
            f"All {len(blades)} blades in Phantom Blade Zero, grouped by one-handed, dual-wield and "
            "two-handed, with where each one is found and what its property does. Every entry "
            "links to its own page."
        ),
        "keyword": "phantom blade zero blades, primary weapons phantom blade zero, all weapons list",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Slot", "value": "Primary"},
            {"label": "Carried at once", "value": "2"},
            {"label": "Records with a location", "value": str(len(blades))},
            {"label": "Official total", "value": "More than 30 (August 2026 deep dive)"},
            {"label": "Counterpart", "value": "Phantom Edges"},
            {"label": "Swap effect", "value": "Refills stamina"},
        ],
        "section_order": ["overview", "list", "swap", "acquisition", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "What Blades Are",
                "content": (
                    "<p>Blades are the <strong>primary</strong> weapon class in Phantom Blade Zero. "
                    "Soul carries <strong>two of them at the same time</strong>, alongside two "
                    '<a href="/phantom-edges">Phantom Edges</a> in the secondary slots - a 2 + 2 '
                    "loadout rather than one weapon plus an off-hand.</p>"
                    f"<p>This page lists the <strong>{len(blades)} blades</strong> that have a "
                    "recorded acquisition point, split across three families: one-handed, dual-wield "
                    "and two-handed. S-GAME put the shipped total at more than 30, so this is not the "
                    "whole roster - it is the part a source ties to a location, which is the only part "
                    "you can act on.</p>"
                    "<p>The family split is the actual choice, because reach, speed and guard-break "
                    "trade against each other through the weapon rather than through a stat line.</p>"
                ),
            },
            {
                "id": "list",
                "title": f"The {len(blades)} Recorded Blades",
                "content": groups,
            },
            {
                "id": "swap",
                "title": "Why Switching Matters More Than Which Blade",
                "content": (
                    "<p>Switching weapons <strong>refills stamina immediately</strong> and lets a combo "
                    "continue. That single mechanic is why the combat reads closer to "
                    "<em>Ninja Gaiden</em> than to a FromSoftware fight: the aggressive line is "
                    "sustainable because the resource comes back on the swap.</p>"
                    '<p><a href="/combat">Sha-chi</a> is a separate pool, spent on heavy attacks and '
                    "on blocking. Because both spend it, blocking everything runs the resource dry at "
                    "the worst moment.</p>"
                ),
            },
            {
                "id": "acquisition",
                "title": "How Blades Are Obtained",
                "content": (
                    "<p>Three routes cover almost the whole list. <strong>Boss drops</strong> are the "
                    "largest group - the game gives you the weapon of the thing that killed you. "
                    "<strong>World pickups</strong> hang off bells and outposts and are the ones people "
                    "walk past. <strong>Tempering</strong> converts Sanguine and Sanguine Reach into "
                    "their upgraded forms, which is why the starting blade is not a throwaway.</p>"
                    '<p>The weapon-by-weapon table is on <a href="/weapons">the weapons hub</a>.</p>'
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>This is a tier-2 index: it aggregates the blade entries generated from "
                    "<code>src/data/entities/weapons.json</code>. See "
                    '<a href="/weapons">the weapons hub</a> for the system as a whole and '
                    '<a href="/phantom-edges">Phantom Edges</a> for the secondary slot.</p>'
                ),
            },
        ],
    }


def build_phantom_edges():
    weapons = load("weapons")
    edges = [w for w in weapons if w.get("slot") != "Primary"]
    return {
        "slug": "phantom-edges",
        "title": f"Phantom Edges in Phantom Blade Zero - the {len(edges)} With a Recorded Location",
        "description": (
            f"All {len(edges)} Phantom Edges in Phantom Blade Zero - cannons, spears, axes and "
            "instruments rather than more swords - with where each is found and how they pair with "
            "blades."
        ),
        "keyword": "phantom edge phantom blade zero, secondary weapons phantom blade zero, all phantom edges",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Slot", "value": "Secondary"},
            {"label": "Carried at once", "value": "2"},
            {"label": "Records with a location", "value": str(len(edges))},
            {"label": "Official total", "value": "Around 25 (August 2026 deep dive)"},
            {"label": "Counterpart", "value": "Blades"},
        ],
        "section_order": ["overview", "list", "roster-cn", "types", "pairing", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "What Phantom Edges Are",
                "content": (
                    "<p>Phantom Edges occupy Soul's <strong>two secondary weapon slots</strong>. The "
                    "set is deliberately ungovernable - <strong>cannons, spears, shields, bows and an "
                    "instrument</strong> - which is a long way from a standard sword list. The word "
                    "&ldquo;Edge&rdquo; in the name is doing conceptual work rather than literal work: "
                    "several of them are not blades at all.</p>"
                    f"<p><strong>{len(edges)} Phantom Edges</strong> have a recorded acquisition "
                    "point, against an official total of around 25. "
                    "They cover problems a blade build cannot - range, reach, and a couple of utility "
                    "answers like thread-cutting - which is why a loadout is a choice about "
                    "<em>which situations you can handle</em> rather than a damage comparison.</p>"
                ),
            },
            {
                "id": "list",
                "title": f"The {len(edges)} Recorded Phantom Edges",
                "content": table(
                    ["Phantom Edge", "Type", "How to obtain"],
                    edges,
                    lambda w: [
                        link(w),
                        w.get("category", "Not stated"),
                        w.get("obtained", "Not recorded"),
                    ],
                ),
            },
            {
                "id": "types",
                "title": "The Types, and Why They Exist",
                "content": (
                    "<p>Types are read off the item name where the name states one; the rest are "
                    "marked &ldquo;not stated&rdquo; rather than inferred from a screenshot.</p>"
                    "<ul><li><strong>Cannons and bows</strong> - the ranged answer. Tiger Cannon is a "
                    "boss drop, Feather Bow is an early outpost pickup.</li>"
                    "<li><strong>Spears and tridents</strong> - reach on a melee weapon.</li>"
                    "<li><strong>Axes and polearms</strong> - slow, heavy, guard-breaking.</li>"
                    "<li><strong>Throwing blades</strong> - Flying Dagger and Flying Guillotine, both "
                    "cheap to get and easy to forget to equip.</li>"
                    "<li><strong>The pipa</strong> - an instrument, and the only entry whose attacks "
                    "are not obviously strikes.</li></ul>"
                ),
            },
            {
                "id": "roster-cn",
                "title": "How Many Phantom Edges Are There, Really?",
                "content": (
                    "<p>Two numbers circulate and they are not the same number. The launch "
                    f"acquisition table behind this page records <strong>{len(edges)}</strong>. The "
                    "Chinese BWIKI catalogue that predates release listed 33 names, splitting them "
                    "into 23 it considered confirmed and 10 it could not place - and warned in "
                    "writing that some of the unplaced names were not official at all.</p>"
                    "<p>Neither number is a mistake. The BWIKI list is a name catalogue collected "
                    "before release, so it includes entries that were cut, renamed or never shipped. "
                    "This page lists what a named source ties to an acquisition point, because a name "
                    "with no location cannot be found in the game. If a missing edge turns up with a "
                    "verified route, it is one record in "
                    "<code>src/data/entities/weapons.json</code> and it appears here on the next "
                    "build.</p>"
                ),
            },
            {
                "id": "pairing",
                "title": "Pairing With Blades",
                "content": (
                    '<p>Two <a href="/blades">blades</a> plus two Phantom Edges, all four live during '
                    "a fight. Swapping between them refills stamina and continues the combo chain, so a "
                    "run is normally built around which two edges cover what the blades cannot.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/weapons.json</code>. "
                    'See <a href="/weapons">the weapons hub</a>.</p>'
                ),
            },
        ],
    }


# ---------------------------------------------------------------- bosses


def bucket(kind):
    k = kind.lower()
    if k.startswith("story"):
        return "Story"
    if k.startswith("optional") or k.startswith("recurring"):
        return "Optional"
    return "True ending only"


def build_bosses_by_class():
    bosses = load("bosses")
    groups = {}
    for b in bosses:
        groups.setdefault(bucket(b["kind"]), []).append(b)

    blurbs = {
        "Story": "Fights the campaign puts in front of you. Most boss trophies sit here.",
        "Optional": (
            "Fights you can walk past - and the reason a full run takes 40 hours instead of 20. "
            "Several carry trophies, weapons or true-ending requirements."
        ),
        "True ending only": "Encounters that exist only on the true-ending route.",
    }

    blocks = ""
    for name in ("Story", "Optional", "True ending only"):
        subset = groups.get(name, [])
        if not subset:
            continue
        blocks += f"<h3>{name} ({len(subset)})</h3><p>{blurbs[name]}</p>" + table(
            ["Boss", "Region", "Drop"],
            subset,
            lambda b: [
                link(b),
                b.get("region", "Not recorded"),
                ", ".join(b.get("drops", [])) or "-",
            ],
        )

    return {
        "slug": "bosses-by-class",
        "title": f"Phantom Blade Zero Bosses by Class - {len(bosses)} Story and Optional Fights",
        "description": (
            f"All {len(bosses)} bosses in Phantom Blade Zero sorted by whether the story forces the "
            "fight or you can walk past it, with region and drop for each. Every name links to its "
            "own page."
        ),
        "keyword": "phantom blade zero all bosses, story bosses, optional bosses, boss list",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Total encounters", "value": str(len(bosses))},
            {"label": "Story", "value": str(len(groups.get("Story", [])))},
            {"label": "Optional", "value": str(len(groups.get("Optional", [])))},
            {"label": "True ending only", "value": str(len(groups.get("True ending only", [])))},
        ],
        "section_order": ["overview", "classes", "why", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "How This Split Works",
                "content": (
                    f"<p>Phantom Blade Zero has <strong>{len(bosses)} recorded encounters</strong>. "
                    "The split below is not cosmetic: story fights come to you, optional fights do "
                    "not, and the difference between a 20-hour run and a 40-hour one is almost "
                    "entirely optional fights.</p>"
                    "<p>Class is taken from the encounter's role in the campaign, not from difficulty. "
                    "An optional fight can be harder than a story one - see the "
                    '<a href="/boss-guide">boss guide</a> for the colour tells that decide both.</p>'
                ),
            },
            {"id": "classes", "title": "The Full Roster, by Class", "content": blocks},
            {
                "id": "why",
                "title": "Why the Optional Fights Matter",
                "content": (
                    "<p>Optional bosses are where the weapons are. Thirty-seven of the sixty "
                    "encounters drop something, and the optional half of that list is where the "
                    "distinctive builds live - the paired blades, the leg-mounted saws, the "
                    "instrument.</p>"
                    "<p>They are also where the missable trophies are. Anything that can expire is "
                    'listed on <a href="/missable">the missable page</a>, and the drops are '
                    'collected on <a href="/boss-drops">what bosses drop</a>.</p>'
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/bosses.json</code>. "
                    'The region-by-region version is <a href="/boss-list">the boss list</a>.</p>'
                ),
            },
        ],
    }


def build_boss_drops():
    bosses = load("bosses")
    with_drops = [b for b in bosses if b.get("drops")]
    no_drop = [b for b in bosses if not b.get("drops")]

    return {
        "slug": "boss-drops",
        "title": "Phantom Blade Zero Boss Drops - Every Weapon and Where It Comes From",
        "description": (
            f"What each of Phantom Blade Zero's {len(with_drops)} dropping bosses gives you, with "
            "the boss page linked both ways so you can work from the weapon or the fight. Bosses "
            "with no recorded drop are listed too, rather than left out."
        ),
        "keyword": "phantom blade zero boss drops, boss rewards, weapon drops",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Bosses listed", "value": str(len(bosses))},
            {"label": "With a recorded drop", "value": str(len(with_drops))},
            {"label": "Without one", "value": str(len(no_drop))},
        ],
        "section_order": ["overview", "table", "none", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "Bosses Drop Their Own Weapon",
                "content": (
                    "<p>Phantom Blade Zero follows one rule almost without exception: the boss you "
                    "just beat was using the weapon it hands you. Bi Feng gives up the Juggernaut, "
                    "Cavalrybane gives up Armybreaker, Peng Meng gives up the Dread Axe.</p>"
                    "<p>That makes the drop table a weapon acquisition list in disguise, and it "
                    "explains why the fastest route to a specific build is a specific fight rather "
                    'than a specific shop. The item-first view is <a href="/weapons">the weapons '
                    "hub</a>; this page is the fight-first view.</p>"
                ),
            },
            {
                "id": "table",
                "title": "Every Recorded Drop",
                "content": table(
                    ["Boss", "Region", "Drop"],
                    with_drops,
                    lambda b: [
                        link(b),
                        b.get("region", "Not recorded"),
                        ", ".join(b["drops"]),
                    ],
                ),
            },
            {
                "id": "none",
                "title": "Bosses With No Recorded Drop",
                "content": (
                    "<p>These fights are recorded without a distinct reward. That is not a claim "
                    "that they drop nothing - it means no guide we checked names an item, so none is "
                    "listed.</p>"
                    + table(
                        ["Boss", "Region", "Class"],
                        no_drop,
                        lambda b: [link(b), b.get("region", "Not recorded"), b["kind"]],
                    )
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/bosses.json</code>. "
                    'See <a href="/bosses-by-class">bosses by class</a> for the story-versus-optional '
                    'split, and <a href="/boss-list">the boss list</a> for the region-by-region '
                    "version.</p>"
                ),
            },
        ],
    }


# ---------------------------------------------------------------- trophies


def build_trophies():
    trophies = load("trophies")
    tiers = ["Platinum", "Gold", "Silver", "Bronze"]
    blocks = ""
    for tier in tiers:
        subset = [t for t in trophies if t.get("rarity") == tier]
        if not subset:
            continue
        blocks += f"<h3>{tier} ({len(subset)})</h3>" + table(
            ["Trophy", "How to earn it", "Missable"],
            subset,
            lambda t: [link(t), t.get("how", "Not recorded"), t.get("missable", "-")],
        )

    missable = [t for t in trophies if t.get("missable") == "Yes"]
    return {
        "slug": "trophy-list",
        "title": f"Phantom Blade Zero Trophy List - All {len(trophies)} PS5 Trophies",
        "description": (
            f"Every trophy in Phantom Blade Zero by tier - {len(trophies)} in total - with what each "
            "one wants and whether it can be lost. Each entry links to its own page."
        ),
        "keyword": "phantom blade zero trophy list, all trophies, ps5 trophies, achievements",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Total", "value": str(len(trophies))},
            {"label": "Platinum", "value": str(len([t for t in trophies if t.get("rarity") == "Platinum"]))},
            {"label": "Gold", "value": str(len([t for t in trophies if t.get("rarity") == "Gold"]))},
            {"label": "Silver", "value": str(len([t for t in trophies if t.get("rarity") == "Silver"]))},
            {"label": "Bronze", "value": str(len([t for t in trophies if t.get("rarity") == "Bronze"]))},
            {"label": "Missable", "value": str(len(missable))},
        ],
        "section_order": ["overview", "platinum", "missable", "count", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "The Full List, by Tier",
                "content": (
                    f"<p>Phantom Blade Zero has <strong>{len(trophies)} trophies</strong> on PS5: one "
                    "platinum, three gold, fourteen silver and eighteen bronze. Nothing is gated "
                    "behind a difficulty setting, and the director confirmed every trophy can be "
                    "earned in a single playthrough - which makes this a list about not missing "
                    "content rather than about skill.</p>"
                    "<p>Tiers for the grouped boss trophies are disputed between sources; the split "
                    "below follows the four lists that agree, and "
                    '<a href="/trophy-guide">the trophy guide</a> records where they diverge.</p>'
                ),
            },
            {"id": "platinum", "title": "Every Trophy", "content": blocks},
            {
                "id": "missable",
                "title": "The Ten That Can Be Lost",
                "content": (
                    f"<p><strong>{len(missable)}</strong> entries can become unobtainable, and the "
                    "game does not warn you when a window closes. Nine are side-quest completions and "
                    "one is an optional boss.</p>"
                    + table(
                        ["Trophy", "How to earn it"],
                        missable,
                        lambda t: [link(t), t.get("how", "Not recorded")],
                    )
                    + "<p>The safe rule is to clear every side quest in a region before pushing the "
                    'main story past it. <a href="/missable">The missable page</a> covers content '
                    "rather than trophies.</p>"
                ),
            },
            {
                "id": "count",
                "title": "Where the Lists Disagree",
                "content": (
                    "<p>Four sources agree on 36 with a 1 / 3 / 14 / 18 split. Fextralife lists 66 "
                    "for the combined PS5-and-PC set with a 1 / 3 / 22 / 40 split, which is the "
                    "Steam-style count rather than a contradiction.</p>"
                    "<p>Two smaller disputes are recorded rather than resolved. Game8 lists a silver "
                    "called <em>Unsung Legend</em> for completing the Enemy Journal where the other "
                    "lists carry <em>Collector's Notes</em> for 30 accessories - the likeliest "
                    "explanation is that the platform lists differ, not that one source is wrong. And "
                    "Game8 marks 13 trophies hidden while the Chinese list marks more; only the 13 "
                    "both support are labelled hidden on this site.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/trophies.json</code>. "
                    'The route order is on <a href="/trophy-guide">the trophy guide</a>.</p>'
                ),
            },
        ],
    }


# ---------------------------------------------------------------- characters


def build_npcs():
    chars = load("characters")
    npcs = [c for c in chars if c.get("playable") is False]
    return {
        "slug": "npcs",
        "title": "Phantom Blade Zero NPCs - Non-Playable Characters",
        "description": (
            "Every recorded non-playable character in Phantom Blade Zero. The game is single-player "
            "and Soul is the only character you control, so the rest of the cast are NPCs."
        ),
        "keyword": "phantom blade zero npcs, phantom blade zero characters list",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Playable characters", "value": "1 - Soul only"},
            {"label": "Recorded NPCs", "value": str(len(npcs)) or "Not catalogued yet"},
            {"label": "Mode", "value": "Single-player"},
        ],
        "section_order": ["overview", "list", "confusion", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "Who Is on This List",
                "content": (
                    "<p>Phantom Blade Zero is single-player and <strong>Soul is the only playable "
                    "character</strong>. Everyone else in the cast is an NPC, including the characters "
                    "that are playable in S-Game's mobile entries.</p>"
                ),
            },
            {
                "id": "list",
                "title": "Recorded NPCs",
                "content": table(
                    ["Character", "Role", "Portrayed by"],
                    npcs,
                    lambda c: [
                        link(c),
                        c.get("role", "Not recorded"),
                        c.get("portrayed_by", "Not recorded"),
                    ],
                ),
            },
            {
                "id": "confusion",
                "title": "Why This Distinction Exists",
                "content": (
                    "<p>An earlier wave of pre-launch write-ups listed four playable characters for "
                    "this game - Soul, Mu Xiaokui, Zuo Shang and <em>The Chord</em>. That roster belongs "
                    "to S-Game's mobile entries, where those names are playable together. It was never "
                    "announced for Phantom Blade Zero.</p>"
                    "<p>The likeliest source of the confusion is the music: composer Caisheng Bo "
                    "confirmed that Soul, Mu Xiaokui and Zuoshang each have their own thematic melody, "
                    "all descended from the same A minor theme. Three leitmotifs reads like three "
                    "playable characters. It is not. See "
                    '<a href="/is-phantom-blade-zero-single-player">is Phantom Blade Zero '
                    "single-player</a>.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/characters.json</code>. "
                    'The narrative cast is described on <a href="/characters">characters</a>; the '
                    'protagonist has his own page at <a href="/protagonist">Soul</a>. The boss cast '
                    'lives on <a href="/boss-list">the boss list</a>, because they are fights rather '
                    "than NPCs.</p>"
                ),
            },
        ],
    }


def main():
    if not os.path.isdir(PAGES):
        print("run from the repo root")
        sys.exit(1)
    pages = [
        build_blades(),
        build_phantom_edges(),
        build_bosses_by_class(),
        build_boss_drops(),
        build_trophies(),
        build_npcs(),
    ]
    built = [write_page(p) for p in pages]
    print(f"regenerated {len(built)} tier-2 index pages: {', '.join(built)}")
    print(
        f"  entity rows available: weapons={len(load('weapons'))} "
        f"bosses={len(load('bosses'))} characters={len(load('characters'))}"
    )


if __name__ == "__main__":
    main()
