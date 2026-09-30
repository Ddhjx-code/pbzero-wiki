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


def facts_for(rec):
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


BUILDERS = {"boss": (boss_sections, facts_for)}


def build(rec, kind):
    sections_fn, facts_fn = BUILDERS[kind]
    name = rec["name"]
    has_data = rec.get("weak") not in (None, NOT_CONFIRMED) or bool(rec.get("location"))
    subtitle = "Location, Weakness & How to Beat" if has_data else "Everything Confirmed So Far"
    return {
        "slug": rec["slug"],
        "title": f"{name} - {subtitle} (Phantom Blade Zero)",
        "description": (
            f"{name} in Phantom Blade Zero - what has been confirmed about the encounter, "
            f"its elemental weakness, rewards and how to approach it."
        ),
        "keyword": f"{name} phantom blade zero",
        "lastUpdated": "2026-09-28",
        "facts": facts_fn(rec),
        "sections": sections_fn(rec),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kind = "boss"
    if "--type" in sys.argv:
        kind = sys.argv[sys.argv.index("--type") + 1]
    if not args:
        print(__doc__)
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
