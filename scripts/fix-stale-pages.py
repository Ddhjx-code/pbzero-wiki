#!/usr/bin/env python3
"""Fix the two pages whose data went stale on release.

how-long-to-beat was written as "nobody knows yet" and needs replacing outright.
weapons keeps its good systems material but gains the real acquisition tables,
because the pre-launch page could only list names, not locations.
"""
import json
import os

PAGES = "src/data/pages"
STAMP = "2026-11-09"
LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'


def save(slug, data):
    path = os.path.join(PAGES, f"{slug}.json")
    data["lastUpdated"] = STAMP
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {path}")


# ------------------------------------------------------ how-long-to-beat
hltb = {
    "title": "How Long Is Phantom Blade Zero? 20-25 Hours Main, 50-70 to Platinum",
    "description": "Phantom Blade Zero playtime, measured: 20-25 hours for the main story, 30-40 with side content, 40-45 for a full clear, 50-70 for the platinum - and why reviewers reported 50 hours when the director said 20 to 30.",
    "keyword": ("how long is phantom blade zero, phantom blade zero length, phantom blade zero how long to beat, "
                "phantom blade zero playtime, phantom blade zero hours"),
    "facts": [
        {"label": "Main story", "value": "20-25 hours"},
        {"label": "Main + side content", "value": "30-40 hours (guides split between 30-35 and 35-40)"},
        {"label": "Full completion", "value": "40-45 hours; 50-55 for a thorough 100% run"},
        {"label": "Platinum", "value": "50-70 hours, per Game8"},
        {"label": "Director's estimate", "value": "20-30 hours for the story"},
        {"label": "Reviewer runs", "value": "50 hours (IGN) and 55 hours (Combo Infinito) at review"},
        {"label": "Regions", "value": "8, plus realms and secret areas"},
        {"label": "Missions", "value": "22 main story missions"},
        {"label": "Replay", "value": "66 Days mode unlocks after any completion; New Game Plus carries gear over"},
    ],
    "sections": [
        {
            "id": "answer",
            "title": "The Answer",
            "content": (
                "<p><strong>20 to 25 hours</strong> if you chase the story and nothing else. <strong>30 to 40 hours</strong> if "
                "you take the side content, which is the way the game is meant to be played and the range the guides themselves "
                "cannot agree on. <strong>40 to 45 hours</strong> to clear everything, stretching to 50-55 if you are thorough, "
                "and <strong>50 to 70</strong> if you are going for the platinum.</p>"
                "<p>This page used to say the figure was unconfirmed. It was, in September. It is not now, and the pre-release "
                "framing has been replaced rather than annotated.</p>"
            ),
        },
        {
            "id": "table",
            "title": "By Playstyle",
            "content": (
                "<table><thead><tr><th>Playstyle</th><th>Time</th><th>Source</th></tr></thead><tbody>"
                "<tr><td>Main story only</td><td><strong>20-25 hours</strong></td><td>18183, Gamer.org, TigerJek</td></tr>"
                "<tr><td>Main + side content</td><td>30-35 hours</td><td>18183, TigerJek</td></tr>"
                "<tr><td>Main + side content</td><td>35-40 hours</td><td>Gamer.org</td></tr>"
                "<tr><td>100% completion</td><td>40-45 hours</td><td>18183, TigerJek</td></tr>"
                "<tr><td>100% completion</td><td>50-55 hours</td><td>Gamer.org</td></tr>"
                "<tr><td>Platinum trophy</td><td>50-70 hours</td><td>Game8</td></tr>"
                "<tr><td>Director's own estimate</td><td>20-30 hours (story)</td><td>Gamer.org, citing the creative director</td></tr>"
                "<tr><td>Reviewer first runs</td><td>50 hours / 55 hours</td><td>IGN, Combo Infinito (26 October 2026)</td></tr>"
                "</tbody></table>"
                "<p>The spread is not noise. Two different things are being measured: the guides' 20-25 hours is a main-path run "
                "that skips optional bosses and Tales, while the reviewers' 50 hours is a first playthrough that engaged with the "
                "side content because the game pushes you toward it.</p>"
            ),
        },
        {
            "id": "why-50",
            "title": "Why Reviewers Said 50 Hours and the Director Said 20 to 30",
            "content": (
                "<p>The director's 20-30 hour figure is a story estimate, and 20-25 is what it turns into once you actually "
                "route it. The review runs are longer for three compounding reasons:</p>"
                "<ul>"
                "<li><strong>Boss gates.</strong> The combat is deflect-and-punish, so a fight that costs one player fifteen "
                "minutes costs another an hour. Several bosses in the roster are hard walls on a first attempt.</li>"
                "<li><strong>Optional content is not optional in practice.</strong> Weapons, accessories and Sha-Chi Amber "
                "Shards come from side areas. Skip them and the back half gets harder, which lengthens the back half.</li>"
                "<li><strong>The Tales are story.</strong> Purple Tales feed the endings, so anyone reviewing the narrative "
                "had to do them.</li>"
                "</ul>"
                "<p>IGN's reviewer wrote that combat 'never came even close to feeling old across 50 hours', which is the useful "
                "data point: the extra 25 hours were not padding being endured.</p>"
            ),
        },
        {
            "id": "what-drives-it",
            "title": "What Actually Drives Your Number",
            "content": (
                "<p>Four levers, in order of impact:</p>"
                "<p><strong>Difficulty.</strong> Four modes - Wayfarer, Pathbreaker, Hellwalker and 66 Days. Wayfarer exists "
                "specifically for players who want the story and the combat without the wall; Hellwalker makes enemies adaptive. "
                "There is no difficulty trophy, so Wayfarer costs you nothing but pride.</p>"
                "<p><strong>Whether you do the Acolytes and Lóng Pillars.</strong> That is four boss fights and five duels "
                "against the Gold-Masked One, and the later pillars are fought at your current power level, so leaving them late "
                "makes them expensive.</p>"
                "<p><strong>Collectibles.</strong> Seven tracked categories: bells, challenge locations, weapons and Phantom "
                "Edges, accessories and medicines, Sha-Chi Amber Shards, Blackstone Shards, and Memory Flowers. Accessories alone "
                "are 30 for the Collector's Note trophy.</p>"
                "<p><strong>Tempering.</strong> Upgrade and Temper trophies want one weapon at level 30 and ten weapons plus ten "
                "Phantom Edges Tempered. Tempering is refundable, so this is time rather than resources.</p>"
            ),
        },
        {
            "id": "post-game",
            "title": "Post-Game and Replay",
            "content": (
                "<p>Free roam opens after the credits: bells work, regions stay open, and cleanup is possible. What does not "
                "come back is any Tale that expired at the Mount Soulrend climb.</p>"
                "<p><strong>66 Days</strong> unlocks after any completion - 66 lives for a whole run, save deleted on the 66th "
                "death. Dying out of it is the only way to see the secret ending, so a completionist's hour count includes a "
                "deliberate failure somewhere.</p>"
                "<p><strong>New Game Plus</strong> carries skills, weapons and Phantom Edges over, which is the recovery path if "
                "something missable slipped past you. It is also why the platinum is rated 7/10 rather than higher - nothing is "
                "permanently lost, only delayed.</p>"
                f"<p>Chapter order is on <a href=\"/walkthrough\" {LINK}>the walkthrough</a>; the trophy requirements are on "
                f"<a href=\"/trophy-guide\" {LINK}>the trophy guide</a>.</p>"
            ),
        },
    ],
}
save("how-long-to-beat", hltb)

# ----------------------------------------------------------------- weapons
WEAPONS = [
    # name, type, where
    ("Wooden Sanguine", "One-handed", "Story reward - Soul's childhood blade"),
    ("Sanguine (血刃)", "One-handed", "Story reward - starting blade, Tempers into Infernal Rouge"),
    ("Jagged Steel (残钢)", "One-handed", "Weeping Creek Valley, Rustblade Pavilion bell; slashes cause Bleeding"),
    ("The Fanatic's Broken Blade", "One-handed", "Crimson Forest, Pangzhen Bridge Overlook; drink to make it fly"),
    ("Tianxuan Bronze Sword", "One-handed", "Village of Lu, The Lady Grounds bell; high shield-break"),
    ("Soft Snake Sword (灵蛇软剑)", "One-handed", "Mandate Encampment, Path of the Baishan's Fall; deflects and cuts threads"),
    ("Freezing Chaos", "One-handed", "Crimson Forest, Threadbound Great Tree (one checklist attributes it to Yucong, No. 34)"),
    ("Aureate", "One-handed", "Defeat Zuo Shang at Mount Soulrend; mimics his Golden Sword Energy"),
    ("Wild Oriole Sword", "One-handed", "Village of Lu, Puppet Testing Grounds; Mu Xiaokui's blade"),
    ("Infernal Rouge (炼狱红妆)", "One-handed", "Temper Sanguine at level 5; grants Bloodline Rebirth"),
    ("Sanguine Twin (血刃双刀)", "Dual-wield", "Weeping Creek Valley, First Meeting with Yu'er bell"),
    ("White Serpent & Crimson Viper", "Dual-wield", "Defeat Bai Chilian, Lady of the Twin Serpents"),
    ("Parting Hooks (离别钩)", "Dual-wield", "Pangzhen, Dockside Warehouse; guard stance counters melee"),
    ("Sundering Dual Axes (裂空双斧)", "Dual-wield", "Meigu Lake, White Serpent House; defeat Heartpiercer"),
    ("Baishan Stormswords", "Dual-wield", "Mandate Encampment, Training Grounds; defeat Yubi, No. 21"),
    ("Seamless Death (无间死环)", "Dual-wield", "Mountain of Imprisonment, The Lady's Shrine; hurlable ring blades"),
    ("Fiend Saws", "Dual-wield", "Village of Lu, Puppet Testing Grounds; Jade Dancer's leg-mounted saws"),
    ("The Lady's Fan (仕女扇)", "Dual-wield", "Mount Soulrend, The Fallen Dream; defeat Meng Hua"),
    ("Sanguine Reach", "Two-handed", "Weeping Creek Valley; Tempers into Blazing Edge"),
    ("Armybreaker (破军)", "Two-handed", "Pangzhen, Marketplace; defeat Cavalrybane"),
    ("Crescent Blade", "Two-handed", "Mirage Estate, Training Grounds; defeat Yuding, No. 12"),
    ("Juggernaut (巨神兵)", "Two-handed", "Mountain of Imprisonment, Commander's Platform; defeat Bi Feng"),
    ("Bonesaw", "Two-handed", "Mount Soulrend, Giant's Lair bell"),
    ("Whiteshadow (白影)", "Two-handed", "Meigu Lake, Whiteshadow's Fall; four masks + Blizzard Blademaster"),
    ("Blazing Edge (炽刃)", "Two-handed", "Temper Sanguine Reach with Scorched Flame shards"),
    ("Shadowless Edge (无影风)", "Two-handed", "Temper Sanguine Twin (listed by one checklist; not independently verified)"),
]

EDGES = [
    ("Bashpole", "Mandate Encampment, Main Encampment Gate"),
    ("Bastion", "Village of Lu, Old Man Gen's Hideout"),
    ("Dread Axe", "Weeping Creek Valley, The Axemaster's Fall; defeat Peng Meng"),
    ("Feather Bow", "Weeping Creek Valley, Outpost"),
    ("Fire Meteor (火流星)", "Pangzhen, Jingyang Hall; defeat Blaze, Shadow Warden Captain"),
    ("Flying Dagger", "Crimson Forest, Thieves' Camp"),
    ("Flying Guillotine", "Mountain of Imprisonment, The Lady's Shrine"),
    ("Heartrend Pipa (心弦琵琶)", "Village of Lu, Puppet Testing Grounds; defeat Yuzan"),
    ("Hunter's Chain Sickle", "Weeping Creek Valley, Great Waterfall"),
    ("Iron Gauntlets", "Defeat Stone Hand Iron Fever"),
    ("Loong Trident", "Meigu Lake, Blackwater Crew Dock; defeat You Loong"),
    ("Thunder Spear (雷当)", "Pangzhen, Ancestral Shrine Square; defeat Chang Hong"),
    ("Tiger Cannon", "Defeat Lei Dang at Mirage Estate"),
    ("Wolfjaw", "Defeat Wu Xuan, the Fallen General"),
    ("Flaming Mane", "Repaired through the story; needed to open the way into Pangzhen Slums"),
    ("Goldblaze", "Pangzhen, Zhang's Hideout - reward for Quick Hand's Request"),
]


def weapon_table(rows):
    body = "".join(f"<tr><td><strong>{n}</strong></td><td>{t}</td><td>{w}</td></tr>" for n, t, w in rows)
    return ("<table><thead><tr><th>Weapon</th><th>Type</th><th>Where to get it</th></tr></thead>"
            f"<tbody>{body}</tbody></table>")


def edge_table(rows):
    body = "".join(f"<tr><td><strong>{n}</strong></td><td>{w}</td></tr>" for n, w in rows)
    return ("<table><thead><tr><th>Phantom Edge</th><th>Where to get it</th></tr></thead>"
            f"<tbody>{body}</tbody></table>")


wpath = os.path.join(PAGES, "weapons.json")
w = json.load(open(wpath))

# Replace the pre-launch name list with real acquisition tables.
for i, s in enumerate(w["sections"]):
    if s["id"] == "the-weapon-names-published-so-far-in-chinese" or "Published So Far" in s["title"]:
        w["sections"][i] = {
            "id": "every-weapon-and-where-to-find-it",
            "title": "Every Weapon and Where to Find It",
            "content": (
                "<p>This replaces the pre-release name list. Before 29 October the best available evidence was a Chinese wiki "
                "catalogue of announced names with no locations; now every weapon below has a sourced acquisition point.</p>"
                "<p>Three rules govern the list. First, bosses drop their own weapon - that is the design, not a coincidence. "
                "Second, five blades are world pickups rather than drops and are easy to walk past. Third, the Sanguine family "
                "is the Tempering tree, so the three starting blades are not throwaways.</p>"
                "<h3>One-handed</h3>" + weapon_table([r for r in WEAPONS if r[1] == "One-handed"]) +
                "<h3>Dual-wield</h3>" + weapon_table([r for r in WEAPONS if r[1] == "Dual-wield"]) +
                "<h3>Two-handed</h3>" + weapon_table([r for r in WEAPONS if r[1] == "Two-handed"]) +
                "<h3>Phantom Edges</h3>" + edge_table(EDGES)
            ),
        }

# Append a Tempering section before the closing "what changed" section.
temper = {
    "id": "tempering-tree",
    "title": "The Tempering Tree",
    "content": (
        "<p>Tempering converts one blade into another and keeps the upgrade level, which is why the starter weapons matter. "
        "AxeeTech and Gamer.org agree on the mappings:</p>"
        "<table><thead><tr><th>From</th><th>To</th><th>Notes</th></tr></thead><tbody>"
        "<tr><td>Sanguine</td><td>Infernal Rouge</td><td>Bloodline Rebirth - heals to full and boosts attack on lethal damage</td></tr>"
        "<tr><td>Sanguine Reach</td><td>Blazing Edge</td><td>Needs Scorched Flame shards; one from Zhu Yuan under the Sha-Chi tower, "
        "one from the midlake challenge</td></tr>"
        "<tr><td>Sanguine Twin</td><td>Shadowless Edge</td><td>Pure speed; outclassed late by dual-wield blades with effects</td></tr>"
        "</tbody></table>"
        "<p>Tempering is refundable - the upgrade materials come back - so experimenting costs time, not resources. That is what "
        "makes the two Tempering trophies (ten weapons, ten Phantom Edges) reasonable rather than a grind trap.</p>"
    ),
}
w["sections"].insert(-1, temper)

w["title"] = "Phantom Blade Zero Weapons Guide - All Blades, Phantom Edges & Locations"
w["description"] = (
    "Every Phantom Blade Zero weapon and where to get it: 26 named blades across one-handed, dual-wield and two-handed, "
    "16 Phantom Edges, the Sanguine Tempering tree, and the Sha-Chi swap mechanic that makes a two-weapon loadout stronger "
    "than either blade."
)
w["keyword"] = ("phantom blade zero weapons, phantom blade zero all weapons, phantom blade zero weapon locations, "
                "phantom blade zero phantom edges, phantom blade zero tempering")

facts = {f["label"]: f for f in w.get("facts", [])}
facts["Full roster"] = {"label": "Named here", "value": "26 blades (10 one-handed, 8 dual-wield, 7 two-handed, plus Tempering forms) and 16 Phantom Edges"}
facts["Boss drops"] = {"label": "Boss drops", "value": "Each boss drops its own blade or edge - the roster doubles as a checklist"}
facts["Swap effect"] = facts.get("Swap effect", {"label": "Swap effect"})
facts["Tempering"] = {"label": "Tempering", "value": "Refundable; three Sanguine blades convert into Infernal Rouge, Blazing Edge and Shadowless Edge"}
w["facts"] = list(facts.values())

save("weapons", w)
