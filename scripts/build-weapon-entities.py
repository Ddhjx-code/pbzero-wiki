#!/usr/bin/env python3
"""Build src/data/entities/weapons.json from the acquisition table on /weapons.

The table is the single source of truth for *where* a weapon comes from. Each
cell is a compound string - location, sometimes a "defeat X" condition, and
sometimes what the weapon actually does - so the split is done deliberately
rather than by blanket-splitting on the semicolon.

Usage: python3 scripts/build-weapon-entities.py
"""
import json
import os
import re

PAGES = "src/data/pages"
OUT = "src/data/entities/weapons.json"

# Types are read off the item name where the name states one ("Feather Bow",
# "Thunder Spear"). Where the name does not state a type, the record keeps
# "Not stated" rather than guessing from a blurb.
EDGE_TYPES = {
    "Bashpole": "Polearm",
    "Bastion": "Shield",
    "Dread Axe": "Axe",
    "Feather Bow": "Bow",
    "Fire Meteor": "Ranged (fire)",
    "Flying Dagger": "Throwing blade",
    "Flying Guillotine": "Throwing blade",
    "Heartrend Pipa": "Instrument",
    "Hunter's Chain Sickle": "Chain sickle",
    "Iron Gauntlets": "Gauntlets",
    "Loong Trident": "Trident",
    "Thunder Spear": "Spear",
    "Tiger Cannon": "Cannon",
}

# Only genuine mechanics belong in `property`. Anything starting with "defeat"
# is an acquisition condition, and ownership notes ("Mu Xiaokui's blade") are
# provenance - both stay in `obtained` instead.
PROPERTY = {
    "Jagged Steel": "Slashes cause Bleeding",
    "The Fanatic's Broken Blade": "Drinking lets the blade be thrown",
    "Tianxuan Bronze Sword": "High shield-break",
    "Soft Snake Sword": "Deflects attacks and cuts threads",
    "Parting Hooks": "Guard stance counters melee",
    "Seamless Death": "Ring blades can be hurled",
    "Sanguine": "Tempers into Infernal Rouge at level 5",
    "Sanguine Reach": "Tempers into Blazing Edge",
    "Aureate": "Mimics Zuo Shang's Golden Sword Energy",
}
REQUIREMENT = {
    "Whiteshadow": "Four retainer masks plus the Blizzard Blademaster",
}
# Cells that carry a second fact inside the location string.
OBTAINED_OVERRIDE = {
    "Sanguine": "Story reward - the starting blade",
    "Wooden Sanguine": "Story reward - Soul's childhood blade",
}
# "Sanguine is a one-handed in ..." is not English.
CATEGORY_NOUN = {
    "One-handed": "one-handed blade",
    "Dual-wield": "dual-wielded blade pair",
    "Two-handed": "two-handed blade",
}
# The parenthetical Chinese on this row is the boss (雷当 / Lei Dang), not the
# weapon, so it is dropped rather than printed as if it were the item's name.
DROP_PARENTHETICAL = {"Thunder Spear"}

# Extra context the acquisition cell does not carry. Kept short on purpose:
# these pages exist to answer "where do I get it, and what does it do".
NOTES = {
    "Wooden Sanguine": "Soul's childhood blade. It is the tutorial weapon and the one the story "
    "opens with, not a placeholder to be thrown away.",
    "Sanguine": "The starting blade and the root of the Tempering tree - every Sanguine-family "
    "transformation is built from it, which is why the starting weapon stays relevant.",
    "Jagged Steel": "Slashes apply Bleeding, so its value is damage that keeps ticking after you "
    "disengage rather than burst on the swing.",
    "The Fanatic's Broken Blade": "The 'drink to make it fly' input is the reason to carry it: the "
    "blade leaves the hand, which turns a melee slot into a short-range projectile.",
    "Tianxuan Bronze Sword": "High shield-break - it is the answer to guards rather than to health "
    "bars, and guard breaks are what drain the Sha-Chi bar.",
    "Soft Snake Sword": "Deflects and cuts threads. Threads are a recurring obstacle type, so this "
    "is a utility slot rather than a damage slot.",
    "Freezing Chaos": "One checklist attributes it to Yucong, No. 34, rather than to the tree itself; "
    "both routes are recorded because sources disagree.",
    "Aureate": "Mimics Zuo Shang's Golden Sword Energy, which makes it the one weapon on the list "
    "that copies a boss moveset instead of a damage type.",
    "Wild Oriole Sword": "Mu Xiaokui's own blade. Picking it up is also how the game signals that the "
    "fight is over rather than merely survived.",
    "Infernal Rouge": "The first Tempering endpoint: Sanguine at level 5 becomes this and grants "
    "Bloodline Rebirth.",
    "Sanguine Twin": "Dual-wield branch of the Sanguine family, taken from the First Meeting with "
    "Yu'er beat in Weeping Creek Valley.",
    "White Serpent & Crimson Viper": "Bai Chilian's paired blades - two elements in one loadout, "
    "which is unusual on a list where most entries are a single weapon.",
    "Parting Hooks": "Guard stance counters melee, so it is a defensive pick that punishes "
    "commitment rather than a damage pick.",
    "Sundering Dual Axes": "Heartpiercer's axes. Slow, wide, and the reason the Three Wardens Fall "
    "trophy can be finished without a second build.",
    "Baishan Stormswords": "Taken from Yubi, No. 21, in the Mandate Encampment training grounds.",
    "Seamless Death": "Hurlable ring blades - the only dual-wield entry whose ranged option is the "
    "weapon itself rather than a Phantom Edge.",
    "Fiend Saws": "Leg-mounted saws taken from the Jade Dancer, so the moveset is a kick rather than "
    "a swing.",
    "The Lady's Fan": "Meng Hua's fan. It sits on the All Dreams Must End gold trophy, which makes it "
    "hard to miss on a full run.",
    "Sanguine Reach": "Two-handed root of the Tempering tree; it becomes Blazing Edge.",
    "Armybreaker": "Cavalrybane's two-hander. Named for the counter it performs: it breaks horses and "
    "guards with the same swing.",
    "Crescent Blade": "Yuding, No. 12's weapon from the Mirage Estate training grounds.",
    "Juggernaut": "Bi Feng's weapon - one of the Two Blade Masters trophies.",
    "Bonesaw": "Found at the Giant's Lair bell rather than dropped by a boss, which makes it one of "
    "the few two-handers you can walk to.",
    "Whiteshadow": "Requires four masks plus the Blizzard Blademaster, so it is the most gated weapon "
    "on the list and ties directly into the true ending checklist.",
    "Blazing Edge": "Second Tempering endpoint: Sanguine Reach plus Scorched Flame shards.",
    "Shadowless Edge": "Listed by one checklist as a Tempering result from Sanguine Twin; not "
    "independently verified, so treat the route as unconfirmed.",
    "Bashpole": "Found at the Main Encampment Gate in the Mandate Encampment - a pickup, not a drop.",
    "Bastion": "Old Man Gen's Hideout in the Village of Lu. The name is the job description.",
    "Dread Axe": "Peng Meng's axe, from The Axemaster's Fall.",
    "Feather Bow": "An outpost pickup in Weeping Creek Valley, and the earliest ranged option most "
    "players will find.",
    "Fire Meteor": "Blaze, Shadow Warden Captain's weapon, from Jingyang Hall in Pangzhen.",
    "Flying Dagger": "Thieves' Camp in Crimson Forest. Cheap to get and easy to forget to equip.",
    "Flying Guillotine": "The Lady's Shrine on the Mountain of Imprisonment.",
    "Heartrend Pipa": "Yuzan's instrument - one of the Four Freed, so it is on the platinum path.",
    "Hunter's Chain Sickle": "Great Waterfall in Weeping Creek Valley.",
    "Iron Gauntlets": "Dropped by Stone Hand Iron Fever.",
    "Loong Trident": "You Loong's trident from the Blackwater Crew Dock, on the Master of the Misty "
    "Waters trophy.",
    "Thunder Spear": "Chang Hong's spear, from the Ancestral Shrine Square in Pangzhen. The Chinese "
    "name printed beside it in the source table is 雷当, which is the boss rather than the weapon.",
    "Tiger Cannon": "Lei Dang's cannon from Mirage Estate, and the reason that region cannot be "
    "skipped on a completionist run.",
    "Wolfjaw": "Dropped by Wu Xuan, the Fallen General.",
    "Flaming Mane": "Repaired through the story rather than found - it is required to open the way "
    "into Pangzhen Slums, so it cannot be missed.",
    "Goldblaze": "Reward for Quick Hand's Request at Zhang's Hideout in Pangzhen, which means it is "
    "tied to the Lost and Found trophy.",
}


def slugify(name):
    base = re.sub(r"\s*\([^)]*\)", "", name).strip()
    base = base.replace("&", " and ").replace("'", "").replace("’", "")
    base = base.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def bare(name):
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def parse_tables():
    page = json.load(open(f"{PAGES}/weapons.json", encoding="utf-8"))
    section = next(s for s in page["sections"] if s["id"] == "every-weapon-and-where-to-find-it")
    html = section["content"]

    blades, edges = [], []
    for table_html in re.findall(r"<table>.*?</table>", html, re.S):
        head = re.search(r"<th>([^<]+)</th>", table_html)
        if not head:
            continue
        is_edge = "Phantom Edge" in head.group(1)
        for tr in re.findall(r"<tr>(.*?)</tr>", table_html, re.S):
            cells = [
                re.sub(r"<[^>]+>", "", c).strip()
                for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
            ]
            if not cells:
                continue
            if is_edge and len(cells) >= 2:
                edges.append({"name": cells[0], "raw": cells[1]})
            elif not is_edge and len(cells) >= 3:
                blades.append({"name": cells[0], "type": cells[1], "raw": cells[2]})
    return blades, edges


def split_obtained(raw, name):
    """Reduce the acquisition cell to where it is, plus any 'defeat X' clause."""
    # A semicolon inside parentheses is part of a remark, not a field separator.
    depth = 0
    split_at = None
    for i, ch in enumerate(raw):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == ";" and depth == 0:
            split_at = i
            break
    if split_at is None:
        where, clause = raw.strip(), ""
    else:
        where, clause = raw[:split_at].strip(), raw[split_at + 1:].strip()

    if clause.lower().startswith("defeat"):
        where = f"{where} - {clause}"
        clause = ""

    if name in PROPERTY:
        return where, PROPERTY[name]
    if clause:
        # Unrecognised clause is provenance, not a mechanic.
        return f"{where} ({clause})", ""
    return where, ""


def build_records():
    blades, edges = parse_tables()
    records = []

    for b in blades:
        name = bare(b["name"])
        display_name = name if name in DROP_PARENTHETICAL else b["name"]
        where, prop = split_obtained(b["raw"], name)
        records.append(
            {
                "slug": slugify(name),
                "name": display_name,
                "slot": "Primary",
                "category": b["type"],
                "obtained": where,
                "property": prop,
                "requirement": REQUIREMENT.get(name, ""),
                "summary": NOTES.get(name, ""),
            }
        )

    for e in edges:
        name = bare(e["name"])
        where, prop = split_obtained(e["raw"], name)
        records.append(
            {
                "slug": slugify(name),
                "name": name,
                "slot": "Secondary (Phantom Edge)",
                "category": EDGE_TYPES.get(name, "Not stated in the source list"),
                "obtained": where,
                "property": prop,
                "requirement": REQUIREMENT.get(name, ""),
                "summary": NOTES.get(name, ""),
            }
        )

    for rec in records:
        if not rec["requirement"]:
            rec.pop("requirement")
        key = bare(rec["name"])
        if key in OBTAINED_OVERRIDE:
            rec["obtained"] = OBTAINED_OVERRIDE[key]
        slot_word = "primary" if rec["slot"] == "Primary" else "secondary"
        noun = CATEGORY_NOUN.get(rec["category"], rec["category"].lower())
        lead = f"{rec['name']} is a {noun} in Phantom Blade Zero's {slot_word} weapon set."
        rec["summary"] = f"{lead} {rec['summary']}".strip() if rec["summary"] else (
            f"{lead} It is obtained at {rec['obtained']}."
        )
    return records


def main():
    records = build_records()
    if any(not r["slug"] for r in records):
        raise SystemExit("slug generation failed")

    seen = {}
    for rec in records:
        if rec["slug"] in seen:
            raise SystemExit(f"duplicate slug {rec['slug']}: {rec['name']} / {seen[rec['slug']]}")
        seen[rec["slug"]] = rec["name"]

    existing = {f[:-5] for f in os.listdir(PAGES) if f.endswith(".json")}
    clashes = sorted(set(seen) & existing)

    json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    prim = sum(1 for r in records if r["slot"] == "Primary")
    print(f"{len(records)} weapon records -> {OUT} (primary {prim}, secondary {len(records) - prim})")
    print(f"records carrying a mechanic note: {sum(1 for r in records if r['property'])}")
    print(f"existing pages that will be refreshed: {len(clashes)}")


if __name__ == "__main__":
    main()
