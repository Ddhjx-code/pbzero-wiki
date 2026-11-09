#!/usr/bin/env python3
"""Add the two guide pages the site never had: /trophy-guide and /walkthrough.

Both were listed as Phase 4 "after release" items in plan.md and never built.
"""
import json
import os

PAGES = "src/data/pages"
STAMP = "2026-11-09"
LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'


def write(slug, data):
    path = os.path.join(PAGES, f"{slug}.json")
    data["lastUpdated"] = STAMP
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {path}")


# ------------------------------------------------------------ trophy guide
trophy = {
    "title": "Phantom Blade Zero Trophy Guide - All 36 Trophies, Platinum Roadmap",
    "description": "Phantom Blade Zero's full trophy list and a platinum roadmap: 36 trophies on PS5, 66 achievements on Steam, everything earnable in one run, and the six Tale trophies that expire silently.",
    "keyword": ("phantom blade zero trophies, phantom blade zero trophy guide, phantom blade zero platinum, "
                "phantom blade zero achievements, phantom blade zero missable trophies"),
    "facts": [
        {"label": "PS5 trophies", "value": "36 - 1 Platinum, 3 Gold, 14 Silver, 18 Bronze"},
        {"label": "Steam achievements", "value": "66 - the PC list adds chapter and combat-move entries"},
        {"label": "Runs needed", "value": "One. All 36 PS5 trophies are earnable in a single playthrough"},
        {"label": "Difficulty trophies", "value": "None - any difficulty, and you can change it freely"},
        {"label": "Missable trophies", "value": "Yes - six Tale trophies plus four boss trophies expire at the Mount Soulrend climb"},
        {"label": "Platinum length", "value": "50 to 70 hours, per Game8's estimate"},
        {"label": "Platinum difficulty", "value": "7/10, per Game8"},
        {"label": "Hidden trophies", "value": "13, including all three Gold trophies"},
    ],
    "sections": [
        {
            "id": "overview",
            "title": "How the List Is Shaped",
            "content": (
                "<p>The platinum is <strong>Defy Destiny</strong>, awarded for the other 35. Game8's assessment is that the whole "
                "set fits in one run at roughly 7/10 difficulty over 50 to 70 hours, with no difficulty-gated trophies and no "
                "bugged ones - the difficulty is entirely in not missing content, not in beating anything on a hard setting.</p>"
                "<p>The category split matters more than the individual entries, because it tells you where the risk is:</p>"
                "<table><thead><tr><th>Category</th><th>Trophies</th><th>Risk</th></tr></thead><tbody>"
                "<tr><td>Story chapters</td><td>Automatic on the main path</td><td>None</td></tr>"
                "<tr><td>Boss kills</td><td>One per named boss, including grouped fights</td><td>Low - most are story bosses</td></tr>"
                "<tr><td>Tales</td><td>Six Tale-completion trophies</td><td><strong>High</strong> - several expire</td></tr>"
                "<tr><td>Grind</td><td>Tempering, upgrades, collectibles, enemy journal</td><td>None, just time</td></tr>"
                "</tbody></table>"
                "<p>PS5 and Steam are not the same list. The Chinese guide 177xz puts PS5 at 36 and Steam at 66 and warns that a "
                "PC player who works from the PS5 list will still have gaps, because Steam adds chapter and weapon-move entries. "
                "PlayStation players can ignore that entirely.</p>"
            ),
        },
        {
            "id": "missable",
            "title": "The Missable Trophies",
            "content": (
                "<p>Six Tale trophies can become unobtainable, and the game does not warn you when a Tale expires. All of them "
                "must be finished before the climb to Mount Soulrend.</p>"
                "<table><thead><tr><th>Trophy</th><th>Tale</th><th>What catches people</th></tr></thead><tbody>"
                "<tr><td>The Healer's Legacy</td><td>Flesh Lily + Apprentice Healer + A Healer's Mercy</td>"
                "<td>Three Tales, not one. Delivering a single flower is not enough.</td></tr>"
                "<tr><td>The Last of Baishan</td><td>Secrets of the Baishan Sect</td>"
                "<td>Must be accepted before the Bai Chilian fight, not after.</td></tr>"
                "<tr><td>Together Till The End</td><td>The Journey Home</td>"
                "<td>Old Man Gen's request - accept it before entering Pangzhen.</td></tr>"
                "<tr><td>A Wanderer's Honor</td><td>Young Master Lan</td>"
                "<td>Same window as The Journey Home; both start in the Village of Lu.</td></tr>"
                "<tr><td>Spectral Blade</td><td>Severing the Mindseal</td>"
                "<td>Easy to walk past; not on the critical path.</td></tr>"
                "<tr><td>Lost and Found</td><td>All of Quick Hand Zhang's Requests</td>"
                "<td>Five separate encounters. Miss one and the chain is dead.</td></tr>"
                "</tbody></table>"
                "<p>The 177xz route note is worth following literally: chase 玉儿's Tales early, because The Healer's Legacy needs "
                "<em>Apprentice Healer</em> delivered before the Bai Chilian fight and <em>Secrets of the Baishan Sect</em> "
                "accepted before it as well. Both are in the Village of Lu / Crimson Forest window, well before the point of no return.</p>"
            ),
        },
        {
            "id": "boss-trophies",
            "title": "Boss Trophies, Including the Grouped Ones",
            "content": (
                "<p>Most boss trophies are a single kill. Four are grouped, which means one trophy can hide three fights:</p>"
                "<table><thead><tr><th>Trophy</th><th>Requires</th></tr></thead><tbody>"
                "<tr><td>Master of the Misty Waters</td><td>You Loong, Yan Qiansui and the One-Eyed Archer</td></tr>"
                "<tr><td>The Four Freed</td><td>Yuzan, Yubi, Yuding and Yucong - the four great puppets</td></tr>"
                "<tr><td>Three Wardens Fall</td><td>Cavalrybane, Soulclaimer and Heartpiercer</td></tr>"
                "<tr><td>The Two Blade Masters</td><td>Zhu Yuan and Commander Bi Feng</td></tr>"
                "</tbody></table>"
                "<p>The golds are <strong>With Heart and Blood</strong> (true ending), <strong>All Dreams Must End</strong> "
                "(Meng Hua) and <strong>The Four Freed</strong>. That makes the true ending unavoidable for the platinum - "
                f"there is no version of this list you can finish on the ordinary ending. The checklist is on "
                f"<a href=\"/true-ending\" {LINK}>the true ending page</a>, and the roster with locations is on "
                f"<a href=\"/boss-list\" {LINK}>the boss list</a>.</p>"
            ),
        },
        {
            "id": "grind",
            "title": "The Six Grind Trophies",
            "content": (
                "<p>None of these are hard, all of them are counting, and all of them are cheap to set up if you know the targets:</p>"
                "<table><thead><tr><th>Trophy</th><th>Requirement</th><th>Fastest route</th></tr></thead><tbody>"
                "<tr><td>A Tempered Ten</td><td>Temper 10 weapons</td><td>Temper the cheap Sanguine family first - the "
                "transformations count</td></tr>"
                "<tr><td>Overwhelming Force</td><td>Upgrade one weapon to level 30</td><td>One weapon only; the cap is 30 for all</td></tr>"
                "<tr><td>Phantom Arsenal</td><td>Temper 10 Phantom Edges</td><td>Tempering is refundable, so materials are not lost</td></tr>"
                "<tr><td>Skill Over Strength</td><td>Upgrade one Phantom Edge to level 30</td><td>Same as Overwhelming Force, other slot</td></tr>"
                "<tr><td>Listen to Every Flower</td><td>Collect 10 Memory Flowers</td><td>Memory Flowers also gate the Dusk encounter, "
                "so this doubles as progress</td></tr>"
                "<tr><td>Collector's Note</td><td>Collect 30 Accessories</td><td>The longest of the six - accessories are scattered "
                "rather than dropped</td></tr>"
                "</tbody></table>"
                "<p><strong>Unsung Legend</strong> is not in that table but belongs with it: it needs the enemy journal completed, "
                "which means killing everything at least once rather than only the bosses you have to.</p>"
            ),
        },
        {
            "id": "roadmap",
            "title": "Platinum Roadmap",
            "content": (
                "<ol>"
                "<li><strong>Prologue and Weeping Creek Valley</strong> - play normally. The Heart's Journey and the first boss "
                "trophies come free. Kill Hua, Deadly Betrothed before leaving the region; she is optional and missable.</li>"
                "<li><strong>Village of Lu</strong> - start 玉儿's Tale chain and Quick Hand Zhang's first request here. "
                "Do An Unwavering Heart / chapter content as it comes.</li>"
                "<li><strong>Before entering Pangzhen</strong> - accept The Journey Home and Young Master Lan, then finish both. "
                "This is the window 177xz warns about.</li>"
                "<li><strong>Crimson Forest and Crimson Manor</strong> - all four Acolyte scarecrows except Hansui, Hansui last. "
                "Deliver Apprentice Healer and pick up Secrets of the Baishan Sect before Bai Chilian.</li>"
                "<li><strong>Pangzhen</strong> - the widest optional window in the game. Clean the Tales here, not later.</li>"
                "<li><strong>Meigu Lake</strong> - mirror realm, the Lóng Pillar inside it, Blizzard Blademaster and Whiteshadow.</li>"
                "<li><strong>Mountain of Imprisonment</strong> - the Yin eye, plus Bi Feng and Jade-Face.</li>"
                "<li><strong>Manual save before the Mirage Estate.</strong></li>"
                "<li><strong>Mirage Estate</strong> - the last Lóng Pillar, then commit to Mount Soulrend.</li>"
                "<li><strong>Endgame</strong> - Meng Hua, Zuo Shang, then The Last Battle for With Heart and Blood.</li>"
                "<li><strong>Cleanup</strong> - free roam after the credits covers accessories, Tempering and the journal. "
                "New Game Plus is there if something expired anyway.</li>"
                "</ol>"
            ),
        },
        {
            "id": "sources",
            "title": "Sources and the Count Disagreement",
            "content": (
                "<p>Tier counts and the PS5-versus-Steam split: Game8's platinum guide, Gfinity's full list and 177xz's "
                "platform comparison all give 36 for PS5 with the same 1/3/14/18 split. Fextralife lists 66 for the combined "
                "PS5-and-PC set with a different split (1/3/22/40), which is the Steam-style count.</p>"
                "<p>Not resolved: exactly which tier each grouped boss trophy occupies. Sources agree on the three golds - "
                "With Heart and Blood, All Dreams Must End, The Four Freed - and disagree on several silvers. The category "
                "tables above avoid asserting tiers for the disputed entries.</p>"
                "<p>IGN's page gives 36 in one table and '50 trophies' in a summary line; 50 appears to be a typo carried from an "
                "early build, since 1+3+14+18 is 36 and every other outlet agrees.</p>"
            ),
        },
    ],
}
write("trophy-guide", trophy)

# ------------------------------------------------------------- walkthrough
walkthrough = {
    "title": "Phantom Blade Zero Walkthrough - Chapter Order and What Locks When",
    "description": "Phantom Blade Zero's main story in order: 8 regions, 22 missions, the point of no return at the Mount Soulrend climb, and which optional Tales expire before you get there.",
    "keyword": ("phantom blade zero walkthrough, phantom blade zero chapters, phantom blade zero mission list, "
                "phantom blade zero story order, phantom blade zero point of no return"),
    "facts": [
        {"label": "Regions", "value": "8 main regions plus realms and secret areas"},
        {"label": "Main missions", "value": "22 named missions, including two prologue missions"},
        {"label": "Main story length", "value": "20 to 25 hours"},
        {"label": "With side content", "value": "30 to 40 hours depending on how much you chase"},
        {"label": "Point of no return", "value": "The climb to Mount Soulrend after the Mirage Estate"},
        {"label": "Structure", "value": "Semi-open regions, not open world - you clear an area then move on"},
        {"label": "Backtracking", "value": "Free after the credits; bells allow fast travel within unlocked regions"},
        {"label": "Missable window", "value": "Everything before Mirage Estate - Tales expire silently"},
    ],
    "sections": [
        {
            "id": "how-it-is-structured",
            "title": "How the Campaign Is Structured",
            "content": (
                "<p>Eight semi-open regions in a fixed order, each with a story thread and a pile of optional content. "
                "The game calls its side content <em>Tales</em>; purple Tales are the ones tied to the true ending.</p>"
                "<p>This is not an open world. You cannot wander into Pangzhen from the prologue, and the regions unlock in "
                "sequence. What you <em>can</em> do is leave a region early - and that is where runs go wrong, because several "
                "Tales stop being completable once the story moves past them.</p>"
                "<p>Fast travel is by bells, one or more per region. Bells do not work inside the Phantom Illusionist Ruins, "
                "which is why the Four Guardians' Mirror realm is a one-way trip until you clear it.</p>"
            ),
        },
        {
            "id": "mission-order",
            "title": "The 22 Missions in Order",
            "content": (
                "<table><thead><tr><th>#</th><th>Region</th><th>Mission</th></tr></thead><tbody>"
                "<tr><td>P</td><td>Prologue</td><td>Diverging Paths &middot; Reckless Pursuit</td></tr>"
                "<tr><td>1</td><td>Weeping Creek Valley</td><td>Against the Flow &middot; Steel and Steam &middot; Crimson Manor</td></tr>"
                "<tr><td>2</td><td>Crimson Forest</td><td>Illusion of Inanis &middot; Snake's Reflection</td></tr>"
                "<tr><td>3</td><td>Crimson Forest / Village of Lu</td><td>Heartless Remnants</td></tr>"
                "<tr><td>4</td><td>Pangzhen</td><td>Town of Death &middot; The Heart's Trail &middot; "
                "The Four Serpent Houses &middot; The Way Forward</td></tr>"
                "<tr><td>5</td><td>Mandate Encampment</td><td>Pillars of Kunlun</td></tr>"
                "<tr><td>6</td><td>Meigu Lake</td><td>Sha-Chi Powered Boat &middot; Secrets at the Heart of the Lake &middot; "
                "Allure of Vanity &middot; Illusory Pipa</td></tr>"
                "<tr><td>7</td><td>Mountain of Imprisonment</td><td>Whence the Weeping</td></tr>"
                "<tr><td>8</td><td>Mount Soulrend</td><td>The Herald's Illusion &middot; Bloodline Awakening &middot; "
                "A Soul's Worth</td></tr>"
                "</tbody></table>"
                "<p>Two caveats. Mission-to-region assignment varies between outlets - <em>Heartless Remnants</em> is put in "
                "Village of Lu by one list and in Crimson Forest by another, and <em>Pillars of Kunlun</em> moves between "
                "Mandate Encampment and Mount Soulrend depending on who is writing. The order of the missions is consistent "
                "across sources; the region labels are not. Treat the sequence as reliable and the borders as approximate.</p>"
            ),
        },
        {
            "id": "region-notes",
            "title": "Region Notes, In the Order You Hit Them",
            "content": (
                "<p><strong>Weeping Creek Valley.</strong> Tutorial-by-stealth: the region exists to teach Sha-Chi. Peng Meng is "
                "the first real boss and drops the Dread Axe, your first Phantom Edge. Hua, Deadly Betrothed is optional and "
                "sits in the Flesh Lily Fields - fight her here, not later, because her drop (Scarlet Wraithblade) is one of the "
                "best early weapons and the fight is scaled for this point.</p>"
                "<p><strong>Crimson Forest.</strong> Two story bosses that teach the elemental vocabulary: Hua Qianxiao's "
                "drinking shield, Jing Ye's horse and blood-draining sword. Bai Chilian closes the region. "
                "<Here>Everything missable in the Village of Lu window should be resolved before the mirror puzzle.</p>"
                "<p><strong>Village of Lu.</strong> The densest optional region. Mu Xiaokui's encounter hands out more than one "
                "weapon, Yuzan drops the Heartrend Pipa, and four Tales start here. Clear it properly.</p>"
                "<p><strong>Pangzhen.</strong> The largest region and the widest missable window. Flame, the Lion Dance "
                "Grandmaster closes it and drops the Flaming Mane, which you need later to open the way into Pangzhen Slums for "
                "Acolyte Lei Ting. Do not leave before the Tales are done.</p>"
                "<p><strong>Mandate Encampment.</strong> Short. The Seven-Stars Formation is the fight that matters; clear the "
                "disciples before the leader or the leader has support.</p>"
                "<p><strong>Meigu Lake.</strong> Three separate systems converge here - the boat, the mirror realm, and the "
                "Blizzard Blademaster. This is where the true-ending checklist either comes together or falls apart.</p>"
                "<p><strong>Mountain of Imprisonment.</strong> Optional for the story, required for the true ending. The Yin "
                "Crystal Puppet Eye is here, and so are Bi Feng and Jade-Face.</p>"
                "<p><strong>Mount Soulrend.</strong> The endgame. Herald of the Veil, Bloodline Awakening's fifth pillar, "
                "Meng Hua, Zuo Shang, and then the hidden fight.</p>"
            ).replace("<Here>", ""),
        },
        {
            "id": "point-of-no-return",
            "title": "The Point of No Return",
            "content": (
                "<p>The climb from the Mirage Estate to the peak of Mount Soulrend is the cutoff. The game warns you; the warning "
                "is not specific about what you are about to lose. Per 177xz, the warning appears even when every prerequisite "
                "is already met, so it is not a diagnostic - do not read it as one.</p>"
                "<p>What expires: any purple Tale still open, the Acolyte scarecrow fights you have not triggered, "
                "the Crimson Manor secret boss, and the optional bosses in regions you have already passed.</p>"
                "<p>What survives: free roam after the credits, bells, accessories and collectible cleanup, Tempering, and "
                "New Game Plus. So a missed item is recoverable; a missed <em>Tale</em> usually is not, because the trigger "
                "depends on a story state you cannot go back to.</p>"
            ),
        },
        {
            "id": "before-you-commit",
            "title": "Before You Commit",
            "content": (
                "<ul>"
                "<li>Manual save, separate slot, at the Mirage Estate.</li>"
                "<li>Purple Tales: all done, none open.</li>"
                "<li>Acolytes: four masks in hand.</li>"
                "<li>Pillars: four destroyed plus the one in the mirror realm.</li>"
                "<li>Crystal Puppet Eyes: two, from the Mountain of Imprisonment and the Crimson Manor.</li>"
                "<li>Illusory Pipa: restored. Puppet's Tongue: used.</li>"
                "<li>Quick Hand Zhang: all five relics delivered.</li>"
                "</ul>"
                f"<p>Anything not ticked, tick it now - the <a href=\"/true-ending\" {LINK}>true ending checklist</a> has the "
                f"long version. For how much time the run should take, see <a href=\"/how-long-to-beat\" {LINK}>how long to beat</a>.</p>"
            ),
        },
        {
            "id": "sources",
            "title": "Sources",
            "content": (
                "<p>Mission names and order: Gamer.org's chapter-and-mission list and TigerJek's chapter list, which agree on the "
                "sequence and differ on two region labels. Region structure and the semi-open framing: both, plus 18183's "
                "Chinese version. Point-of-no-return behaviour and the warning prompt: 177xz and VGTimes.</p>"
                "<p>Not asserted here: an exact per-mission hour count. No source breaks the campaign down that finely, and the "
                "20-25 hour figure is for the story as a whole.</p>"
            ),
        },
    ],
}
write("walkthrough", walkthrough)
