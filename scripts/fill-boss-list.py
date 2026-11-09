#!/usr/bin/env python3
"""Rebuild /boss-list from post-launch sources.

The page shipped listing 11 pre-launch encounters and said the rest was
unanswerable. It is answerable now. Boss names come from NoobFeed's regional
rundown; drops are cross-checked against the weapon checklists; the
Chinese names come from 游侠网 and OSLink. Where the sources conflict the page
says so rather than picking a winner.
"""
import json
import os

PAGES = "src/data/pages"
STAMP = "2026-11-09"
LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'

# region, boss, type, location / trigger, drop ("" = unknown)
ROSTER = [
    ("Prologue & Weeping Creek Valley", "Zuo Shang (prologue duel)", "Story (tutorial)",
     "Opening pursuit sequence", "None - scripted fight"),
    ("Prologue & Weeping Creek Valley", "The Hunt", "Story", "Main road pursuit, returns later",
     "Hunter's Chain Sickle (Great Waterfall, same region)"),
    ("Prologue & Weeping Creek Valley", "Jagged Steel, the Frenzied Brute",
     "Story", "Rustblade Pavilion bell", "Jagged Steel"),
    ("Prologue & Weeping Creek Valley", "Peng Meng, the Axemaster (斧老大 彭猛)",
     "Story", "The Axemaster's Fall", "Dread Axe"),
    ("Prologue & Weeping Creek Valley", "Hua, Deadly Betrothed (新娘阿花)",
     "Optional", "Flesh Lily Fields", "Scarlet Wraithblade"),
    ("Prologue & Weeping Creek Valley", "Aberrant Three-Faced Puppet",
     "Optional", "Challenge Rift", "Unknown"),
    ("Prologue & Weeping Creek Valley", "The Gold-Masked One", "Recurring optional",
     "Lóng Pillar trials, five times", "None - pillar progress"),
    ("Crimson Manor & Crimson Forest", "Puppet Scavenger", "Optional", "Crimson Manor",
     "Unknown"),
    ("Crimson Manor & Crimson Forest", "Acolyte Hansui", "Optional", "Crimson Manor, via scarecrow",
     "Frost Mask"),
    ("Crimson Manor & Crimson Forest", "Hua Qianxiao, the Sword Fanatic (剑痴 花千笑)",
     "Story", "Pangzhen Bridge Overlook", "The Fanatic's Broken Blade"),
    ("Crimson Manor & Crimson Forest", "Jing Ye, the Outlaw (亡命徒 荆野)",
     "Story", "Crimson Forest", "Outlaw Warblade"),
    ("Crimson Manor & Crimson Forest", "Stone Hand Iron Fever (拳痴 铁狂)",
     "Optional", "Crimson Forest", "Iron Gauntlets"),
    ("Crimson Manor & Crimson Forest", "Bai Chilian, Lady of the Twin Serpents (双蛇夫人 白赤练)",
     "Story - region finale", "Threadbound Great Tree, after the mirror puzzle",
     "White Serpent & Crimson Viper"),
    ("Crimson Manor & Crimson Forest", "Jade Dancer and Iron Fiend", "Optional", "Crimson Forest",
     "Fiend Saws (via the Mu Xiaokui encounter)"),
    ("Crimson Manor & Crimson Forest", "Yucong, the Twisted Puppet (No. 34)", "Optional rematch",
     "Returns later in the story", "Freezing Chaos"),
    ("Village of Lu", "Zhuo Bi, the Gatekeeper", "Story", "Village of Lu approach", "Bastion"),
    ("Village of Lu", "Master Bi Yuan", "Story", "Puppet Testing Grounds route",
     "Tianxuan Bronze Sword"),
    ("Village of Lu", "Master Bi Hai", "Story", "Village of Lu", "Unknown"),
    ("Village of Lu", "Yuzan, the Musician Puppet (三号乐偶师 玉瓒)", "Story",
     "Drop into the puppet well after Bi Yuan and Bi Hai", "Heartrend Pipa"),
    ("Village of Lu", "Dusk, the Puppeteer", "Optional", "Unlocked through Memory Flowers", "Unknown"),
    ("Village of Lu", "Mu Xiaokui, Young Mistress of the Order (沐小葵)", "Story",
     "Village of Lu, with Yu Yao and Tie Gui", "Wild Oriole Sword"),
    ("Village of Lu", "Acolyte Yanru", "Optional", "Terrace bell, north side, rice field scarecrow",
     "Blazing Mask"),
    ("Pangzhen", "Blaze, Shadow Warden Captain (鬼差队长 火流星)", "Story",
     "In front of the South Gate bridge bell", "Fire Meteor"),
    ("Pangzhen", "Cavalrybane (鬼差高手 斩骑)", "Optional", "Statue Grounds bell, north of the long bridge",
     "Armybreaker"),
    ("Pangzhen", "Wu Xuan, the Fallen General (堕落将军 武轩)", "Story",
     "Back Street Archway bell", "Wolfjaw"),
    ("Pangzhen", "Gu Wanyue (女妖 骨婉约)", "Story", "The Singing Pond bell", "Unknown"),
    ("Pangzhen", "Xie Qiudong, the Divine Healer (神医 谢秋冬)", "Story",
     "Up from the Three Ships Well", "Unknown"),
    ("Pangzhen", "Chang Hong, the Thunder Spear (长鸿)", "Story", "Pangzhen", "Thunder Spear"),
    ("Pangzhen", "You Loong, Blackwater Crew Leader (游龙)", "Optional",
     "Green Serpent House, then the water to the west", "You Loong's Deluge / Loong Trident"),
    ("Pangzhen", "Flame, the Lion Dance Grandmaster (舞狮尊主 烈焰)", "Story - region finale",
     "Second half of Pangzhen, unmissable", "Flaming Mane"),
    ("Pangzhen", "Soulclaimer (勾魂)", "Optional", "Dockside Warehouse, down and right", "Parting Hooks"),
    ("Pangzhen", "Zhu Yuan", "Optional", "Pangzhen", "Unknown"),
    ("Pangzhen", "Acolyte Lei Ting", "Optional",
     "Pangzhen Slums via the Flaming Mane; scarecrow mid-path from Old Man Gen's House", "Thunder Mask"),
    ("Mandate Encampment", "Corpse-Eating Xue", "Story", "Mandate Encampment", "Unknown"),
    ("Mandate Encampment", "Wan Jun, the Coppermaul", "Story", "Mandate Encampment", "Unknown"),
    ("Mandate Encampment", "Red, the Mysterious Wraith", "Story", "Mandate Encampment", "Unknown"),
    ("Mandate Encampment", "Wu Lengshuang, the Soft Sword (柔剑 武林霜)", "Optional",
     "Path of the Baishan's Fall", "Soft Snake Sword"),
    ("Mandate Encampment", "Chief Disciple of the Seven-Stars Formation", "Story",
     "Clear the disciples before the leader", "Unknown"),
    ("Mandate Encampment", "Yubi, the Swordfighter Puppet (No. 21)", "Optional",
     "Training Grounds, past the main gate", "Baishan Stormswords"),
    ("Meigu Lake", "Grief-Stricken Jin", "Story", "Meigu Lake", "Unknown"),
    ("Meigu Lake", "One-Eyed Archer (独眼弓客)", "Optional", "Meigu Lake", "Unknown"),
    ("Meigu Lake", "Yan Qiansui, the Zither Maiden (烟千岁)", "Optional", "Meigu Lake", "Unknown"),
    ("Meigu Lake", "Heartpiercer (穿心者)", "Optional", "White Serpent House", "Sundering Dual Axes"),
    ("Meigu Lake", "Blizzard Blademaster (暴雪刀主)", "Optional - true ending gate",
     "Whiteshadow's Fall bell, inside the Illusion Realm", "Whiteshadow"),
    ("Meigu Lake", "Acolyte Guhe", "Optional", "Meigu Village East Dock, scarecrow", "Venom Mask"),
    ("Mountain of Imprisonment", "Iron Butcher", "Story", "Mountain of Imprisonment", "Unknown"),
    ("Mountain of Imprisonment", "Bi Feng, Giant Saber Commander (巨刀统领 白峰)", "Story",
     "Commander's Platform", "Juggernaut"),
    ("Mountain of Imprisonment", "Kui Yanyan", "Story", "Mountain of Imprisonment", "Unknown"),
    ("Mountain of Imprisonment", "Jade-Face", "Optional", "The Lady's Shrine", "Seamless Death"),
    ("Mountain of Imprisonment", "Yu Ding, No. 12 Crescent Blade Puppet", "Story",
     "Training Grounds, Mirage Estate", "Crescent Blade"),
    ("Mount Soulrend & endgame", "Leng Tu", "Story", "Mount Soulrend ascent", "Unknown"),
    ("Mount Soulrend & endgame", "Herald of the Veil", "Story", "Mount Soulrend", "Unknown"),
    ("Mount Soulrend & endgame", "Meng Hua, Merciful Lady of the Blossom Veil (莫华)", "Story",
     "Peak of Mount Soulrend - true ending checkpoint", "The Lady's Fan"),
    ("Mount Soulrend & endgame", "Zuo Shang, The True Long", "Story - final boss",
     "Peak of Mount Soulrend", "Aureate"),
    ("Mount Soulrend & endgame", "The Last Battle", "True ending only",
     "Triggers immediately after Zuo Shang if the checklist is complete", "None"),
    ("Mount Soulrend & endgame", "The Saw and the Crusher", "Optional", "Endgame", "Unknown"),
]

REGION_ORDER = [
    "Prologue & Weeping Creek Valley",
    "Crimson Manor & Crimson Forest",
    "Village of Lu",
    "Pangzhen",
    "Mandate Encampment",
    "Meigu Lake",
    "Mountain of Imprisonment",
    "Mount Soulrend & endgame",
]


def table_for(region):
    rows = [r for r in ROSTER if r[0] == region]
    body = "".join(
        f"<tr><td><strong>{name}</strong></td><td>{kind}</td><td>{where}</td>"
        f"<td>{drop if drop != 'Unknown' else '<span style=\"color:#8a8a99\">Not documented</span>'}</td></tr>"
        for _, name, kind, where, drop in rows
    )
    return (
        "<table><thead><tr><th>Boss</th><th>Type</th><th>Where</th><th>Drop</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


total = len(ROSTER)
story = sum(1 for r in ROSTER if r[2].startswith("Story"))
optional = total - story

sections = [
    {
        "id": "short-answer",
        "title": "The Short Answer",
        "content": (
            f"<p>The table below names <strong>{total} encounters</strong> across eight regions - "
            f"{story} on the story path and {optional} optional or recurring. S-GAME's own figure is "
            "<strong>50 or more bosses</strong>, so this list is close to the full roster but not guaranteed to be "
            "every optional duel in the game.</p>"
            "<p>This page replaced an older version that listed 11 bosses and labelled the rest unanswerable. That version "
            "was honest for its date - it was written before the 29 October 2026 release, when the only evidence was demos and "
            "trailers. The release made the question answerable, so the pre-launch roster is gone rather than kept alongside.</p>"
            f"<p>What is still not documented: elemental weaknesses and resistances for most fights. The game does have "
            "elemental interactions - water attacks strip Flame's fire, frost builds on you against the Blizzard Blademaster - "
            "but no outlet has published a per-boss weakness table, and this page will not invent one. Strategy per fight lives "
            f"on <a href=\"/boss-guide\" {LINK}>the boss guide</a>.</p>"
        ),
    }
]

for region in REGION_ORDER:
    rid = region.lower().replace(" & ", "-").replace(" ", "-")
    sections.append({
        "id": rid,
        "title": region,
        "content": table_for(region),
    })

sections += [
    {
        "id": "drops",
        "title": "What Bosses Drop, and Why It Matters",
        "content": (
            "<p>Every boss that matters drops its weapon, and the pattern is consistent enough to plan around: "
            "the fight teaches the weapon. Beat Hua Qianxiao and you get The Fanatic's Broken Blade, a sword you drink from "
            "to make it fly. Beat Hua, Deadly Betrothed and you get the Scarlet Wraithblade, which lets Soul grow spider lilies "
            "the way she did. Beat Flame and you get the Flaming Mane, fire against the frost you will meet later.</p>"
            "<p>That is why this list doubles as a weapon checklist. Five weapons in the roster above are not drops at all - "
            "they are found on racks or created by Tempering - and those are marked in the weapon guide instead: "
            "<strong>Jagged Steel</strong>, <strong>Bonesaw</strong>, <strong>Tianxuan Bronze Sword</strong>, "
            "<strong>Soft Snake Sword</strong> and the four Sanguine transformations.</p>"
            "<p>Sources disagree on two entries and the tables follow the more specific one: "
            "<strong>Freezing Chaos</strong> is listed by one checklist as a drop from Yucong, No. 34 and by another as a "
            "Crimson Forest pickup at the Threadbound Great Tree; <strong>The Fanatic's Broken Blade</strong> is listed as "
            "Hua Qianxiao's drop and also as a Crimson Forest pickup. In both cases the boss and the region are the same "
            "place, so the practical answer does not change.</p>"
        ),
    },
    {
        "id": "optional",
        "title": "The Optional Fights You Should Not Skip",
        "content": (
            "<p>Four optional bosses are load-bearing for the true ending, which makes 'optional' misleading:</p>"
            "<ul>"
            "<li><strong>The Gold-Masked One</strong> - five duels, one per Lóng Pillar. Losing leaves the pillar standing.</li>"
            "<li><strong>Blizzard Blademaster</strong> - drops Whiteshadow, and sits in the Illusion Realm behind the "
            "four-mask gate. Acolyte Guhe's mask is in the same region, so the two steps chain.</li>"
            "<li><strong>The four Acolytes</strong> - Yanru, Lei Ting, Guhe, Hansui. Their masks are the key to the "
            "Meigu Lake mirror.</li>"
            "<li><strong>Crimson Manor's secret boss</strong> - one of the two Crystal Puppet Eyes.</li>"
            "</ul>"
            f"<p>The full dependency chain is on <a href=\"/true-ending\" {LINK}>the true ending checklist</a>. "
            "For the fights themselves, the three habits that hold across the whole roster: parry the blue flash, "
            "dodge the red flash, and swap weapons to refill Sha-Chi instead of backing off.</p>"
        ),
    },
    {
        "id": "count",
        "title": "How Many Bosses Are There, Really",
        "content": (
            "<p>Three numbers circulate and they measure different things. S-GAME's director said <strong>50 or more</strong> "
            "before release. This page names "
            f"<strong>{total}</strong> distinct encounters. Trophy lists imply a fourth count by grouping fights: the "
            "<em>The Four Freed</em> trophy covers Yuzan, Yubi, Yuding and Yucong as one entry, <em>Three Wardens Fall</em> "
            "covers Cavalrybane, Soulclaimer and Heartpiercer as one, and <em>Master of the Misty Waters</em> groups "
            "You Loong, Yan Qiansui and the One-Eyed Archer.</p>"
            "<p>So the roster is comfortably above 50 once rematches and Challenge Rift variants are counted, and any single "
            "published number below that is probably counting trophies rather than fights.</p>"
        ),
    },
    {
        "id": "sources",
        "title": "Sources",
        "content": (
            "<p>Regional roster: NoobFeed's all-bosses guide, which is the only source found that organises the full set by "
            "region. Drops: AxeeTech's 51-item weapon checklist, Gamer.org's location guide and Quora Marketing's "
            "Pangzhen-specific list. Chinese names: 游侠网's all-boss strategy compilation and OSLink's main-line boss table. "
            "Trophy groupings: Game8 and Fextralife.</p>"
            "<p>Every boss above appears in at least two of those sources except the ones marked "
            "<em>Not documented</em> for drops, which appear in the roster but in no loot list.</p>"
        ),
    },
]

page = {
    "title": "Phantom Blade Zero Boss List - All 50+ Bosses by Region",
    "description": (
        f"Every Phantom Blade Zero boss by region: {total} named encounters across Weeping Creek Valley, Crimson Forest, "
        "Village of Lu, Pangzhen, Mandate Encampment, Meigu Lake, the Mountain of Imprisonment and Mount Soulrend - "
        "with locations and what each one drops."
    ),
    "keyword": ("phantom blade zero boss list, all bosses phantom blade zero, phantom blade zero boss count, "
                "phantom blade zero boss drops, phantom blade zero optional bosses"),
    "facts": [
        {"label": "Named on this page", "value": f"{total} encounters - {story} story, {optional} optional or recurring"},
        {"label": "Developer figure", "value": "50 or more bosses (director, October 2026)"},
        {"label": "Regions", "value": "8 - Weeping Creek Valley, Crimson Forest, Village of Lu, Pangzhen, "
                                      "Mandate Encampment, Meigu Lake, Mountain of Imprisonment, Mount Soulrend"},
        {"label": "Final boss", "value": "Zuo Shang, The True Long - then The Last Battle on a true-ending run"},
        {"label": "Boss rewards", "value": "Each boss drops its own weapon or Phantom Edge; no shared loot pool"},
        {"label": "Weakness table", "value": "Not published by any outlet - elemental interactions exist but are per-fight"},
        {"label": "True-ending gates", "value": "Gold-Masked One x5, Blizzard Blademaster, four Acolytes, Crimson Manor secret boss"},
        {"label": "Missable bosses", "value": "Yes - several optional fights expire at the Mount Soulrend climb"},
    ],
    "sections": sections,
}

path = os.path.join(PAGES, "boss-list.json")
page["lastUpdated"] = STAMP
with open(path, "w") as f:
    json.dump(page, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"wrote {path}: {total} bosses, {len(sections)} sections")
