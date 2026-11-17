#!/usr/bin/env python3
"""Generate src/data/pages/map.json.

The "phantom blade zero map" query (~1,000 US searches/month in October 2026) was
previously carried only by /locations, whose title says "Locations". Those are two
different intents: "map" is people asking whether the game has a map at all and how
big it is, "locations" is people asking which region comes next. This page answers
the first and hands off to the second.

The per-region weapon index is the part no other site has in table form: weapons.json
records where each blade is picked up, so grouping by region is a data view rather
than new claims. Nothing here is invented - counts are computed from
entities/bosses.json and entities/weapons.json at generation time.
"""
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENT = ROOT / "src" / "data" / "entities"
OUT = ROOT / "src" / "data" / "pages" / "map.json"

LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'

# Order is the boss order, which is also the order the game hands the maps to you.
# The fourth column is hand-written context, not a count.
REGIONS = [
    ("Prologue & Weeping Creek Valley", "1-7",
     "Tutorial ground. One short map, then the first real valley. Bells arrive here."),
    ("Crimson Manor & Crimson Forest", "8-15",
     "Two maps joined by a manor interior. The forest is where the minimap starts hiding things."),
    ("Village of Lu", "16-22",
     "Dense vertical map. Wells and rooftops connect areas the minimap does not draw."),
    ("Pangzhen", "23-33",
     "The hub map, and the largest. Most optional fights in the game branch off its bells."),
    ("Mandate Encampment", "34-39",
     "Story-dense and relatively flat. Almost no optional content off the main line."),
    ("Meigu Lake", "40-45",
     "Water map. Crossing by boat is a traversal method, not a loading screen."),
    ("Mountain of Imprisonment", "46-51",
     "Vertical prison map. Two shrine fights sit off the critical path."),
    ("Mirage Estate", "52-54",
     "Short late-game estate. Over almost before it starts."),
    ("Mount Soulrend & endgame", "55-60",
     "The climb. Point of no return for optional content behind you."),
]

# Weapons are attributed by the region name that appears in their "obtained" string.
WEAPON_REGION_ALIASES = {
    "Weeping Creek Valley": "Prologue & Weeping Creek Valley",
    "Crimson Forest": "Crimson Manor & Crimson Forest",
    "Crimson Manor": "Crimson Manor & Crimson Forest",
    "Village of Lu": "Village of Lu",
    "Pangzhen": "Pangzhen",
    "Mandate Encampment": "Mandate Encampment",
    "Meigu Lake": "Meigu Lake",
    "Mountain of Imprisonment": "Mountain of Imprisonment",
    "Mount Soulrend": "Mount Soulrend & endgame",
    "Mirage Estate": "Mirage Estate",
}


def a(href, text):
    return f'<a href="{href}" {LINK}>{text}</a>'


def main():
    bosses = json.loads((ENT / "bosses.json").read_text())
    weapons = json.loads((ENT / "weapons.json").read_text())

    by_region = OrderedDict((r[0], []) for r in REGIONS)
    for b in bosses:
        by_region.setdefault(b["region"], []).append(b)

    weapons_by_region = OrderedDict((r[0], []) for r in REGIONS)
    unplaced = []
    for w in weapons:
        obtained = w.get("obtained") or ""
        placed = False
        for alias, region in WEAPON_REGION_ALIASES.items():
            if alias.lower() in obtained.lower():
                weapons_by_region[region].append(w)
                placed = True
                break
        if not placed:
            unplaced.append(w)

    total_bosses = len(bosses)
    story = sum(1 for b in bosses if b["kind"].startswith("Story") or b["kind"] == "True ending only")
    optional = total_bosses - story
    weapon_count = len(weapons)
    placed_weapons = weapon_count - len(unplaced)

    # --- section 3: the region map table -------------------------------------
    rows = []
    for idx, (region, span, note) in enumerate(REGIONS, start=1):
        group = by_region[region]
        s = sum(1 for b in group if b["kind"].startswith("Story") or b["kind"] == "True ending only")
        o = len(group) - s
        wcount = len(weapons_by_region[region])
        rows.append(
            f"<tr><td>{idx}</td><td>{a('/locations', region)}</td><td>{span}</td>"
            f"<td>{s}</td><td>{o}</td><td>{wcount}</td><td>{note}</td></tr>"
        )
    region_table = (
        "<table><thead><tr><th>#</th><th>Region map</th><th>Boss #</th>"
        "<th>Story</th><th>Optional</th><th>Weapons</th><th>What the map is for</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )

    # --- section 5: weapons by region ---------------------------------------
    wblocks = []
    for region, _span, _note in REGIONS:
        ws = weapons_by_region[region]
        if not ws:
            continue
        items = "".join(
            f"<li>{a('/' + w['slug'], w['name'])} &mdash; {w['obtained']}</li>"
            for w in ws
        )
        wblocks.append(f"<h3>{region} ({len(ws)})</h3><ul>{items}</ul>")
    weapons_section = "".join(wblocks)

    facts = [
        {"label": "Region maps", "value": "9 blocks in the boss data; S-GAME's pre-launch copy says eight hand-painted maps"},
        {"label": "World map screen", "value": "None - the game has per-region maps, not one stitched map of the Wulin"},
        {"label": "Map type", "value": "Wide-linear: handcrafted regions joined seamlessly, not an open world"},
        {"label": "Fog of war", "value": "Cleared by touching bells, not by walking"},
        {"label": "Fast travel", "value": "Bells only, and only between bells you have already touched"},
        {"label": "Completion tracking", "value": "Per-map collectible total, pickup list and a percentage"},
        {"label": "Gated areas", "value": "Some require a specific Phantom Edge; the map marks which"},
        {"label": "Point of no return", "value": "The Mount Soulrend climb - optional content behind it expires"},
        {"label": "Interactive map", "value": "Not hosted here - see the comparison section for what each tool does"},
    ]

    sections = [
        {
            "id": "short-answer",
            "title": "Does Phantom Blade Zero Have a Map?",
            "content": (
                "<p>Yes, but not the kind the question usually means. Phantom Blade Zero has "
                "<strong>no world map screen</strong>: there is no single image of the Wulin you can zoom "
                "out to. What it has is one hand-painted ink-wash map per region, a minimap that fills in as "
                "you explore, and a bell network that acts as the fast-travel layer.</p>"
                "<p>So the three questions behind \"phantom blade zero map\" have three separate answers:</p>"
                "<ul>"
                "<li><strong>Is there a map?</strong> Yes - per region, with fog of war and a completion percentage.</li>"
                "<li><strong>Is it open world?</strong> No. S-GAME's own wording is that every corner is handcrafted and "
                "the game is neither open-world nor a straight line. Community documentation calls the structure "
                "wide-linear with light Metroidvania-style exploration.</li>"
                "<li><strong>How many maps?</strong> Nine region blocks in the boss data. Public counts vary between "
                "eight, nine and ten because sites disagree on whether Mirage Estate and the endgame count as their "
                "own regions. The table below uses the boss data's grouping so the counts reconcile with the "
                + a("/boss-list", "boss list") + " and the " + a("/boss-order", "boss order") + ".</li>"
                "</ul>"
                "<p>If what you actually want is the region-to-region progression order, "
                + a("/locations", "the locations page") + " covers that in narrative form. This page is about the "
                "map system itself: how big it is, how the bells work, what each map hides, and what locks when.</p>"
            ),
        },
        {
            "id": "map-size",
            "title": "How Big Is the Map?",
            "content": (
                f"<p>There is no square-kilometre figure, and any number quoted for one is an estimate. What can be "
                f"counted is what sits on the maps: <strong>{total_bosses} named encounters</strong> across nine region "
                f"blocks - <strong>{story} on the story path</strong> and <strong>{optional} optional, recurring or "
                f"rematch fights</strong> - plus <strong>{placed_weapons} weapons and Phantom Edges</strong> with a "
                f"recorded pickup location.</p>"
                "<p>The shape matters more than the size. Regions are joined seamlessly rather than through a level "
                "select, so the boundary between two maps is a corridor, not a menu. Backtracking is done through "
                "bells, which means the map is effectively a network of hubs rather than one continuous surface - "
                "and that is why per-map completion percentages exist at all.</p>"
                "<p>Two structural details decide how much of each map you will actually see. First, some areas need "
                "a particular Phantom Edge to reach, so a map can read 80% complete while a quarter of it is still "
                "physically closed to you. Second, bells clear fog <em>around the bell</em> rather than around you, "
                "so a map you have crossed twice can still have dark corners that no amount of walking fixes.</p>"
            ),
        },
        {
            "id": "region-maps",
            "title": "All Nine Region Maps, in Order",
            "content": (
                "<p>Counts are encounters, not characters - Pangzhen has eleven because it is the hub players return "
                "to, not because eleven strangers stand in the street. The weapons column counts blades and Phantom "
                "Edges whose recorded pickup names that region; the full per-weapon breakdown is "
                + a("#weapons-by-region", "further down this page") + ".</p>"
                + region_table
                + "<p>The boss-number ranges are the same ones used by the "
                + a("/boss-order", "boss order") + " page, so you can tell at a glance how much of the game is left "
                "when you enter a map. Region-by-region narrative - what the place is, who you meet, how the bells "
                "connect - is on " + a("/locations", "locations") + ".</p>"
            ),
        },
        {
            "id": "bells",
            "title": "The Bells Are the Map",
            "content": (
                "<p>Bells do four jobs, and only one of them is fast travel. Treating them as waypoints undersells "
                "the system and is why people finish a region at 70% and cannot work out what they missed.</p>"
                "<ol>"
                "<li><strong>Fog reveal.</strong> The first touch clears the minimap around that bell. Walking past a "
                "dark area does not reveal it - the bell does.</li>"
                "<li><strong>Fast travel.</strong> Travel runs between bells you have already touched. There is no "
                "free travel across the whole map, which is what keeps the wide-linear structure from behaving like "
                "an open world.</li>"
                "<li><strong>Restock.</strong> Combat resources refresh at bells, the same way a bonfire or a lantern "
                "does in the games this one is inevitably compared to.</li>"
                "<li><strong>Gating.</strong> Some fights are built into the travel network itself - forced-combat "
                "waypoints you cannot walk around. A bell that will not let you leave until a fight ends is not a "
                "bug.</li>"
                "</ol>"
                "<p>Water travel exists as a second traversal method in at least one region; the boat crossing on "
                "Meigu Lake is part of the map, not a cutscene. The " + a("/collectibles", "collectibles page")
                + " covers what the bells are worth in completion terms.</p>"
            ),
        },
        {
            "id": "weapons-by-region",
            "title": "Weapons by Region - What Each Map Hides",
            "content": (
                f"<p>{placed_weapons} of the {weapon_count} documented weapons and Phantom Edges have a pickup "
                "location that names a region, so they can be filed by map. The remaining "
                f"{len(unplaced)} are story rewards, tempering upgrades or boss drops, and are listed on "
                + a("/blades", "blades") + " and " + a("/phantom-edges", "Phantom Edges") + " instead.</p>"
                "<p>Read this as a per-map shopping list: if you are about to leave a region, this is what is still "
                "reachable behind you. Names in Chinese are kept where that is the only recorded name.</p>"
                + weapons_section
                + "<p>Pickups gated behind a specific Phantom Edge are marked on the in-game map, which is the one "
                "place the map screen is genuinely helpful - it tells you a thing exists before you can reach it.</p>"
            ),
        },
        {
            "id": "completion",
            "title": "Map Completion: What the Percentage Counts",
            "content": (
                "<p>Each map tracks three things: the total number of collectibles in it, the specific pickups you "
                "have and have not taken, and a completion percentage. The categories that count are special items "
                "(Sha-chi Amber shards, Black Stone shards, Memory Flowers), books and story items. Weapons, flasks, "
                "accessories and Remnant Spark are equipment or currency and do not move the number.</p>"
                "<p>That split is why a map can sit at 95% with nothing visibly left. The usual culprits, in order of "
                "how often they are the answer:</p>"
                "<ul>"
                "<li>A bell you touched but never searched around - the fog is gone, the pickup is not.</li>"
                "<li>An area behind a Phantom Edge you have not found yet, so the map still marks it as locked.</li>"
                "<li>An optional fight whose arena held a story item, and the fight expired at the climb.</li>"
                "</ul>"
                "<p>The three permanent upgrades are worth chasing for their own sake: Sha-chi Amber raises the "
                "Sha-chi bar cap, Black Stone raises attack and poise-break, Memory Flowers raise maximum health. "
                "Exact totals per map are not published anywhere, including here - the in-game counter is the only "
                "authority.</p>"
            ),
        },
        {
            "id": "point-of-no-return",
            "title": "What Locks at Mount Soulrend",
            "content": (
                "<p>Mount Soulrend is the point of no return, and it locks optional content rather than story. "
                "Anything still open behind you - optional fights, their drops, side tales - expires on the climb. "
                "For the story itself nothing is lost; for a 100% run the last region is where you either did the "
                "work or did not.</p>"
                "<p>Practical order for a completion run: finish Pangzhen's optional fights before leaving it (it "
                "carries the most), do Meigu Lake's optional block because one fight there gates the true ending, "
                "and check the " + a("/missable", "missables page") + " before starting the ascent. The "
                + a("/trophy-guide", "trophy guide") + " lists which trophies sit behind that gate.</p>"
            ),
        },
        {
            "id": "interactive-maps",
            "title": "Interactive Maps vs This Page",
            "content": (
                "<p>If you want to pixel-hunt a single chest, an interactive map with pins is the right tool - "
                "MapGenie, the Fextralife map and the Game8 map all do that, and this site does not host one. "
                "What an interactive map does not do is tell you the order to do things in, which is what this "
                "page and " + a("/boss-order", "boss order") + " are for.</p>"
                "<table><thead><tr><th>You want</th><th>Use</th></tr></thead><tbody>"
                "<tr><td>The exact spot of one collectible</td><td>An interactive map with pins</td></tr>"
                "<tr><td>Whether the game has a map at all, and how the maps work</td><td>This page</td></tr>"
                "<tr><td>Which region comes next and what is in it</td><td>" + a("/locations", "Locations") + "</td></tr>"
                "<tr><td>Encounter-by-encounter order, including optionals</td><td>" + a("/boss-order", "Boss order") + "</td></tr>"
                "<tr><td>What expires if you climb now</td><td>" + a("/missable", "Missables") + "</td></tr>"
                "</tbody></table>"
                "<p>One caveat about every map you will find, ours included: the pre-launch build and the release "
                "build do not have identical map boundaries, so older pin sets occasionally place a pickup in a "
                "region that no longer starts there.</p>"
            ),
        },
    ]

    page = {
        "slug": "map",
        "title": "Phantom Blade Zero Map - 9 Region Maps, Bells & Completion",
        "description": (
            "No world map screen - nine hand-painted region maps instead, bells for fast travel and fog reveal, "
            "and a completion percentage per map. What each one hides."
        ),
        "keyword": (
            "phantom blade zero map, phantom blade zero map size, phantom blade zero world map, "
            "phantom blade zero is it open world, phantom blade zero maps in order, phantom blade zero fast travel, "
            "phantom blade zero map completion"
        ),
        "lastUpdated": "2026-11-17",
        "facts": facts,
        "sections": sections,
    }

    OUT.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n")
    words = sum(len(re.sub(r"<[^>]+>", " ", s["content"]).split()) for s in sections)
    print(f"wrote {OUT.relative_to(ROOT)}  sections={len(sections)}  words≈{words}")
    print(f"  bosses={total_bosses} story={story} optional={optional} weapons placed={placed_weapons}/{weapon_count}")


if __name__ == "__main__":
    main()
