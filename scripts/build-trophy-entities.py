#!/usr/bin/env python3
"""Build src/data/entities/trophies.json - the 36-trophy PS5 list.

Tier split (1 platinum / 3 gold / 14 silver / 18 bronze) is the consensus of
Game8, Gfinity, TechWiser and One More Game. Where those sources disagree the
record says so rather than picking a winner - see the note fields.

Usage: python3 scripts/build-trophy-entities.py
"""
import json
import os
import re

PAGES = "src/data/pages"
OUT = "src/data/entities/trophies.json"

# Game8's "Hidden Trophies" block lists exactly 13. The Chinese-language list
# marks more than that, so only the 13 both sets support are marked hidden.
HIDDEN = {
    "The Lion's Spirit Lives On",
    "Sword Against the Seven-Stars",
    "Crossroads of Blood",
    "Nothing Goes to Waste",
    "All Return to Dust",
    "The White Shadow",
    "Saw It Through",
    "All Dreams Must End",
    "Master of the Misty Waters",
    "The Four Freed",
    "The Two Blade Masters",
    "Three Wardens Fall",
    "With Heart and Blood",
}

# Nine side-quest trophies expire without a warning in-game, plus one optional
# boss. Everything else stays reachable through free-roam or a second run.
MISSABLE = {
    "Forbidden Arts Beneath the Lake",
    "Phantom and Blade",
    "Even Trees Know Sorrow",
    "The Last of Baishan",
    "Together Till the End",
    "A Wanderer's Honor",
    "Spectral Blade",
    "The Healer's Legacy",
    "Lost and Found",
    "Scarlet Wraithblade",
}

TROPHIES = [
    (
        "Defy Destiny",
        "Platinum",
        "Earn every other trophy in the list.",
        "The platinum is automatic once the other 35 are done - nothing extra is "
        "required, and no difficulty setting gates it. That single fact is why the "
        "whole set can be finished in one run.",
        [],
    ),
    (
        "The Heart's Journey",
        "Bronze",
        "Complete the Prologue - escape the pursuers on the Main Road.",
        "The first trophy in the game and the one nobody can miss. It doubles as the "
        "moment the red and blue attack flashes are taught.",
        [],
    ),
    (
        "With Heart and Blood",
        "Gold",
        "Reach the All Comes to Light ending - the true ending.",
        "This is the gold that makes the true ending compulsory for the platinum. The "
        "prerequisite checklist is on the true ending page: nine purple side quests, "
        "four retainer masks, five dragon pillars and both crystal puppet eyes.",
        [
            "Finish all nine purple-marked side quests before climbing Mount Soulrend.",
            "Collect the four retainer masks.",
            "Light all five dragon pillars.",
            "Obtain both crystal puppet eyes.",
            "Complete the final boss chain without leaving the area.",
        ],
    ),
    (
        "All Dreams Must End",
        "Gold",
        "Reach the ending where all schemes come to nothing - the Meng Hua route.",
        "The ordinary ending rather than the true one, which means it is easy to reach "
        "by accident on a first run and impossible to skip if you are chasing the "
        "platinum anyway.",
        [],
    ),
    (
        "The Four Freed",
        "Gold",
        "Defeat all four Great Puppets: Yuzan, Yubi, Yuding and Yucong.",
        "One trophy hiding four fights, and the one that forces a detour into the "
        "Puppet Testing Grounds and the Mirage Estate. All four are named bosses with "
        "their own entity pages.",
        [],
    ),
    (
        "The Hunt",
        "Silver",
        "Defeat the Hunt, Hunter of the Order.",
        "A named story boss. The fight is the first real test of the parry window "
        "rather than the dodge.",
        [],
    ),
    (
        "The Shattered Mirror",
        "Silver",
        "Defeat Bai Chilian, Lady of the Twin Serpents.",
        "Drops the White Serpent and Crimson Viper paired blades, so the reward is a "
        "loadout change rather than a stat bump.",
        [],
    ),
    (
        "Will We Meet Again?",
        "Silver",
        "Defeat Mu Xiaokui, the Young Mistress of the Order.",
        "Beating her unlocks the third phase of the encounter, so a first attempt that "
        "ends early is not the same fight as the one the trophy is named after.",
        [],
    ),
    (
        "The Lion's Spirit Lives On",
        "Silver",
        "Defeat Flame, the Lion Dance Grandmaster.",
        "A hidden boss tied to the Memory Flower count, which is why flower collection "
        "is not optional on a completionist run.",
        [],
    ),
    (
        "Sword Against the Seven-Stars",
        "Silver",
        "Defeat the Chief Disciple of the Seven-Stars.",
        "The Seven-Stars are a formation rather than a single enemy, so the fight is "
        "about reading several attackers at once. See the disambiguation page for what "
        "the name refers to in each context.",
        [],
    ),
    (
        "Crossroads of Blood",
        "Silver",
        "Defeat Huangxing, the Kunlun Renegade.",
        "One of the optional region bosses that is easy to walk past if you take the "
        "main road through.",
        [],
    ),
    (
        "Nothing Goes to Waste",
        "Silver",
        "Defeat the Puppet Scavenger.",
        "Sits in the same area as Acolyte Hansui, which is why guides usually cover "
        "the two together.",
        [],
    ),
    (
        "All Return to Dust",
        "Silver",
        "Defeat Lei Dang, the Order's Envoy.",
        "A Mirage Estate encounter. The region was missing from the first version of "
        "the boss roster entirely, so check the Mirage Estate section if you cannot "
        "find the fight.",
        [],
    ),
    (
        "The White Shadow",
        "Silver",
        "Defeat the Blizzard Blademaster.",
        "The same encounter that gates the Whiteshadow weapon, which needs four "
        "retainer masks on top of the kill.",
        [],
    ),
    (
        "Saw It Through",
        "Silver",
        "Defeat the Saw and the Crusher.",
        "A paired fight - one fast, one heavy. Fighting both inside the same cone is "
        "what ends runs, so separate them first.",
        [],
    ),
    (
        "Collector's Notes",
        "Silver",
        "Collect 30 accessories.",
        "Game8 lists a different silver in this slot - Unsung Legend, for completing "
        "the Enemy Journal - and does not list this one at all. Four other lists carry "
        "Collector's Notes with the 30-accessory requirement, so that is the version "
        "recorded here. If your list shows Unsung Legend instead, the collectible "
        "trophy on your platform is the journal rather than the accessories.",
        [],
    ),
    (
        "Forbidden Arts Beneath the Lake",
        "Silver",
        "Complete the side quest Secrets at the Heart of the Lake.",
        "Missable. One of the nine purple side quests, and one of the two that also "
        "carries a silver rather than a bronze.",
        [],
    ),
    (
        "Phantom and Blade",
        "Silver",
        "Complete the side quest Bloodline Awakening.",
        "Missable. Tied to the dragon pillar chain - the pillars are the quest's "
        "collectible, so this and the true ending share a checklist item.",
        [],
    ),
    (
        "Even Trees Know Sorrow",
        "Silver",
        "Complete the side quest Heart of the Banyan.",
        "Missable. The third of the three silver quest trophies and the easiest to "
        "leave until too late, because the Banyan area stops being reachable.",
        [],
    ),
    (
        "The Last of Baishan",
        "Bronze",
        "Complete the side quest Secrets of the Baishan Sect.",
        "Missable. It has to be accepted before the Bai Chilian fight, not after - "
        "accepting it late is the single most common way this one is lost.",
        [],
    ),
    (
        "Together Till the End",
        "Bronze",
        "Complete the side quest The Journey Home.",
        "Missable. Old Man Gen's request, and the window closes on entering Pangzhen.",
        [],
    ),
    (
        "A Wanderer's Honor",
        "Bronze",
        "Complete the side quest Young Master Lan.",
        "Missable. Same window as The Journey Home - both start in the Village of Lu, "
        "so both should be finished before moving on.",
        [],
    ),
    (
        "Spectral Blade",
        "Bronze",
        "Complete the side quest A Severed Mindseal.",
        "Missable. The quest is also the source of the Soft Snake Sword's thread-"
        "cutting utility, so finishing it early pays for itself.",
        [],
    ),
    (
        "The Healer's Legacy",
        "Bronze",
        "Complete Flesh Lily, Apprentice Healer and A Healer's Mercy.",
        "Missable, and the one trophy people assume is three quests or one. It is "
        "three, and delivering a single flower is not enough.",
        [],
    ),
    (
        "Lost and Found",
        "Bronze",
        "Complete every one of Quick Hand's requests.",
        "Missable. The final reward is the Goldblaze Phantom Edge, so the trophy and a "
        "weapon sit behind the same chain.",
        [],
    ),
    (
        "A Tempered Ten",
        "Bronze",
        "Perform Tempering on 10 weapons.",
        "Counting, not difficulty. Temper the cheap Sanguine-family blades first - each "
        "transformation counts separately.",
        [],
    ),
    (
        "Overwhelming Force",
        "Bronze",
        "Upgrade a single weapon to level 30.",
        "One weapon only. The cap is 30 for every weapon, so this is a materials "
        "question rather than a choice about which blade.",
        [],
    ),
    (
        "Listen to Every Flower",
        "Bronze",
        "Collect 10 Memory Flowers.",
        "Memory Flowers also gate the Dusk encounter and the Lion Dance Grandmaster, so "
        "this one doubles as progress rather than being a detour.",
        [],
    ),
    (
        "Phantom Arsenal",
        "Bronze",
        "Perform Tempering on 10 Phantom Edges.",
        "Tempering is refundable, so materials spent here are not lost - the only cost "
        "is the run back to the forge.",
        [],
    ),
    (
        "Skill Over Strength",
        "Bronze",
        "Upgrade a single Phantom Edge to level 30.",
        "The secondary-slot twin of Overwhelming Force. Same cap, different slot.",
        [],
    ),
    (
        "The Axe's Grudge",
        "Bronze",
        "Defeat Axemaster Peng Meng.",
        "Drops the Dread Axe. A straight fight with a long wind-up, so it is the "
        "cleanest place to practise parrying a heavy.",
        [],
    ),
    (
        "Scarlet Wraithblade",
        "Bronze",
        "Defeat Hua, the Bride.",
        "Missable, because she is optional. Kill her before leaving the opening "
        "region - the roadmap's first warning is exactly this fight.",
        [],
    ),
    (
        "A Thousand Cups Drained",
        "Bronze",
        "Defeat Hua Qianxiao, the Sword Fanatic.",
        "The drunk boss. His timing is deliberately irregular, which makes parrying by "
        "rhythm fail - read the flash colour instead.",
        [],
    ),
    (
        "Master of the Misty Waters",
        "Bronze",
        "Defeat Blackwater Leader You Loong, Zither Maiden Yan Qiansui and the "
        "One-Eyed Archer.",
        "One trophy, three fights, all in the Meigu Lake region. Drops include the "
        "Loong Trident.",
        [],
    ),
    (
        "The Two Blade Masters",
        "Bronze",
        "Defeat Zhu Yuan and Commander Bi Feng.",
        "Two separate encounters in different regions, so this is a checklist item "
        "rather than a single set piece.",
        [],
    ),
    (
        "Three Wardens Fall",
        "Bronze",
        "Defeat the three Shadow Wardens: Cavalrybane, Soulclaimer and Heartpiercer.",
        "Three fights, and Heartpiercer drops the Sundering Dual Axes, which is why "
        "many builds end up finishing this one first.",
        [],
    ),
]


def slugify(name):
    base = name.replace("'", "").replace("’", "").replace("?", "")
    base = base.replace("&", " and ")
    base = base.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def main():
    existing = {f[:-5] for f in os.listdir(PAGES) if f.endswith(".json")}
    records, seen = [], {}
    for name, tier, how, summary, steps in TROPHIES:
        slug = slugify(name)
        if slug in existing or slug in seen:
            # The Hunt is also a boss page, so the trophy needs its own URL.
            slug = f"{slug}-trophy"
        if slug in seen:
            raise SystemExit(f"duplicate slug {slug}")
        seen[slug] = name
        rec = {
            "slug": slug,
            "name": name,
            "rarity": tier,
            "how": how,
            "summary": summary,
            "missable": "Yes" if name in MISSABLE else "No",
        }
        if name in HIDDEN:
            rec["hidden"] = True
        if steps:
            rec["steps"] = steps
        records.append(rec)

    tiers = {}
    for r in records:
        tiers[r["rarity"]] = tiers.get(r["rarity"], 0) + 1
    if len(records) != 36:
        raise SystemExit(f"expected 36 trophies, built {len(records)}")
    expected = {"Platinum": 1, "Gold": 3, "Silver": 14, "Bronze": 18}
    if tiers != expected:
        raise SystemExit(f"tier split wrong: {tiers} (expected {expected})")

    json.dump(records, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(records)} trophy records -> {OUT}")
    print(f"  tiers: {tiers}")
    print(f"  hidden: {sum(1 for r in records if r.get('hidden'))}  missable: {sum(1 for r in records if r['missable'] == 'Yes')}")


if __name__ == "__main__":
    main()
