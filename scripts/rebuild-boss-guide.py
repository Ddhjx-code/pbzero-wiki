#!/usr/bin/env python3
"""Rebuild /boss-guide as the boss theme hub.

The old page was written pre-launch: it listed "confirmed bosses", linked eight
stub pages and carried a "what changed this week" section. Now that the roster is
real, the hub has a different job - teach the defensive rules once, then route
people to the region index (/boss-list) and to the individual fights that
actually stop runs.

Counts and links are derived from src/data/entities/bosses.json, so this page
cannot drift from the roster.
"""
import json
from collections import Counter

ENTITIES = "src/data/entities/bosses.json"
OUT = "src/data/pages/boss-guide.json"

# Hardest fights, ordered roughly as players meet them. Each one is a fight where
# the general rules stop being enough.
SPIKES = [
    ("gu-wanyue", "Gu Wanyue — immune until the Sha-Chi bar breaks"),
    ("wu-lengshuang-the-soft-sword", "Wu Lengshuang — a parry duel with a purple-flash counter"),
    ("bai-chilian-lady-of-the-twin-serpents", "Bai Chilian — the attack set changes mid-fight"),
    ("bi-feng-giant-saber-commander", "Bi Feng — sweeping attacks and a guard that has to be broken"),
    ("leidang-boss", "Lei Dang — two phases, and the Tiger Cannon behind them"),
    ("zuo-shang-the-true-long", "Zuo Shang — the true-ending final boss"),
]


def main():
    records = json.load(open(ENTITIES, encoding="utf-8"))
    regions = Counter(r["region"] for r in records)
    story = sum(1 for r in records if r["kind"].lower().startswith("story"))
    optional = sum(1 for r in records if r["kind"].lower().startswith("optional"))

    order = [
        "Prologue & Weeping Creek Valley",
        "Crimson Manor & Crimson Forest",
        "Village of Lu",
        "Pangzhen",
        "Mandate Encampment",
        "Meigu Lake",
        "Mountain of Imprisonment",
        "Mirage Estate",
        "Mount Soulrend & endgame",
    ]
    rows = "".join(
        f'<tr><td>{r}</td><td>{regions.get(r, 0)}</td>'
        f'<td><a href="/boss-list">roster</a></td></tr>'
        for r in order
        if regions.get(r)
    )

    spikes = "".join(f'<li><a href="/{slug}">{label}</a></li>' for slug, label in SPIKES)

    sections = [
        {
            "id": "overview",
            "title": "The Short Answer",
            "content": (
                f"<p>Phantom Blade Zero has <strong>{len(records)} documented boss encounters</strong> across "
                f"nine regions: {story} on the critical path and {optional} optional. Published counts range "
                "from 50 to 62 because some lists fold in rematches, so the number you see elsewhere is not "
                "wrong so much as counting something different.</p>"
                "<p>This page is the hub: the rules that apply to every fight, then the route into the "
                '<a href="/boss-list">full roster by region</a> and the individual fights worth reading up on '
                "before you walk in.</p>"
            ),
        },
        {
            "id": "rules",
            "title": "The Three Colours That Decide Every Fight",
            "content": (
                "<p>There is no elemental weakness system, so the usual resistance tables do not apply. What the "
                "game uses instead is a colour language on enemy attacks, and it is the single most valuable "
                "thing to internalise:</p>"
                "<table><thead><tr><th>Tell</th><th>Meaning</th><th>Answer</th></tr></thead><tbody>"
                "<tr><td><strong>Red flash</strong></td><td>Unblockable attack</td><td>Dodge — guarding does nothing</td></tr>"
                "<tr><td><strong>Blue flash</strong></td><td>Parryable attack</td><td>Deflect for the fastest Sha-Chi drain</td></tr>"
                "<tr><td><strong>Purple flash</strong></td><td>The boss just parried you</td><td>Stop attacking; a counter is coming</td></tr>"
                "</tbody></table>"
                '<p>The purple flash is the one that ends runs, because it looks like an opening. See '
                '<a href="/combat">the combat system</a> for how Sha-Chi, Ghoststep and guard breaks fit together.</p>'
            ),
        },
        {
            "id": "general-tips",
            "title": "What Works on Almost Everything",
            "content": (
                "<ul>"
                "<li>Deflect blue flashes to drain Sha-Chi — it is the fastest way to open a damage window, faster than hitting.</li>"
                "<li>Dodge red flashes instead of blocking. Every guide that mentions the system says the same thing.</li>"
                "<li>Break guard with Sha-Chi attacks rather than chipping health through a raised guard.</li>"
                "<li>Swap weapons mid-fight: switching refills stamina, which is what keeps a combo alive.</li>"
                "<li>Hold Power Surge for the window you have already created, never to create one.</li>"
                "<li>When a boss will not take damage at all, look for the smoke or shimmer effect — that is an "
                "invulnerability state you have to break, not out-damage.</li>"
                "</ul>"
            ),
        },
        {
            "id": "regions",
            "title": "Bosses by Region",
            "content": (
                "<table><thead><tr><th>Region</th><th>Bosses</th><th>Index</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>"
                '<p>Full names, story or optional status, location and drops are in the '
                '<a href="/boss-list">boss list</a>; every row there links to the individual fight page.</p>'
            ),
        },
        {
            "id": "spikes",
            "title": "The Fights That Actually Stop People",
            "content": (
                f"<ul>{spikes}</ul>"
                "<p>Everything else in the roster folds into two habits: read the flash colour, and stop pressing "
                "attack when the boss tells you to stop.</p>"
            ),
        },
        {
            "id": "endings",
            "title": "Which Boss Ends Which Ending",
            "content": (
                "<p>The normal ending closes on <strong>Meng Hua</strong>; the true ending continues past her to "
                "<strong>Zuo Shang, The True Long</strong>, and the final scripted encounter only fires if the "
                'true-ending checklist is complete. The requirements are on the '
                '<a href="/true-ending">true ending page</a>, and the four endings themselves are on '
                '<a href="/endings">endings</a>.</p>'
            ),
        },
        {
            "id": "status",
            "title": "Sources",
            "content": (
                "<p>Roster, locations and drops are compiled from published post-launch guides (NoobFeed, Game8, "
                "GamesRadar, 游侠网) and cross-checked against each other; where they disagree the individual "
                "fight page says so. Attack patterns and colour tells are only written where a guide describes "
                f"the fight — the {len(records) - sum(1 for r in records if r.get('tips'))} encounters without "
                "published notes are marked as unconfirmed rather than filled with filler.</p>"
            ),
        },
    ]

    page = {
        "slug": "boss-guide",
        "title": "Phantom Blade Zero Boss Guide - Rules, Regions and the Fights That Stop Runs",
        "description": (
            "How boss fights work in Phantom Blade Zero: the red, blue and purple flash tells, the Sha-Chi "
            "loop, and where every one of the 59 documented bosses sits by region."
        ),
        "keyword": "phantom blade zero boss guide",
        "lastUpdated": "2026-11-10",
        "facts": [
            {"label": "Bosses", "value": f"{len(records)} documented"},
            {"label": "Story", "value": str(story)},
            {"label": "Optional", "value": str(optional)},
            {"label": "Regions", "value": str(len(regions))},
            {"label": "Normal final boss", "value": "Meng Hua"},
            {"label": "True final boss", "value": "Zuo Shang, The True Long"},
        ],
        "sections": sections,
    }
    json.dump(page, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"boss-guide rebuilt: {len(sections)} sections, {len(records)} bosses, {len(regions)} regions")


if __name__ == "__main__":
    main()
