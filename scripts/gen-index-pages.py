"""Regenerate tier-2 category index pages from src/data/entities/*.json.

Huiji rule: an index page is never hand-maintained, because a hand-maintained
list is always out of date. The roster tables below are rebuilt from the entity
data on every run, so adding a weapon or character updates every index that
lists it.

Usage: python3 scripts/gen-index-pages.py
"""

import json
import os
import re
import sys

ENTITIES = "src/data/entities"
PAGES = "src/data/pages"
UPDATED = "2026-10-10"


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
            "<p>No entries have been confirmed yet. This table is generated from "
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


def build_blades():
    weapons = load("weapons")
    blades = [w for w in weapons if "primar" in str(w.get("slot", "")).lower()
              or "blade" in str(w.get("category", "")).lower()]
    return {
        "slug": "blades",
        "title": "Blades in Phantom Blade Zero - Primary Weapon List",
        "description": (
            "Blades are Phantom Blade Zero's primary weapons - Soul carries two at once. What is "
            "confirmed about the class, the full list of blades as it is verified, and how they "
            "interact with Phantom Edges."
        ),
        "keyword": "phantom blade zero blades, primary weapons phantom blade zero",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Slot", "value": "Primary"},
            {"label": "Carried at once", "value": "2"},
            {"label": "Counterpart", "value": "Phantom Edges"},
            {"label": "Swap effect", "value": "Refills stamina"},
            {"label": "Named blades", "value": "Not confirmed pre-launch"},
        ],
        "section_order": ["overview", "list", "swap", "acquisition", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "What Blades Are",
                "content": (
                    "<p>Blades are the <strong>primary</strong> weapon class in Phantom Blade Zero. "
                    "Soul carries <strong>two of them at the same time</strong>, alongside two "
                    "<a href=\"/phantom-edges\">Phantom Edges</a> in the secondary slots - a 2 + 2 "
                    "loadout rather than one weapon plus an off-hand.</p>"
                    "<p>Individual blade names, damage values and move sets have not been published. "
                    "The demo build showed a pair of short swords together with a longer katana-class "
                    "weapon, which is the shape of the choice: reach and speed trade against each other "
                    "through the weapon itself, not through a stat line.</p>"
                ),
            },
            {
                "id": "list",
                "title": "Blade List",
                "content": table(
                    ["Blade", "Class", "Damage", "How to obtain"],
                    blades,
                    lambda w: [
                        f'<a href="/{w["slug"]}">{w["name"]}</a>',
                        w.get("category", "Not confirmed"),
                        w.get("damage", "Not confirmed"),
                        w.get("obtained", "Not confirmed"),
                    ],
                ),
            },
            {
                "id": "swap",
                "title": "Why Switching Matters More Than Which Blade",
                "content": (
                    "<p>Switching weapons <strong>refills stamina immediately</strong> and lets a combo "
                    "continue. That single mechanic is why the combat reads closer to "
                    "<em>Ninja Gaiden</em> than to a FromSoftware fight: the aggressive line is "
                    "sustainable because the resource comes back on the swap.</p>"
                    "<p><a href=\"/combat\">Sha-chi</a> is a separate pool, spent on heavy attacks and "
                    "on blocking. Because both spend it, blocking everything runs the resource dry at "
                    "the worst moment.</p>"
                ),
            },
            {
                "id": "acquisition",
                "title": "How Blades Are Obtained",
                "content": (
                    "<p>S-GAME describes boss kills as rewarding unique weapons, which is the strongest "
                    "published hint about where the roster lives. No drop table exists yet, so no "
                    "acquisition route is asserted for any individual blade.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>This is a tier-2 index: it aggregates the blade entries generated from "
                    "<code>src/data/entities/weapons.json</code>. See "
                    "<a href=\"/weapons\">the weapons hub</a> for the system as a whole.</p>"
                ),
            },
        ],
    }


def build_phantom_edges():
    weapons = load("weapons")
    edges = [w for w in weapons if "secondar" in str(w.get("slot", "")).lower()
             or "phantom" in str(w.get("category", "")).lower()]
    return {
        "slug": "phantom-edges",
        "title": "Phantom Edges in Phantom Blade Zero - Secondary Weapon List",
        "description": (
            "Phantom Edges are Phantom Blade Zero's secondary weapons - cannons, lances, axes and "
            "hammers rather than more swords. What is confirmed, the list as it is verified, and how "
            "they pair with blades."
        ),
        "keyword": "phantom edge phantom blade zero, secondary weapons phantom blade zero",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Slot", "value": "Secondary"},
            {"label": "Carried at once", "value": "2"},
            {"label": "Counterpart", "value": "Blades"},
            {"label": "Confirmed example types", "value": "Cannons, lances, axes, hammers"},
            {"label": "Named edges", "value": "Not confirmed pre-launch"},
        ],
        "section_order": ["overview", "list", "types", "pairing", "status"],
        "sections": [
            {
                "id": "overview",
                "title": "What Phantom Edges Are",
                "content": (
                    "<p>Phantom Edges occupy Soul's <strong>two secondary weapon slots</strong>. The "
                    "confirmed example set is deliberately ungovernable - <strong>cannons, lances, axes "
                    "and hammers</strong> - which is a long way from a standard sword list. The word "
                    "&ldquo;Edge&rdquo; in the name is doing conceptual work rather than literal work: "
                    "several of them are not blades at all.</p>"
                ),
            },
            {
                "id": "list",
                "title": "Phantom Edge List",
                "content": table(
                    ["Phantom Edge", "Type", "Damage", "How to obtain"],
                    edges,
                    lambda w: [
                        f'<a href="/{w["slug"]}">{w["name"]}</a>',
                        w.get("category", "Not confirmed"),
                        w.get("damage", "Not confirmed"),
                        w.get("obtained", "Not confirmed"),
                    ],
                ),
            },
            {
                "id": "types",
                "title": "The Confirmed Types",
                "content": (
                    "<p>Ranged and reach-extreme weapons cover problems a blade build cannot, which is "
                    "why a loadout is a choice about <em>which situations you can handle</em> rather "
                    "than a damage comparison. The four types named in published material:</p>"
                    "<ul><li><strong>Cannons</strong> - ranged fire, the only confirmed option that "
                    "engages from distance.</li>"
                    "<li><strong>Lances</strong> - long reach on a melee weapon.</li>"
                    "<li><strong>Axes</strong> - slow, heavy hits.</li>"
                    "<li><strong>Hammers</strong> - slow, heavy hits with a different guard-break "
                    "profile.</li></ul>"
                    "<p>Counts, names and stats for individual Phantom Edges are unpublished.</p>"
                ),
            },
            {
                "id": "pairing",
                "title": "Pairing With Blades",
                "content": (
                    "<p>Two <a href=\"/blades\">blades</a> plus two Phantom Edges, all four live during "
                    "a fight. Swapping between them refills stamina and continues the combo chain, so a "
                    "run is normally built around which two edges cover what the blades cannot.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/weapons.json</code>. "
                    "See <a href=\"/weapons\">the weapons hub</a>.</p>"
                ),
            },
        ],
    }


def build_npcs():
    chars = load("characters")
    npcs = [c for c in chars if c.get("playable") is False]
    return {
        "slug": "npcs",
        "title": "Phantom Blade Zero NPCs - Non-Playable Characters",
        "description": (
            "Every confirmed non-playable character in Phantom Blade Zero. The game is single-player "
            "and Soul is the only character you control, so the rest of the cast are NPCs."
        ),
        "keyword": "phantom blade zero npcs, phantom blade zero characters list",
        "lastUpdated": UPDATED,
        "facts": [
            {"label": "Playable characters", "value": "1 - Soul only"},
            {"label": "Confirmed NPCs", "value": "Not confirmed pre-launch"},
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
                "title": "Confirmed NPCs",
                "content": table(
                    ["Character", "Role", "Portrayed by"],
                    npcs,
                    lambda c: [
                        f'<a href="/{c["slug"]}">{c["name"]}</a>',
                        c.get("role", "Not confirmed"),
                        c.get("portrayed_by", "Not confirmed"),
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
                    "<a href=\"/is-phantom-blade-zero-single-player\">is Phantom Blade Zero "
                    "single-player</a>.</p>"
                ),
            },
            {
                "id": "status",
                "title": "Source Status",
                "content": (
                    "<p>Tier-2 index generated from <code>src/data/entities/characters.json</code>. "
                    "The narrative cast is described on <a href=\"/characters\">characters</a>; the "
                    "protagonist has his own page at <a href=\"/protagonist\">Soul</a>.</p>"
                ),
            },
        ],
    }


def main():
    if not os.path.isdir(PAGES):
        print("run from the repo root")
        sys.exit(1)
    built = [write_page(p) for p in (build_blades(), build_phantom_edges(), build_npcs())]
    counts = {
        "weapons": len(load("weapons")),
        "characters": len(load("characters")),
    }
    print(f"regenerated {len(built)} tier-2 index pages: {', '.join(built)}")
    print(f"  entity rows available: weapons={counts['weapons']} characters={counts['characters']}")
    print("  empty tables are intentional and render an explicit 'not confirmed yet' note")


if __name__ == "__main__":
    main()
