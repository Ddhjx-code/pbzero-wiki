import json

TODAY = "2026-10-20"
P = "src/data/pages/"

BWIKI_SRC = (
    '<p class="text-sm text-gray-500">Community terminology and structure on this page comes from the '
    '<a href="https://wiki.biligame.com/yingzhiren/" rel="noopener nofollow" target="_blank">'
    '影之刃 WIKI on BWIKI</a>, a fan wiki maintained by the moderators of the 影之刃 Baidu Tieba, which '
    'states it has no affiliation with S-GAME. It was last edited 2026-10-13 and much of it is still '
    'marked 待补充 (to be filled in). Anything taken from it is labelled as community-sourced rather than '
    'official, and counts will be replaced with measured data after release.</p>'
)


def write(slug, title, desc, kw, facts, sections):
    doc = {
        "slug": slug,
        "title": title,
        "description": desc,
        "keyword": kw,
        "lastUpdated": TODAY,
        "facts": [{"label": k, "value": v} for k, v in facts],
        "sections": [{"id": i, "title": t, "content": c} for i, t, c in sections],
    }
    with open(P + slug + ".json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  wrote /%s" % slug)


# ============ 4. 收集物体系（BWIKI 搬运 + 官方术语）============
write(
    "collectibles",
    "Phantom Blade Zero Collectibles - All Seven Types and What Each Gives",
    "The world hides seven categories of collectibles, including three fragment types that permanently raise Soul's Sha-chi bar, attack and health. Bells double as fast travel and resource restock points. Bilingual names included.",
    "phantom blade zero collectibles, phantom blade zero memory flower, sha-chi amber, black stone fragment, bells fast travel",
    [
        ("Collectible categories", "7 documented, plus story notes and letters"),
        ("Completion tracking", "The game shows a total and a percentage per map"),
        ("Bells (铃铛 / ベル)", "Fog reveal, resource restock, and fast travel between discovered bells"),
        ("Sha-chi Amber shards (杀气琥珀碎片)", "Community-documented: +10% to the Sha-chi bar cap each"),
        ("Black Stone shards (黑石碎片)", "Community-documented: +10% attack and guard-breaking"),
        ("Memory Flowers (记忆之花 / 記憶の花)", "Community-documented: +10% maximum health"),
        ("Gate-locked pickups", "Some weapons and Phantom Edges need a specific Phantom Edge to reach"),
        ("Exact counts per map", "Not published before release"),
    ],
    [
        (
            "overview",
            "The seven categories",
            "<p>The world is built to be walked back through, and the collectibles are what mark whether you have actually explored it. Community documentation lists seven categories, and the game tracks a total and a completion percentage per map, so you can see what you skipped.</p>"
            "<ol>"
            "<li><strong>Bells (铃铛)</strong> - the backbone of the map system, described in its own section below.</li>"
            "<li><strong>Weapons and Phantom Edges (武器与影之武装)</strong> - pickups scattered through the world, some of which need a specific Phantom Edge to reach at all.</li>"
            "<li><strong>Accessories and flasks (饰品与药瓶)</strong> - the gear and healing items that round out a build.</li>"
            "<li><strong>Challenge locations (挑战地点)</strong> - optional fight areas with rewards on completion.</li>"
            "<li><strong>Sha-chi Amber shards (杀气琥珀碎片)</strong> - community-documented as raising the Sha-chi bar cap by 10%.</li>"
            "<li><strong>Black Stone shards (黑石碎片)</strong> - community-documented as raising attack and guard-breaking by 10%.</li>"
            "<li><strong>Memory Flowers (记忆之花)</strong> - community-documented as raising maximum health by 10%.</li>"
            "</ol>"
            "<p>Separate from those are <strong>story collectibles</strong> - notes and letters (纸条、信件) that sit in the world and can be re-read from the inventory. They carry lore rather than power, which makes them the category completionists are most likely to miss on a first pass.</p>",
        ),
        (
            "bells",
            "Bells do three jobs",
            "<p>The official State of Play described bells as the fast-travel mechanism. Community documentation adds two things that matter more in practice:</p>"
            "<ul>"
            "<li><strong>Touching a bell for the first time clears the fog on the minimap around it</strong>, so a bell is a map-reveal as well as a waypoint.</li>"
            "<li><strong>Bells restore combat resources</strong>, which makes them the rest point in a game where, by the same accounts, defeated enemies do not simply repopulate when you rest.</li>"
            "<li>Travel runs between discovered bells, and a consumable teleport item (穿行符) lets you jump from anywhere back to one.</li>"
            "</ul>"
            "<p>The practical consequence: bells are not just convenience, they are the economy of the map. If you are stuck on a boss, the answer is more often a bell you have not reached than a level you have not earned.</p>",
        ),
        (
            "fragments",
            "The three permanent upgrades",
            "<p>Three of the seven categories are progression rather than loot, each reported by the community wiki as a flat 10% per pickup: Sha-chi Amber to the resource bar cap, Black Stone to attack and guard-breaking, Memory Flower to health. That is the closest thing this game has to a stat system, and it is exploration-driven rather than combat-driven - which is the design statement.</p>"
            "<p><strong>Marked as community-sourced.</strong> The exact percentage, whether it compounds linearly, and how many of each exist have not been published by S-GAME. Verify against the retail game before planning a route around them.</p>",
        ),
        (
            "gating",
            "Why you will come back",
            "<p>The October 2026 studio previews described Phantom Edges being used outside combat: an axe that smashes environmental barriers, a chain sickle that works as a grappling hook. That means some pickups in the seven categories are physically unreachable until you have the right secondary weapon, which is also why the per-map completion percentage exists at all.</p>"
            "<p>Treat any 80%-complete map as a promise rather than a mistake - the missing 20% is probably gated, and the game tells you how much you have left.</p>"
            + BWIKI_SRC,
        ),
    ],
)

# ============ 5. 不可逆内容 ============
write(
    "missable",
    "Phantom Blade Zero Missable Content - What You Can Permanently Skip",
    "Community documentation states plainly that some side quests cannot be recovered once missed. This page separates what is actually known from what is guess, and gives a route that keeps the recoverable stuff safe.",
    "phantom blade zero missable, phantom blade zero miss side quests, phantom blade zero points of no return, phantom blade zero completionist",
    [
        ("Missable side quests", "Reported by the community wiki: some cannot be recovered"),
        ("Which ones", "Not published before release - no list exists yet"),
        ("Points of no return", "Not documented before release"),
        ("New Game Plus", "Confirmed; carries weapons, upgrades and progression"),
        ("66 Days mode unlock", "Requires finishing on Pathbreaker or Hellwalker"),
        ("Late-game weapons", "Drop from late and hidden bosses, effectively collectibles on a first run"),
        ("Completion tracking", "Per-map totals and percentage, which is your missable detector"),
    ],
    [
        (
            "what-is-known",
            "What is actually known, and what is not",
            "<p>One line in the community wiki is worth more than any other pre-release sentence: <strong>部分支线任务错过后无法挽回</strong> - some side quests cannot be recovered once missed. That is a real warning, and it is the reason this page exists.</p>"
            "<p>What nobody has, before launch, is the list. No outlet or wiki has published which quests are missable, where the points of no return are, or which quests lock behind a chapter. Anyone publishing a specific missable list before reviewers have the retail build is guessing, and this page will not pretend otherwise.</p>",
        ),
        (
            "why-it-matters",
            "Why this game makes it sharper than usual",
            "<p>Three confirmed design choices stack the risk:</p>"
            "<ul>"
            "<li><strong>Side quests can open new story paths.</strong> S-GAME's own State of Play post says interacting with people and completing some side quests may open paths through the story. So a missed quest is potentially a missed branch, not just missed loot.</li>"
            "<li><strong>There are reportedly eight endings.</strong> If endings are driven by side content and collection, a missable quest is an ending you may not see on this run.</li>"
            "<li><strong>Exploration is gated by weapons.</strong> Some areas need a specific Phantom Edge to reach, so an area you skip is a set of quests you never saw the existence of.</li>"
            "</ul>",
        ),
        (
            "safe-route",
            "The route that keeps you safe",
            "<p>Until a real list exists, the only defensible approach is procedural:</p>"
            "<ol>"
            "<li><strong>Watch the map percentage, not the quest markers.</strong> The game tracks totals per area, so a map that stops climbing is telling you something.</li>"
            "<li><strong>Clear 庞镇 / Pang Town before advancing a chapter.</strong> The hub is where the NPC-linked quests live, and the community notes say some side quests are tied to Pang Town NPCs. Hub state is usually the first thing a chapter transition invalidates.</li>"
            "<li><strong>Take every Phantom Edge you find,</strong> even if you do not use it - it may be the key to a region rather than a weapon.</li>"
            "<li><strong>Pick a difficulty you can actually finish with.</strong> The director's stated reason for moving the death limit into <a href=\"/difficulty-modes\">66 Days</a> was that a countdown on the first run was too harsh. That is an explicit invitation to play the story first and the challenge second.</li>"
            "<li><strong>Plan on a second run.</strong> New Game Plus carries weapons and upgrades, and the late-game arsenal is designed to be used there.</li>"
            "</ol>",
        ),
        (
            "ng-plus",
            "New Game Plus is part of the plan, not a consolation prize",
            "<p>The director has been direct about why NG+ exists: weapons that drop from late, final and hidden bosses arrive with so little of the campaign left that on a first run they are collectibles. They were built out in full anyway, with more motion capture and more involved mechanics than the early weapons.</p>"
            "<p>So a first run that misses content is not a failure state - it is the intended shape. Clearing the game on Pathbreaker or Hellwalker also unlocks 66 Days, which means finishing the story is a prerequisite for the hardest mode rather than a warm-up for it.</p>"
            + BWIKI_SRC,
        ),
    ],
)

# ============ 6. 地区（修掉之前 /locations 的缺失引用）============
write(
    "locations",
    "Phantom Blade Zero Locations - Every Region Named So Far",
    "Six regions have been named across official material and community documentation, from the valley where Soul wakes to a mountain prison. The world is a wide-linear structure of handcrafted areas, not an open world.",
    "phantom blade zero locations, phantom blade zero map, phantom blade zero regions, Pang Town, phantom blade world map",
    [
        ("World structure", "Wide-linear: handcrafted regions joined seamlessly, not an open world"),
        ("Hand-painted maps", "Eight, in Chinese ink-wash style, deliberately imprecise"),
        ("Fast travel", "Bells between discovered locations"),
        ("Named regions", "6 so far, from official and community material"),
        ("Setting names", "The Wulin 武林, also called the Phantom World in official English copy"),
        ("Full map", "To be completed after release"),
    ],
    [
        (
            "structure",
            "Not an open world, not a corridor either",
            "<p>This is one of the most-asked questions about the game, and the answer is settled. S-GAME's own wording: Phantom Blade Zero is <em>not</em> an open-world game, nor a linear adventure from beginning to end - every corner is handcrafted. Community documentation describes it as a wide-linear flow built from large maps with light Metroidvania-style exploration and side content filling them.</p>"
            "<p>Navigation runs through <strong>eight hand-painted Chinese ink-wash maps</strong>. In complex regions they deliberately give only a rough sense of direction, which is where the hidden enemies, side quests, rare treasures and story clues sit. Previewers reported genuinely struggling to orient early on, so that friction is designed, not a shortcoming.</p>",
        ),
        (
            "regions",
            "The named regions",
            "<ul>"
            "<li><strong>溪谷 / the Valley</strong> - the first map, where Soul wakes.</li>"
            "<li><strong>血色森林 / Blood-Coloured Forest</strong> - a forest under red blood-mist.</li>"
            "<li><strong>庞镇 / Pang Town</strong> - the central hub, where martial artists from across the Wulin have gathered; described in the deep dive as a trap of rival factions and hidden malice, and scored with an unusual seven-beat piece.</li>"
            "<li><strong>梅谷湖 / Plum Valley Lake</strong> - a lake area crossed by water travel on a fast vessel.</li>"
            "<li><strong>狱山 / Prison Mountain</strong> - a mountain prison region.</li>"
            "<li><strong>正道大营 / Camp of the Righteous Path</strong> - the encampment of a righteous sect.</li>"
            "</ul>"
            "<p>Also named in official material: an abandoned warehouse hung with puppets where a ritual is underway, and a steam-powered iron tower built for some kind of dark experiment.</p>",
        ),
        (
            "naming",
            "Two official names for the same world",
            "<p>Expect to see both. The August State of Play post on PlayStation Blog, written by S-GAME's founder, calls the setting <strong>the Wulin (武林)</strong>. The English store copy and the Japanese product page call it <strong>the Phantom World</strong> - and the Chinese site uses 影境. None of these is a translation error; they are the marketing, the in-fiction and the localised names for one place.</p>"
            "<p>Japanese material uses 武林 alongside Phantom World, and the Chinese official site's own tagline pairs 影境江湖 with 功夫朋克 (kungfupunk).</p>",
        ),
        (
            "travel",
            "Getting around",
            "<p>Bells handle fast travel between discovered locations, and each bell also clears nearby minimap fog and restocks combat resources. Water travel exists in at least one region. Some areas are only reachable once you hold the right <a href=\"/phantom-edges\">Phantom Edge</a>, which is why <a href=\"/collectibles\">per-map completion percentages</a> matter more here than in a typical action game.</p>"
            "<p>Region design is said to draw on real terrain from Guangdong, Fujian, Zhejiang and Hebei, with Ming-era architecture sitting alongside industrial machinery - the visual argument for the kungfupunk label.</p>"
            + BWIKI_SRC,
        ),
    ],
)
