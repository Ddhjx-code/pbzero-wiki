#!/usr/bin/env python3
"""Generate entity page JSON from a data file.

Usage: python3 scripts/gen-entity-pages.py <data-file> --type boss

Keeps the data layer separate from the rendered page, so adding an entity is
one record rather than one hand-written page.

The rule is that a record only renders what it declares - no default item
names, default weaknesses or default rewards, because a template that fills
gaps invents content. What it must not do is announce the gap in the same
words on 137 pages: an omission should read as a decision, not as a template
hole. See scripts/fix-placeholder-pages.py for the sweep that cleaned up the
pages this file used to write.
"""
import json
import os
import re
import sys

PAGES = "src/data/pages"
UNKNOWN = "Not confirmed post-launch"
NOT_CONFIRMED = "__not_confirmed__"
UPDATED = "2026-11-13"

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


def display(value):
    return UNKNOWN if value in (None, "", NOT_CONFIRMED) else value


ANCHOR_STYLE = "color:var(--accent);text-decoration:underline;text-underline-offset:2px"
_SLUGS = None

# bosses.json is stored in progression order, so the record order is the
# in-game order. main() fills these so a regenerated page still carries its
# position and its neighbours instead of standing alone.
BOSS_ORDER = []
BOSS_NAMES = {}


def boss_nav(slug):
    if slug not in BOSS_ORDER:
        return ""
    i = BOSS_ORDER.index(slug)
    total = len(BOSS_ORDER)
    prev_s = BOSS_ORDER[i - 1] if i > 0 else None
    next_s = BOSS_ORDER[i + 1] if i + 1 < total else None

    def link(s):
        return f'<a href="/{s}" style="{ANCHOR_STYLE}">{BOSS_NAMES.get(s, s)}</a>'

    before = f"Before it: {link(prev_s)}. " if prev_s else "It opens the game. "
    after = f"After it: {link(next_s)}." if next_s else "It closes the game."
    return (
        f"No. <strong>{i + 1}</strong> of {total} in the progression order. {before}{after} "
    )


def item_slug(text):
    """Same shape the weapon and trophy builders use, so a drop resolves to the
    page that already exists for that item."""
    base = re.sub(r"\s*\([^)]*\)", "", text).strip()
    base = base.replace("&", " and ").replace("'", "").replace("\u2019", "")
    base = base.lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def page_slugs():
    global _SLUGS
    if _SLUGS is None:
        _SLUGS = {f[:-5] for f in os.listdir(PAGES) if f.endswith(".json")}
    return _SLUGS


def link_drop(text):
    """Link a drop only when its page exists on disk. A dead internal link is
    worse than plain text, so the slug is checked rather than assumed."""
    slug = item_slug(text)
    if slug and slug in page_slugs():
        return f'<a href="/{slug}" style="{ANCHOR_STYLE}">{text}</a>'
    return text


def affinity_block(rec):
    """No weakness table, because there is no weakness system.

    The old version printed a four-row table whose every cell said "Not
    confirmed post-launch" - a table that looked like data and carried none,
    repeated verbatim on 59 pages.
    """
    if "weak" in rec and rec.get("weak") not in (NOT_CONFIRMED, None, ""):
        rows = [
            ("Weak to", rec["weak"]),
            ("Resists", display(rec.get("resists"))),
            ("Absorbs", display(rec.get("absorbs"))),
            ("Immune", display(rec.get("immune"))),
        ]
        body = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows)
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
        return (
            "<table><thead><tr><th>Property</th><th>Value</th></tr></thead>"
            f"<tbody>{body}</tbody></table>{note}"
        )

    return (
        "<p>There is no weakness table for this fight because there is no damage-type "
        "system to fill one in: nothing here resists, absorbs or is immune to anything, "
        "and a chart that says otherwise has been inferred from how the boss looks. Read "
        "the fight by attack colour instead - <strong>red</strong> must be dodged, "
        "<strong>blue</strong> must be deflected, <strong>purple</strong> means it has "
        "just parried you and a counter is already coming. The full explanation is on "
        "<a href=\"/combat\">the combat system</a>.</p>"
        f"<p>{KIND_NOTE.get(rec.get('kind', ''), '')}</p>"
    )


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
        rewards = "<ul>" + "".join(f"<li>{link_drop(d)}</li>" for d in drops) + "</ul>"
    else:
        rewards = (
            "<p>No drop is recorded for this encounter in the sources checked, so none is "
            "listed. That is a gap in the record rather than a statement that it drops "
            "nothing.</p>"
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
            f"<p>No published fight breakdown exists for {name}, so none is written here - a "
            "move list assembled from a video thumbnail would be worse than its absence. The "
            "general rules still hold, and they are most of the fight: deflect the blue flashes, "
            "dodge the red ones, and break the Sha-Chi bar with guard breaks instead of trading "
            "hits. How those interact is on <a href=\"/combat\">the combat system</a>; where the "
            "encounter sits is on the <a href=\"/boss-order\">progression order</a>.</p>"
        )
    strategy += observed_block(rec)
    out.append({"id": "strategy", "title": f"How to Beat the {name}", "content": strategy})

    out.append(
        {
            "id": "status",
            "title": "Status",
            "content": (
                f"<p>{boss_nav(rec['slug'])} Location and drops come from the shipped game. The "
                "roster by region is on the <a href=\"/boss-list\">boss list</a>, and the order "
                "you meet them in - including the optional fights that expire when a region is "
                "left - is on the <a href=\"/boss-order\">progression order</a>.</p>"
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
    # A facts card is a summary, not a confession: three of six rows reading
    # "not confirmed" tells a reader nothing they can use, so the unknown rows
    # are dropped rather than filled with the placeholder.
    facts = []
    if rec.get("slot"):
        facts.append(("Slot", rec["slot"]))
    if rec.get("category"):
        facts.append(("Class", rec["category"]))
    for label, key in (("Damage", "damage"), ("Scaling", "scaling")):
        if rec.get(key):
            facts.append((label, rec[key]))
    if rec.get("property"):
        facts.append(("Special property", rec["property"]))
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
            f"<p>{name} has no published damage, scaling or speed figure, because the game does "
            "not print a numeric stat sheet for individual weapons. Nothing has been measured for "
            "this one either, so those three numbers are absent rather than estimated - the slot "
            "and the property are what the choice actually turns on.</p>"
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
            f"<p>Nothing verified has been published on how {name} behaves inside a combo, so no "
            "chain is described here. The general rule still applies: swapping to a secondary "
            "refills stamina instead of spending it, so the second slot is what extends a chain "
            "past the point the blade you were using runs dry - see "
            "<a href=\"/combat\">the combat system</a>.</p>"
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
        acquisition = f"<p>No acquisition route has been recorded for {name} yet.</p>"
    out.append({"id": "acquisition", "title": "How to Obtain", "content": acquisition})
    out.append(
        {
            "id": "status",
            "title": "Source Status",
            "content": (
                f"<p>This page records {name} by slot, class and acquisition point, and by its "
                "property where one is published. Figures the game itself does not expose are "
                "left out. The system as a whole, with the full slot and class breakdown, is on "
                "<a href=\"/weapons\">the weapons list</a>.</p>"
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
        how = f"<p>The unlock condition for {name} has not been recorded here yet.</p>"
    out.append({"id": "how", "title": "How to Earn", "content": how})

    # No "Glitchable" row: there is no data behind it, and a row whose value is
    # "not confirmed" on all 36 pages is noise dressed as a table.
    rows = [
        ("Rarity", display(rec.get("rarity"))),
        ("Missable", display(rec.get("missable"))),
        ("Hidden", "Yes" if rec.get("hidden") else "No"),
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
                "<p>Filled from the shipped game on either platform; PS5 trophy and PC "
                "achievement lists are recorded separately where they differ. The full list "
                "with rarity is on <a href=\"/trophy-list\">the trophy list</a>, and the "
                "Platinum route is on <a href=\"/trophy-guide\">the trophy guide</a>.</p>"
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
    if kind == "boss":
        BOSS_ORDER[:] = [r["slug"] for r in records]
        BOSS_NAMES.update({r["slug"]: r["name"] for r in records})
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
