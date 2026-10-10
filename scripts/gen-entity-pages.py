#!/usr/bin/env python3
"""Generate entity page JSON from a data file.

Usage: python3 scripts/gen-entity-pages.py <data-file> --type boss

Keeps the data layer separate from the rendered page, so adding an entity is
one record rather than one hand-written page.

Anything a record does not declare renders as "Not confirmed pre-launch" or is
left out entirely. The generator has no default item names, no default
weaknesses and no default rewards, because a template that fills gaps
invents content.
"""
import json
import os
import sys

PAGES = "src/data/pages"
UNKNOWN = "Not confirmed pre-launch"
NOT_CONFIRMED = "__not_confirmed__"


def display(value):
    return UNKNOWN if value in (None, "", NOT_CONFIRMED) else value


def affinity_block(rec):
    rows = [
        ("Weak to", display(rec["weak"]) if "weak" in rec else UNKNOWN),
        ("Resists", display(rec.get("resists"))),
        ("Absorbs", display(rec.get("absorbs"))),
        ("Immune", display(rec.get("immune"))),
    ]
    body = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
    table = (
        "<table><thead><tr><th>Property</th><th>Value</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )

    if rec.get("weak") == NOT_CONFIRMED or "weak" not in rec:
        return table + (
            f"<p>{UNKNOWN}. S-GAME has not published elemental affinities for this "
            "encounter, and no demo footage shows one being exploited. Nothing here "
            "is estimated from the boss's appearance - that is exactly how wrong "
            "weakness tables get written before release.</p>"
        )

    note = f"<p>Bring {rec['weak']} damage.</p>"
    extras = []
    if rec.get("resists"):
        extras.append(f"{rec['resists']} is resisted, so those turns are halved.")
    if rec.get("absorbs"):
        extras.append(f"{rec['absorbs']} is absorbed and heals the boss.")
    if rec.get("immune"):
        extras.append(f"{rec['immune']} has no effect at all.")
    if extras:
        note += f"<p>{' '.join(extras)}</p>"
    return table + note


def observed_block(rec):
    observed = rec.get("observed") or []
    if not observed:
        return ""
    items = "".join(f"<li>{o}</li>" for o in observed)
    return (
        "<h3>What has actually been shown</h3>"
        f"<ul>{items}</ul>"
        "<p>Everything above comes from footage S-GAME released. Anything not listed "
        "has not been shown, however confident a write-up elsewhere looks.</p>"
    )


def boss_sections(rec):
    name = rec["name"]
    out = [
        {"id": "overview", "title": "Overview", "content": f'<p>{rec["summary"]}</p>'},
    ]

    find = ""
    if rec.get("location"):
        find += f'<p><strong>Location:</strong> {rec["location"]}.</p>'
    if rec.get("act"):
        find += f'<p><strong>Appears in:</strong> {rec["act"]}.</p>'
    if rec.get("level"):
        find += f'<p><strong>Recommended level:</strong> {rec["level"]}.</p>'
    if rec.get("source"):
        find += f'<p><strong>First shown:</strong> {rec["source"]}.</p>'
    if not find:
        find = f"<p>{UNKNOWN} where this encounter sits in the campaign.</p>"
    out.append({"id": "how-to-find", "title": f"Where to Find the {name}", "content": find})

    out.append(
        {"id": "weakness", "title": "Weakness & Resistances", "content": affinity_block(rec)}
    )

    drops = rec.get("drops") or []
    if drops:
        rewards = "<ul>" + "".join(f"<li>{d}</li>" for d in drops) + "</ul>"
    else:
        rewards = (
            f"<p>{UNKNOWN}. Bosses in Phantom Blade Zero are described by S-GAME as "
            "rewarding unique weapons on defeat, but no drop table has been published "
            "for this encounter, so none is listed here.</p>"
        )
    out.append({"id": "rewards", "title": "Rewards", "content": rewards})

    strategy = observed_block(rec)
    tips = rec.get("tips") or []
    if tips:
        strategy += "<h3>How to approach it</h3><ul>" + "".join(f"<li>{t}</li>" for t in tips) + "</ul>"
    else:
        strategy += (
            "<h3>How to approach it</h3>"
            "<p>There is no honest strategy section for an encounter nobody outside the "
            "studio has finished. What can be said comes from the systems rather than from "
            "the fight: blocking and heavy attacks both spend "
            "<a href=\"/combat\">Sha-chi</a>, so a defensive player who blocks everything "
            "runs out of the resource at the worst moment. Unblockable attacks have to be "
            "dodged, which means reading the animation rather than relying on the guard.</p>"
            "<p>Real phase data, parry windows and timings land here once the game ships.</p>"
        )
    out.append({"id": "strategy", "title": f"How to Beat the {name}", "content": strategy})

    out.append(
        {
            "id": "status",
            "title": "Pre-launch Status",
            "content": (
                f"<p>This page tracks the {name} in Phantom Blade Zero, which releases on "
                "<a href=\"/release-date\">October 29, 2026</a>. It is written from official "
                "demo and trailer material only. After release it gets updated with verified "
                "fight data; see the <a href=\"/boss-guide\">boss guide</a> for the full roster "
                "and the <a href=\"/boss-video-guides\">video guide index</a> for walkthroughs.</p>"
            ),
        }
    )
    return out


def boss_facts(rec):
    facts = []
    if rec.get("location"):
        facts.append(("Location", rec["location"]))
    if rec.get("act"):
        facts.append(("Appears in", rec["act"]))
    if rec.get("level"):
        facts.append(("Recommended level", rec["level"]))
    facts.append(("Weak to", display(rec["weak"]) if "weak" in rec else UNKNOWN))
    if rec.get("resists"):
        facts.append(("Resists", rec["resists"]))
    if rec.get("absorbs"):
        facts.append(("Absorbs", rec["absorbs"]))
    if rec.get("source"):
        facts.append(("First shown", rec["source"]))
    if rec.get("drops"):
        facts.append(("Drops", " · ".join(rec["drops"])))
    return [{"label": k, "value": v} for k, v in facts]


def weapon_facts(rec):
    facts = []
    if rec.get("slot"):
        facts.append(("Slot", rec["slot"]))
    if rec.get("category"):
        facts.append(("Class", rec["category"]))
    facts.append(("Damage", display(rec.get("damage"))))
    facts.append(("Scaling", display(rec.get("scaling"))))
    facts.append(("Special property", display(rec.get("property"))))
    if rec.get("obtained"):
        facts.append(("How to obtain", rec["obtained"]))
    if rec.get("source"):
        facts.append(("First shown", rec["source"]))
    return [{"label": k, "value": v} for k, v in facts]


def character_facts(rec):
    facts = []
    facts.append(("Playable", "Yes" if rec.get("playable") else "No - NPC" if rec.get("playable") is False else UNKNOWN))
    if rec.get("role"):
        facts.append(("Role", rec["role"]))
    if rec.get("affiliation"):
        facts.append(("Affiliation", rec["affiliation"]))
    if rec.get("portrayed_by"):
        facts.append(("Portrayed by", rec["portrayed_by"]))
    if rec.get("weapon"):
        facts.append(("Weapon", rec["weapon"]))
    return [{"label": k, "value": v} for k, v in facts]


def quest_facts(rec):
    facts = []
    if rec.get("giver"):
        facts.append(("Given by", rec["giver"]))
    if rec.get("location"):
        facts.append(("Location", rec["location"]))
    if rec.get("trigger"):
        facts.append(("How to start", rec["trigger"]))
    facts.append(("Type", rec.get("kind") or UNKNOWN))
    if rec.get("reward"):
        facts.append(("Reward", " · ".join(rec["reward"]) if isinstance(rec["reward"], list) else rec["reward"]))
    return [{"label": k, "value": v} for k, v in facts]


def trophy_facts(rec):
    facts = []
    facts.append(("Rarity", display(rec.get("rarity"))))
    if rec.get("hidden"):
        facts.append(("Hidden", "Yes"))
    facts.append(("Missable", display(rec.get("missable"))))
    return [{"label": k, "value": v} for k, v in facts]


def weapon_sections(rec):
    name = rec["name"]
    out = [{"id": "overview", "title": "Overview", "content": f'<p>{rec["summary"]}</p>'}]

    slot = rec.get("slot")
    if slot:
        slot_text = (
            f"<p>{name} occupies the <strong>{slot}</strong> slot. Soul carries two primary blades and "
            "two secondary <a href=\"/weapons\">Phantom Edges</a> at once, and switching between the four "
            "refills stamina rather than costing it - which is what keeps a combo chain running. "
            "<a href=\"/combat\">Sha-chi</a> is a separate pool, spent on heavy attacks and blocks.</p>"
        )
    else:
        slot_text = f"<p>{UNKNOWN} which slot this weapon uses.</p>"
    out.append({"id": "classification", "title": "Weapon Class and Slot", "content": slot_text})

    stats = [
        ("Damage", rec.get("damage")),
        ("Scaling", rec.get("scaling")),
        ("Special property", rec.get("property")),
        ("Attack speed", rec.get("speed")),
        ("Range", rec.get("range")),
    ]
    rows = "".join(
        f"<tr><td>{label}</td><td>{display(value)}</td></tr>" for label, value in stats
    )
    body = (
        "<table><thead><tr><th>Stat</th><th>Value</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )
    if not any(v for _, v in stats):
        body += (
            f"<p>{UNKNOWN}. Numbers are filled in only after they have been measured in the "
            "shipped game - no value on this table is inferred from the weapon's appearance or name.</p>"
        )
    out.append({"id": "stats", "title": "Stats and Effects", "content": body})

    if rec.get("moveset"):
        moves = "".join(f"<li>{m}</li>" for m in rec["moveset"])
        combo = f"<ul>{moves}</ul>"
    else:
        combo = (
            f"<p>{UNKNOWN}. Individual weapon movesets have not been catalogued in material we could "
            "verify, so nothing is listed here.</p>"
        )
    out.append({"id": "combo", "title": "Combo Contribution", "content": combo})

    out.append(
        {
            "id": "acquisition",
            "title": "How to Obtain",
            "content": (
                f"<p>{rec['obtained'] if rec.get('obtained') else UNKNOWN}</p>"
                "<p>Boss kills are described by S-GAME as rewarding unique weapons, but no drop table "
                "has been published, so acquisition is recorded only once it has been confirmed.</p>"
            ),
        }
    )
    out.append(
        {
            "id": "status",
            "title": "Source Status",
            "content": (
                f"<p>This page tracks {name} in Phantom Blade Zero. Anything marked "
                f"&ldquo;{UNKNOWN.lower()}&rdquo; has not been published or measured yet; see the "
                "<a href=\"/weapons\">weapons list</a> for the system as a whole.</p>"
            ),
        }
    )
    return out


def character_sections(rec):
    name = rec["name"]
    out = [{"id": "overview", "title": "Overview", "content": f'<p>{rec["summary"]}</p>'}]

    playable = rec.get("playable")
    if playable is True:
        play_text = f"<p><strong>{name} is playable.</strong></p>"
    elif playable is False:
        play_text = (
            f"<p><strong>{name} is not playable.</strong> Phantom Blade Zero is single-player and "
            "the player controls Soul throughout - a claim that any other character is playable needs "
            "an official source, because several pre-launch write-ups have carried a roster from "
            "S-Game's mobile entries by mistake.</p>"
        )
    else:
        play_text = f"<p>{UNKNOWN} whether this character can be played.</p>"
    out.append({"id": "playable", "title": "Playable or NPC", "content": play_text})

    if rec.get("observed"):
        items = "".join(f"<li>{o}</li>" for o in rec["observed"])
        shown = f"<ul>{items}</ul>"
    else:
        shown = f"<p>{UNKNOWN} further on-screen detail.</p>"
    out.append({"id": "shown", "title": "What Has Been Shown", "content": shown})

    cast = rec.get("portrayed_by")
    out.append(
        {
            "id": "portrayal",
            "title": "Portrayal",
            "content": (
                f"<p>{cast}</p>"
                "<p>Character models were built from 3D scans of the cast and facial capture came from "
                "the actors themselves.</p>"
            )
            if cast
            else f"<p>{UNKNOWN} which actor portrays this character.</p>"
        }
    )

    out.append(
        {
            "id": "status",
            "title": "Source Status",
            "content": (
                f"<p>This page tracks {name} in Phantom Blade Zero. See the "
                "<a href=\"/characters\">characters page</a> for the full cast and "
                "<a href=\"/protagonist\">Soul</a> for the protagonist.</p>"
            ),
        }
    )
    return out


def quest_sections(rec):
    name = rec["name"]
    out = [{"id": "overview", "title": "Overview", "content": f'<p>{rec["summary"]}</p>'}]

    steps = rec.get("steps") or []
    if steps:
        walkthrough = "<ol>" + "".join(f"<li>{s}</li>" for s in steps) + "</ol>"
    else:
        walkthrough = (
            f"<p>{UNKNOWN}. Quest walkthroughs are written from the shipped game; a step list written "
            "before release would be a guess with extra steps.</p>"
        )
    out.append({"id": "walkthrough", "title": "Walkthrough", "content": walkthrough})

    out.append(
        {
            "id": "requirements",
            "title": "How to Start",
            "content": f"<p>{rec['trigger'] if rec.get('trigger') else UNKNOWN}</p>",
        }
    )

    reward = rec.get("reward")
    if reward:
        reward_text = (
            "<ul>"
            + "".join(f"<li>{r}</li>" for r in reward)
            + "</ul>"
            if isinstance(reward, list)
            else f"<p>{reward}</p>"
        )
    else:
        reward_text = f"<p>{UNKNOWN} what this quest rewards.</p>"
    out.append({"id": "rewards", "title": "Rewards", "content": reward_text})

    out.append(
        {
            "id": "branching",
            "title": "Does It Affect the Story?",
            "content": (
                "<p>The official State of Play write-up says interacting with citizens and completing "
                "side quests &ldquo;might even open up new story paths&rdquo;. That is the only published "
                "statement about quest branching, so whether <em>this</em> quest gates anything is "
                f"{UNKNOWN.lower()}.</p>"
                "<p>See <a href=\"/endings\">endings</a> for what is known about how the story diverges.</p>"
            ),
        }
    )
    return out


def trophy_sections(rec):
    name = rec["name"]
    out = [{"id": "overview", "title": "Overview", "content": f'<p>{rec["summary"]}</p>'}]

    if rec.get("how"):
        how = f"<p>{rec['how']}</p>"
        if rec.get("steps"):
            how += "<ol>" + "".join(f"<li>{s}</li>" for s in rec["steps"]) + "</ol>"
    else:
        how = f"<p>{UNKNOWN} how to earn this trophy.</p>"
    out.append({"id": "how", "title": "How to Earn", "content": how})

    rows = [
        ("Rarity", display(rec.get("rarity"))),
        ("Missable", display(rec.get("missable"))),
        ("Hidden", "Yes" if rec.get("hidden") else display(rec.get("hidden"))),
        ("Glitchable", display(rec.get("glitchable"))),
    ]
    out.append(
        {
            "id": "details",
            "title": "Trophy Details",
            "content": "<table><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>"
            + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
            + "</tbody></table>",
        }
    )

    out.append(
        {
            "id": "status",
            "title": "Source Status",
            "content": (
                f"<p>Trophy lists for Phantom Blade Zero are not published before release. This entry is "
                f"filled from the shipped game on either platform; PS5 trophy and PC achievement lists "
                f"are recorded separately where they differ. See "
                f"<a href=\"/how-long-to-beat\">how long to beat</a> for run-length context.</p>"
            ),
        }
    )
    return out


META = {
    "boss": {
        "sections": boss_sections,
        "facts": boss_facts,
        "keyword": lambda n: f"{n} phantom blade zero boss",
        "desc": lambda n, has: (
            f"{n} in Phantom Blade Zero - what has been confirmed about the encounter, "
            "its elemental weakness, rewards and how to approach it."
        ),
        "subtitle": lambda has: "Location, Weakness & How to Beat" if has else "Everything Confirmed So Far",
    },
    "weapon": {
        "sections": weapon_sections,
        "facts": weapon_facts,
        "keyword": lambda n: f"{n} phantom blade zero",
        "desc": lambda n, has: (
            f"{n} in Phantom Blade Zero - weapon class, slot, stats, combo contribution and how to "
            "obtain it, with unconfirmed numbers left marked as unconfirmed."
        ),
        "subtitle": lambda has: "Stats, Combo & How to Get" if has else "Everything Confirmed So Far",
    },
    "character": {
        "sections": character_sections,
        "facts": character_facts,
        "keyword": lambda n: f"{n} phantom blade zero character",
        "desc": lambda n, has: (
            f"{n} in Phantom Blade Zero - whether the character is playable, what has been shown, "
            "and who portrays them."
        ),
        "subtitle": lambda has: "Role, Story & Portrayal",
    },
    "quest": {
        "sections": quest_sections,
        "facts": quest_facts,
        "keyword": lambda n: f"{n} phantom blade zero quest",
        "desc": lambda n, has: (
            f"{n} in Phantom Blade Zero - how to start the quest, the walkthrough, rewards, and "
            "whether it opens new story paths."
        ),
        "subtitle": lambda has: "Walkthrough & Rewards",
    },
    "trophy": {
        "sections": trophy_sections,
        "facts": trophy_facts,
        "keyword": lambda n: f"{n} phantom blade zero trophy",
        "desc": lambda n, has: (
            f"{n} trophy in Phantom Blade Zero - how to earn it, whether it is missable, and "
            "rarity once the list is public."
        ),
        "subtitle": lambda has: "How to Earn & Missable Status",
    },
}


def build(rec, kind):
    meta = META[kind]
    name = rec["name"]
    has_data = any(
        v not in (None, "", NOT_CONFIRMED) for k, v in rec.items() if k not in ("slug", "name", "summary")
    )
    return {
        "slug": rec["slug"],
        "title": f"{name} - {meta['subtitle'](has_data)} (Phantom Blade Zero)",
        "description": meta["desc"](name, has_data),
        "keyword": meta["keyword"](name),
        "lastUpdated": "2026-09-28",
        "facts": meta["facts"](rec),
        "sections": meta["sections"](rec),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kind = "boss"
    if "--type" in sys.argv:
        kind = sys.argv[sys.argv.index("--type") + 1]
    if not args:
        print(__doc__)
        sys.exit(1)
    if kind not in META:
        print(f"unknown --type {kind!r}; available: {', '.join(sorted(META))}")
        sys.exit(1)

    records = json.load(open(args[0]))
    written = skipped = 0
    for rec in records:
        path = os.path.join(PAGES, f'{rec["slug"]}.json')
        if os.path.exists(path):
            skipped += 1
            continue
        json.dump(build(rec, kind), open(path, "w"), ensure_ascii=False, indent=2)
        written += 1
    print(f"{written} written, {skipped} skipped ({kind}) from {os.path.basename(args[0])}")


if __name__ == "__main__":
    main()
