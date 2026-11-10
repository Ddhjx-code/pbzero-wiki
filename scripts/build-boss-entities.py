#!/usr/bin/env python3
"""Build src/data/entities/bosses.json from the boss-list page plus published fight notes.

Two inputs, both already on disk or already verified:

1. `src/data/pages/boss-list.json` - the roster. Region, story/optional, where the
   fight happens and what it drops. That table was written from published guides
   and is the single source of truth for those four fields.
2. `TIPS` / `STRATEGY` / `PHASES` below - what published fight guides actually say
   about each encounter, paraphrased. Nothing is inferred from a boss's name or
   silhouette: where no guide describes a fight, the record simply has no tips and
   the generator prints "not confirmed" instead of a guess.

Run: python3 scripts/build-boss-entities.py
"""
import json
import re

BOSS_LIST = "src/data/pages/boss-list.json"
OUT = "src/data/entities/bosses.json"

# Per-encounter notes. Key = a unique fragment of the roster name.
TIPS = {
    "Zuo Shang (prologue": [
        "The prologue duel is a tutorial: follow the prompts and practise the parry timing rather than trying to win fast.",
        "Dying here costs nothing, so use it to learn what a red flash feels like before it matters.",
    ],
    "The Hunt": [
        "Learn his attack rhythm first; the punish window is after the follow-up, not after the first swing.",
        "He returns later in the story at a higher level, so the early fight doubles as a rehearsal.",
    ],
    "Jagged Steel": [
        "Stay out of the heavy swing arc and punish the recovery - the weapon is the reward for exactly that.",
        "Guard breaks land faster than chip damage here; he armours through light hits.",
    ],
    "Peng Meng": [
        "The axe swings are unblockable on the overhead - dodge, do not guard.",
        "Break his guard with Sha-Chi attacks to take the Dread Axe.",
    ],
    "Hua, Deadly": [
        "Do not stand in the Flesh Lily fields - they explode on a delay and the tell is easy to miss while dodging her.",
        "Her grab is unblockable; the dodge window is late, after she commits.",
    ],
    "Aberrant Three-Faced": [
        "An optional Challenge Rift fight - bring upgraded gear rather than attempting it early.",
        "Each face changes the attack set, so re-read the silhouette after every phase change.",
    ],
    "Gold-Masked": [
        "A recurring optional challenger tied to the Long Pillar trials - you meet him five times.",
        "He escalates each meeting; do not assume the pattern from the previous fight still holds.",
    ],
    "Acolyte Hansui": [
        "Reached through the scarecrow in Crimson Manor - an optional fight, not a story gate.",
    ],
    "Hua Qianxiao": [
        "Let his fast sword string finish before countering; interrupting mid-combo gets you punished.",
        "He is the boss most likely to teach you that mashing loses to patience.",
    ],
    "Jing Ye": [
        "Dodge the mounted charges rather than trying to block them, and punish between attack sequences.",
    ],
    "Stone Hand Iron Fever": [
        "Break his guard instead of trading - he is built to outlast chip damage.",
        "Reward is the Iron Gauntlets, which change how the next few fights feel.",
    ],
    "Bai Chilian": [
        "Her attack set changes through the fight; avoid committing to long combos.",
        "Keep one blade's stamina in reserve for the phase change.",
    ],
    "Jade Dancer": [
        "Two guardians at once - keep both in frame and never let them bracket you.",
        "Kill order matters more than damage output here.",
    ],
    "Yucong": [
        "An optional rematch that only opens after later progression.",
    ],
    "Zhuo Bi": [
        "Strong guard-breaking attacks are the intended answer - chip damage takes too long.",
    ],
    "Bi Yuan": [
        "Parry his counters and punish the recovery window; he punishes greed harder than aggression.",
    ],
    "Bi Hai": [
        "Controlled pressure beats burst here - he resets if you back off too far.",
    ],
    "Yuzan": [
        "Evade the projectile patterns and hit between them; the pipa volleys have a fixed rhythm.",
        "Dropped into the puppet well after both Bi fights.",
    ],
    "Dusk": [
        "The encounter only opens through the Memory Flowers, so it is easy to walk past.",
        "Manage the summons first - they will interrupt every opening otherwise.",
    ],
    "Mu Xiaokui": [
        "Learn her combination strings before countering; the optional ribbon objectives pay extra.",
        "She fights alongside Yu Yao and Tie Gui, so the arena stays crowded.",
    ],
    "Acolyte Yanru": [
        "An optional encounter near the Terraces, summoned from the rice-field scarecrow.",
    ],
    "Blaze": [
        "Avoid the fire attacks and counter during recovery - the arena punishes standing still.",
        "Bell placement in front of the South Gate marks the fight.",
    ],
    "Cavalrybane": [
        "His strikes are predictable; parry instead of dodging for the faster punish.",
    ],
    "Wu Xuan": [
        "He hides behind a defensive stance - heavy attacks break it faster than a combo.",
    ],
    "Gu Wanyue": [
        "She is immune to damage until her Sha-Chi bar breaks; parries and perfect dodges are the only way to drain it.",
        "Deflect the blue-flash projectile back at her - it marks her and opens the biggest window.",
        "Dodge every red-flash grab, especially the handstand neck-breaker; a clean dodge removes a large chunk of her bar.",
        "When the arena goes dark she can attack from any angle: hold block and react to the flash rather than parrying blind.",
    ],
    "Xie Qiudong": [
        "He heals - sustain pressure instead of backing off, or the fight resets.",
    ],
    "Chang Hong": [
        "Dodge the charges, and expect the mounted phase to change the timing.",
    ],
    "You Loong": [
        "Defeating him gives You Loong's Deluge, which is the answer to several fire hazards later.",
        "Second encounter happens across the water west of Green Serpent House.",
    ],
    "Flame, the Lion": [
        "Counter the fire attacks with water-based abilities; the fight is unmissable in the second half of Pangzhen.",
    ],
    "Soulclaimer": [
        "Break his guard to earn the Parting Hooks; the Dockside Warehouse route is easy to miss.",
    ],
    "Acolyte Lei Ting": [
        "Optional fight reached via the Flaming Mane and the mid-path scarecrow from Old Man Gen's House.",
    ],
    "Corpse-Eating Xue": [
        "His encounter is part of an associated tale rather than a pure gate.",
    ],
    "Wan Jun": [
        "Slow, heavy strikes - punish the recovery rather than trying to interrupt the wind-up.",
    ],
    "Red, the Mysterious": [
        "Expect sudden attacks; keep defensive timing rather than pre-empting.",
    ],
    "Wu Lengshuang": [
        "Stop attacking the moment the purple flash appears - that is her parry, and a counter is already coming.",
        "Dodge when the follow-up glints red, parry when it glints blue.",
        "Her only two-handed swing is always followed by an unblockable spinning slash.",
        "The acrobatic forward flip slash is parryable and is her main gap closer.",
    ],
    "Chief Disciple": [
        "Clear the supporting disciples before focusing the leader; the formation buffs them.",
    ],
    "Yubi": [
        "Break his guard for the Baishan Stormswords; the Training Grounds route is past the main gate.",
    ],
    "Grief-Stricken Jin": [
        "Clear the nearby threats before committing to the boss - the arena does not stay clear.",
    ],
    "One-Eyed Archer": [
        "Close the distance carefully; the whole fight is about not eating ranged hits on approach.",
    ],
    "Yan Qiansui": [
        "Dodge the musical projectiles and exploit the pauses between phrases.",
    ],
    "Heartpiercer": [
        "Won as part of the Shadow Warden fight; rewards the Sundering Dual Axes.",
    ],
    "Blizzard": [
        "Avoid the Frost attacks; the reward is Whiteshadow, one of the better anti-boss blades.",
    ],
    "Acolyte Guhe": [
        "Optional encounter at the Meigu Village East Dock scarecrow.",
    ],
    "Iron Butcher": [
        "Dodge the heavy strikes, then punish recovery - the same rule as most of the Imprisonment roster.",
    ],
    "Bi Feng": [
        "Stay outside the sweeping attacks and use guard breaks instead of trades.",
    ],
    "Kui Yanyan": [
        "Her combinations change; watch a full string before committing to a counter.",
    ],
    "Jade-Face": [
        "Punish the openings rather than forcing them; the reward is Seamless Death.",
    ],
    "Yu Ding": [
        "Avoid the wide sweeps and strike after the recovery - the Crescent Blade puppet telegraphs heavily.",
    ],
    "Leng Tu": [
        "Stay defensive until a safe opening appears; the ascent leaves little room to heal.",
    ],
    "Herald of the Veil": [
        "Fought on the Mount Soulrend ascent, immediately before the endgame stretch.",
    ],
    "Meng Hua": [
        "Normal-ending final boss - attack during the openings rather than trying to out-trade her.",
        "Her fan attacks cover wide arcs; the safe window is after the sweep, not during it.",
    ],
    "Zuo Shang, The True": [
        "High burst damage is the answer: chill him with Whiteshadow, then swap to Blazing Edge once he is guard-broken or frozen.",
        "You Loong's Deluge staggers him flat, which is the most reliable way to control the pace of the fight.",
        "In phase 1, when he turns his back he is either throwing a spinning sword or setting a counter-parry - do not swing blindly.",
        "Phase 2 is a defensive fight: block and parry the melee, evade the projectiles, and wait for the Sha-Chi break instead of forcing damage.",
    ],
    "The Last Battle": [
        "Triggers immediately after Zuo Shang and only if the true-ending checklist is complete - there is no separate approach.",
    ],
    "Saw and the Crusher": [
        "Separate the pair where possible; fighting both in the same cone is what kills runs.",
    ],
    "Lei Dang": [
        "Two phases - the second changes his attack set, so spend phase one learning tells rather than racing the bar.",
        "The Tiger Cannon is the reward, and it is worth the two attempts this fight usually takes.",
    ],
    "Qiu Feng": [
        "Defensive timing matters more than damage here; his strings punish an early counter.",
    ],
    "Mo Yuan": [
        "Optional, and tied to Soul Tempering materials rather than a weapon - worth doing before the final stretch.",
    ],
}

PHASES = {
    "Zuo Shang, The True": [
        {"when": "Sword Barrage", "watch": "A swarm of swords fills the arena", "answer": "Spam dodge - do not try to parry it"},
        {"when": "Gathering Winds", "watch": "Red flash while wind and leaves gather", "answer": "Unblockable - dodge after the flash"},
        {"when": "Ephemeral Swords", "watch": "Five swords fire in sequence, then a leap", "answer": "Parry the sword swing, dodge the grab that follows"},
        {"when": "Ephemeral Spears", "watch": "Four spears, then a dash", "answer": "Unblockable thrust - dodge sideways, not back"},
        {"when": "Back-turned stance", "watch": "He faces away from you", "answer": "Expect a spinning projectile or a counter-parry - hold your swing"},
    ],
    "Gu Wanyue": [
        {"when": "Sleeve swipes", "watch": "Close-to-mid range strings", "answer": "Parry - this is the main Sha-Chi drain"},
        {"when": "Blue projectile", "watch": "Slow fireball", "answer": "Perfect parry to deflect it back; applies vulnerability"},
        {"when": "Neck Breaker", "watch": "Handstand leap onto your shoulders, red flash", "answer": "Dodge - removes a large chunk of her bar"},
        {"when": "Darkness phase", "watch": "Arena fades to black", "answer": "Hold block, react to the flash, do not parry blind"},
    ],
    "Wu Lengshuang": [
        {"when": "Purple flash", "watch": "She parries you mid-string", "answer": "Stop attacking immediately"},
        {"when": "Counter after purple", "watch": "Red glint = unblockable, blue = parryable", "answer": "Dodge the red, parry the blue"},
        {"when": "Two-handed swing", "watch": "Only attack she uses two hands for", "answer": "Always followed by an unblockable spin - dodge it"},
        {"when": "Acrobatic slash", "watch": "Forward flip, wide slash", "answer": "Parryable - this is your Ghoststep opening"},
    ],
}

STRATEGY = {
    "Gu Wanyue": [
        "Gu Wanyue is the fight that teaches the game's defensive loop, because for most of it she cannot be damaged at all: "
        "while the smoke effect is on her body, attacks pass through. The only way in is to empty her Sha-Chi bar, and the only "
        "way to empty it is to parry and dodge correctly.",
        "The rhythm is drain, stagger, burst: parry the sleeve strings, deflect the projectile, dodge the grabs, then unload "
        "everything the moment she staggers. Back off the instant she recovers and start again. Healing before the arena, not "
        "during it, is the difference between a clean attempt and a wipe.",
    ],
    "Zuo Shang, The True": [
        "The true-ending final boss is a two-phase exam on everything the game has taught. Phase 1 is readable: he telegraphs, "
        "and the back-turned stance is a trap rather than an opening. Phase 2 removes the luxury of forcing damage - his "
        "poise is high enough that reckless combos get punished, so the fight becomes block, parry, evade until the Sha-Chi "
        "bar breaks, then a single committed burst.",
        "The build that makes it tractable is a freeze into burst swap: Whiteshadow to chill and slow him, Blazing Edge for the "
        "damage window once he is frozen or guard-broken, with You Loong's Deluge available to knock him down when the pressure "
        "needs resetting.",
    ],
    "Wu Lengshuang": [
        "Wu Lengshuang is a parry duel rather than a damage race. She deflects constantly, and every deflection is a purple "
        "flash that cancels your damage and leads straight into a counter whose colour tells you what to do: red means dodge, "
        "blue means parry, no colour means block or reposition.",
        "The mistake that loses this fight is pressing through the purple flash. Treat it as a stop signal, react to the counter, "
        "and take the acrobatic flip slash as your one reliable Ghoststep opening.",
    ],
}

# The roster spells a few names differently from the guides; normalise for matching.
ALIASES = {
    "you loong, blackwater crew leader": "You Loong",
    "you, loong, frenzied blackwater crew leader": "You Loong",
}

# Slugs already live and indexed. Reusing them means the stale pre-launch page at that
# URL is replaced by the real one instead of a second page competing with it.
OVERRIDE_SLUGS = {
    "Lei Dang": "leidang-boss",
    "Chang Hong, the Thunder Spear (长鸿)": "changhong-boss",
    "Chief Disciple of the Seven-Stars Formation": "seven-stars-boss",
    "Flame, the Lion Dance Grandmaster (舞狮尊主 烈焰)": "lion-dance-boss",
    "Mu Xiaokui, Young Mistress of the Order (沐小葵)": "xiaokui-guarded-fight",
    "Jade-Face": "huangxing-boss",
    "Jade Dancer and Iron Fiend": "double-boss-fight",
}


def slugify(name):
    """Canonical URL. Keep the epithet (it is what people search), drop the Chinese gloss."""
    base = re.sub(r"\([^)]*\)", "", name).strip()
    base = re.sub(r"^The\s+", "", base)
    base = base.lower().replace("&", " and ")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def find(mapping, name):
    key = name.lower()
    if key in ALIASES:
        key = ALIASES[key].lower()
    for frag, value in mapping.items():
        if frag.lower() in key:
            return value
    return None


def main():
    page = json.load(open(BOSS_LIST, encoding="utf-8"))
    rows = []
    for section in page["sections"]:
        content = section.get("content", "")
        if "<table" not in content:
            continue
        region = re.sub(r"\s+", " ", section["title"]).strip()
        for tr in re.findall(r"<tr>(.*?)</tr>", content, re.S)[1:]:
            cells = [re.sub("<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(cells) >= 4:
                rows.append({"region": region, "name": cells[0], "kind": cells[1], "where": cells[2], "drop": cells[3]})

    seen = {}
    out = []
    for row in rows:
        name = row["name"]
        slug = OVERRIDE_SLUGS.get(name) or slugify(name)
        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 1

        kind = row["kind"]
        drop = row["drop"]
        drops = [] if drop.lower().startswith(("not documented", "none")) else [drop]

        summary = (
            f"{name} is a {kind.lower()} encounter in {row['region']}, found at {row['where'].rstrip('.')}."
        )
        if drops:
            summary += f" Beating it yields {drops[0]}."

        rec = {
            "slug": slug,
            "name": name,
            "kind": kind,
            "region": row["region"],
            "location": row["where"],
            "act": row["region"],
            "summary": summary,
        }
        if drops:
            rec["drops"] = drops
        tips = find(TIPS, name)
        if tips:
            rec["tips"] = tips
        phases = find(PHASES, name)
        if phases:
            rec["phases"] = phases
        strategy = find(STRATEGY, name)
        if strategy:
            rec["strategy"] = strategy
        out.append(rec)

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with_tips = sum(1 for r in out if r.get("tips"))
    with_phases = sum(1 for r in out if r.get("phases"))
    print(f"{len(out)} bosses written -> {OUT}")
    print(f"  {with_tips} have published fight notes, {with_phases} have attack tables, "
          f"{len(out) - with_tips} stay honest about having none")
    dup = [s for s, n in seen.items() if n > 1]
    if dup:
        print("  disambiguated slugs:", ", ".join(dup))


if __name__ == "__main__":
    main()
