#!/usr/bin/env python3
"""Generate entity page JSON from a data file.

Usage: python3 scripts/gen-entity-pages.py <data-file> --type boss

Keeps the data layer separate from the rendered page, so adding an entity is
one record rather than one hand-written page.

Anything a record does not declare renders as "Not confirmed post-launch" or is
left out entirely. The generator has no default item names, no default
weaknesses and no default rewards, because a template that fills gaps
invents content.
"""
import json
import os
import sys

PAGES = "src/data/pages"
UNKNOWN = "Not confirmed post-launch"
NOT_CONFIRMED = "__not_confirmed__"
UPDATED = "2026-11-10"


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
            f"<p>{UNKNOWN}. Phantom Blade Zero does not run an elemental damage system, so "
            "there is no weakness table to fill in - nothing here is estimated from how a "
            "boss looks, which is exactly how wrong weakness tables get written.</p>"
            "<p>What the game does have is a colour language on enemy attacks, and it is the "
            "single most useful thing to learn: a <strong>red flash</strong> marks an unblockable "
            "attack that must be dodged, a <strong>blue flash</strong> marks a parryable one that "
            "should be deflected, and a <strong>purple flash</strong> means the boss has just "
            "parried <em>you</em> and a counter is coming. See "
            "<a href=\"/combat\">the combat system</a> for how Sha-Chi feeds into this.</p>"
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
        {"id": "weakness", "title": "Weaknesses and Counters", "content": affinity_block(rec)}
    )

    drops = rec.get("drops") or []
    if drops:
        rewards = "<ul>" + "".join(f"<li>{d}</li>" for d in drops) + "</ul>"
    else:
        rewards = (
            f"<p>{UNKNOWN}. No guide we checked records a drop for this encounter, so none is "
            "listed - a guess here would be worse than a blank.</p>"
        )
    out.append({"id": "rewards", "title": "Rewards", "content": rewards})

    strategy = ""
    for para in rec.get("strategy") or []:
        strategy += f"<p>{para}</p>"

    phases = rec.get("phases") or []
    if phases:
        rows = "".join(
            f"<tr><td>{p['when']}</td><td>{p['watch']}</td><td>{p['answer']}</td></tr>"
            for p in phases
            if isinstance(p, dict)
        )
        strategy += (
            "<h3>Attacks worth knowing</h3>"
            "<table><thead><tr><th>Attack</th><th>What it does</th><th>Answer</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    tips = rec.get("tips") or []
    if tips:
        strategy += "<h3>What works</h3><ul>" + "".join(f"<li>{t}</li>" for t in tips) + "</ul>"

    if not strategy:
        strategy = (
            f"<p>{UNKNOWN}. No fight breakdown has been published for this encounter, so none "
            "is written here. The general rules still apply: deflect blue flashes, dodge red ones, "
            "and break the Sha-Chi bar with "
            "<a href=\"/combat\">guard breaks</a> rather than trading hits.</p>"
        )
    strategy += observed_block(rec)
    out.append({"id": "strategy", "title": f"How to Beat the {name}", "content": strategy})

    out.append(
        {
            "id": "status",
            "title": "Status",
            "content": (
                f"<p>This page tracks the {name} in Phantom Blade Zero, released "
                "<a href=\"/release-date\">October 29, 2026</a>. Location, drops and tactics are "
                "filled from the shipped game and from published fight guides; anything still "
                f"marked &ldquo;{UNKNOWN.lower()}&rdquo; has not been confirmed by any source we "
                "could check. See the <a href=\"/boss-list\">full boss list</a> for the roster by "
                "region and the <a href=\"/walkthrough\">walkthrough</a> for where the fight sits "
                "in the campaign.</p>"
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
    facts.append(("Weak to", display(rec["weak"]) if "weak" in rec else "No elemental system - see counters"))
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
    if rec.get("requirement"):
        facts.append(("Requirement", rec["requirement"]))
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
        secondary = "secondar" in slot.lower() or "phantom" in str(rec.get("category", "")).lower()
        index = (
            '<a href="/phantom-edges">Phantom Edge index</a>'
            if secondary
            else '<a href="/blades">blade index</a>'
        )
        slot_text = (
            f"<p>{name} occupies the <strong>{slot}</strong> slot, and it is classed as "
            f"<strong>{display(rec.get('category'))}</strong>. Soul carries two primary blades and "
            "two secondary <a href=\"/phantom-edges\">Phantom Edges</a> at once, and switching between "
            "the four refills stamina rather than costing it - which is what keeps a combo chain "
            "running. <a href=\"/combat\">Sha-chi</a> is a separate pool, spent on heavy attacks and "
            f"blocks. The full class lists are on the {index}.</p>"
        )
    else:
        slot_text = f"<p>{UNKNOWN} which slot this weapon uses.</p>"
    out.append({"id": "classification", "title": "Weapon Class and Slot", "content": slot_text})

    stats = [
        ("Damage", rec.get("damage")),
        ("Scaling", rec.get("scaling")),
        ("Attack speed", rec.get("speed")),
        ("Range", rec.get("range")),
    ]
    known = [(label, value) for label, value in stats if value]
    if known:
        rows = "".join(f"<tr><td>{label}</td><td>{value}</td></tr>" for label, value in known)
        body = (
            "<table><thead><tr><th>Property</th><th>Value</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )
        missing = [label for label, value in stats if not value]
        if missing:
            body += (
                f"<p>No published figure exists for {', '.join(m.lower() for m in missing)}, so "
                "those rows are left out rather than filled with a plausible number.</p>"
            )
    else:
        body = (
            f"<p>{UNKNOWN}. Phantom Blade Zero does not publish a numeric stat sheet for individual "
            "weapons, and no measurement of this one has been recorded, so no damage, scaling or "
            "speed figure is given here. A number invented from how the weapon looks is exactly the "
            "kind of filler this page exists to avoid.</p>"
        )
    out.append({"id": "stats", "title": "Stats and Effects", "content": body})

    moves = rec.get("moveset") or []
    if moves:
        combo = "<ul>" + "".join(f"<li>{m}</li>" for m in moves) + "</ul>"
    elif rec.get("property"):
        combo = (
            f"<p>The reason to carry it is its property rather than a damage number: "
            f"{rec['property'].rstrip('.')}.</p>"
            "<p>Switching to it mid-combo refills stamina, so its practical job is to extend a chain "
            "past the point where the blade you were using runs dry. See "
            "<a href=\"/combat\">the combat system</a> for how the swap window works.</p>"
        )
    else:
        combo = (
            f"<p>{UNKNOWN}. No verified note on how this weapon behaves inside a combo has been "
            "published, so nothing is written here.</p>"
        )
    out.append({"id": "combo", "title": "How It Plays", "content": combo})

    source = rec.get("obtained")
    if source:
        acquisition = f"<p><strong>{source}.</strong></p>"
        if rec.get("requirement"):
            acquisition += f"<p>Gated behind: {rec['requirement']}.</p>"
        acquisition += (
            "<p>Acquisition points are taken from the acquisition table on "
            "<a href=\"/weapons\">the weapons hub</a>, which is kept in step with this page - if a "
            "route is corrected there, it is corrected here.</p>"
        )
    else:
        acquisition = (
            f"<p>{UNKNOWN}. No acquisition route has been recorded for this weapon.</p>"
        )
    out.append({"id": "acquisition", "title": "How to Obtain", "content": acquisition})
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

    bg = rec.get("background")
    out.append(
        {
            "id": "background",
            "title": "Background",
            "content": (
                f"<p>{bg}</p>"
                if bg
                else f"<p>{UNKNOWN} backstory. Anything here comes from S-GAME's published "
                "material; nothing is inferred from how a character looks or from the mobile "
                "series' continuity.</p>"
            ),
        }
    )

    playable = rec.get("playable")
    if playable is True:
        play_text = f"<p><strong>{name} is playable.</strong></p>"
    elif playable is False:
        play_text = (
            f"<p><strong>{name} is not playable.</strong> Phantom Blade Zero is single-player and "
            "the player controls Soul throughout - a claim that any other character is playable "
            "needs an official source, because several pre-launch write-ups carried a roster from "
            "S-Game's mobile entries by mistake.</p>"
        )
    else:
        play_text = f"<p>{UNKNOWN} whether this character can be played.</p>"
    out.append({"id": "playable", "title": "Playable or NPC", "content": play_text})

    rel = rec.get("relationships") or []
    if rel:
        rows = "".join(
            f"<tr><td>{r['to']}</td><td>{r['with']}</td></tr>" for r in rel if isinstance(r, dict)
        )
        rel_body = (
            "<table><thead><tr><th>Character</th><th>Relationship</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
            if rows
            else f"<p>{UNKNOWN} published relationships.</p>"
        )
    else:
        rel_body = f"<p>{UNKNOWN} published relationships.</p>"
    out.append({"id": "relationships", "title": "Relationships", "content": rel_body})

    shown = rec.get("appearances") or rec.get("observed") or []
    if shown:
        items = "".join(f"<li>{o}</li>" for o in shown)
        appear = (
            f"<ul>{items}</ul>"
            "<p>Everything above comes from footage S-GAME released. Anything not listed has not "
            "been shown, however confident a write-up elsewhere looks.</p>"
        )
    else:
        appear = f"<p>{UNKNOWN} on-screen appearances catalogued for this character.</p>"
    cast = rec.get("portrayed_by")
    if cast:
        appear += (
            f"<p>Portrayed by <strong>{cast}</strong>. Character models were built from 3D scans of "
            "the cast and facial capture came from the actors themselves.</p>"
        )
    out.append({"id": "appearances", "title": "Appearances and Portrayal", "content": appear})

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
    out.append(
        {
            "id": "status",
            "title": "Source Status",
            "content": (
                f"<p>This page tracks the quest &ldquo;{name}&rdquo; in Phantom Blade Zero. Steps and "
                f"rewards are filled from the shipped game; anything still marked "
                f"&ldquo;{UNKNOWN.lower()}&rdquo; has not been verified.</p>"
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
                f"<p>This entry is filled from the shipped game on either platform; PS5 trophy and "
                f"PC achievement lists are recorded separately where they differ. See "
                f"<a href=\"/trophy-guide\">the trophy guide</a> for the full list and "
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
            f"{n} in Phantom Blade Zero - where the fight happens, what it drops, and how its "
            "attack patterns are countered, including the red and blue flash tells."
        ),
        "subtitle": lambda has: "Location, Tactics & Rewards" if has else "Everything Confirmed",
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
        "lastUpdated": rec.get("updated") or UPDATED,
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
    overwrite = "--overwrite" in sys.argv
    written = skipped = 0
    for rec in records:
        path = os.path.join(PAGES, f'{rec["slug"]}.json')
        if os.path.exists(path) and not overwrite:
            skipped += 1
            continue
        json.dump(build(rec, kind), open(path, "w"), ensure_ascii=False, indent=2)
        written += 1
    print(f"{written} written, {skipped} skipped ({kind}) from {os.path.basename(args[0])}")


if __name__ == "__main__":
    main()
