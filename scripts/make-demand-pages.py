import json

TODAY = "2026-10-20"
P = "src/data/pages/"


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
    print("  wrote /%s  (%d sections, %d facts)" % (slug, len(sections), len(facts)))


# ============ 1. 实体版：美国侧最大的需求簇 ============
write(
    "physical-edition",
    "Phantom Blade Zero Physical Edition - Is There a Disc?",
    "Short answer: no. Phantom Blade Zero launches October 29, 2026 as a digital-only game on PS5 and PC. No boxed edition, steelbook or retailer disc has been announced, and one retailer already pulled its listing.",
    "phantom blade zero physical, phantom blade zero disc, phantom blade steelbook, phantom blade zero physical copy, phantom blade zero gamestop",
    [
        ("Physical disc at launch", "None announced - digital only"),
        ("PlayStation 5", "Digital download via PS Store"),
        ("PC", "Steam and Epic Games Store, digital"),
        ("Steelbook", "Not announced"),
        ("Retailer listing", "Play-Asia removed its boxed listing after being told none was coming"),
        ("Later physical release", "Unconfirmed - no statement from S-GAME or Kepler"),
        ("Deluxe Edition contents", "Cosmetic and bonus media only: two outfits, artbook, soundtrack"),
        ("Early access", "None in any edition"),
    ],
    [
        (
            "answer",
            "The Short Answer",
            "<p><strong>There is no physical version of Phantom Blade Zero at launch.</strong> The game releases on 29 October 2026 as a digital purchase on PlayStation 5, Steam and the Epic Games Store. No boxed PS5 edition, no steelbook, and no retail disc has been announced by S-GAME or its publisher.</p>"
            "<p>If you were waiting for a disc, the practical consequence is that you need roughly <a href=\"/release-date\">135 GB of free space on the console</a> and a working download on day one, because there is no disc to install from while a patch downloads.</p>",
        ),
        (
            "play-asia",
            "What happened at Play-Asia",
            "<p>Play-Asia, a retailer that commonly stocks Asian imports, had listed a physical edition of Phantom Blade Zero. That listing has since been <strong>removed</strong>, with the situation reported as the retailer being told a physical version would not be available. Until S-GAME says otherwise, treat any store page claiming a boxed copy as stale or a third-party placeholder.</p>"
            "<p>It is worth being precise about what this does and does not mean: it is not a statement that a disc will never exist. It is that none is coming for launch, and no later physical run has been announced.</p>",
        ),
        (
            "collector",
            "If you want to collect something",
            "<p>The Digital Deluxe Edition is the only premium tier, and it is worth being clear about what it is: the two extra outfits (Wulin Legend 武林传说 / 武林伝説, and Blood-Steel Form 机械魔躯 / 血鉄の魔躯), a digital artbook and the digital soundtrack. There is no physical goods bundle, no map, no statue and no steelbook attached to any edition.</p>"
            "<p>Both editions also carry the pre-order unlocks - the Treasure Basin accessory (聚宝盆) and the Legacy outfit (传承) - and S-GAME's own store copy states that pre-order content can be obtained through playing. The two Deluxe outfits are labelled exclusive, which is a separate question the official page does not settle.</p>",
        ),
        (
            "why-noisy",
            "Why this question keeps coming up",
            "<p>Comment-volume analysis around the trailer coverage put roughly a third of the week's discussion on the missing disc, heavily concentrated in Spanish-language communities, in the form of &quot;no disc, no buy&quot;. That is a real segment of the audience, not a rounding error, and it is the reason this page exists rather than being buried in an FAQ.</p>"
            "<p>The related searches tell the same story: &quot;physical&quot;, &quot;physical release&quot;, &quot;physical copy&quot;, &quot;ps5 physical copy&quot; and &quot;steelbook&quot; all appear among the rising queries for the game, alongside retailer names. Every one of them is asking the same question, and the answer is no.</p>",
        ),
        (
            "unknown",
            "What Is Still Unknown",
            "<ul>"
            "<li><strong>Whether a physical edition will ever appear.</strong> No announcement either way. Some publishers run boxed releases months later if a game sells well; there is no evidence S-GAME has planned that.</li>"
            "<li><strong>Whether a collector's edition exists.</strong> Reports of a collector's edition selling out quickly came from the Chinese market, which is a different distribution situation from the West.</li>"
            "<li><strong>Day-one patch size.</strong> The 134.857 GB figure is from the store listing before any launch update, so the real day-one requirement is unknown.</li>"
            "</ul>",
        ),
    ],
)

# ============ 2. Demo ============
write(
    "demo",
    "Phantom Blade Zero Demo - Is There a Playable Trial?",
    "There is no public playable demo of Phantom Blade Zero. A demo page briefly appeared on the Chinese PlayStation Store in August 2026 and was never announced, which is the whole story so far.",
    "phantom blade zero demo, pbz demo, phantom blade zero playable, is there a phantom blade zero demo",
    [
        ("Public demo", "None available"),
        ("Leaked store page", "Chinese PlayStation Store, 11 August 2026"),
        ("Announced since", "No - the 17 August State of Play did not mention a demo"),
        ("Event demos", "Playable booths at gamescom and Tokyo Game Show, invite and press sessions"),
        ("Demo footage online", "Yes - hands-on captures, which are not the same as a demo you can download"),
        ("Trial at launch", "None announced; no early access in any edition"),
    ],
    [
        (
            "answer",
            "The Short Answer",
            "<p><strong>No, there is no demo you can download and play.</strong> What exists is a large amount of captured gameplay from closed and event demos, which is easy to mistake for a public trial when searching.</p>",
        ),
        (
            "leak",
            "The store page that appeared and vanished",
            "<p>On 11 August 2026 a demo listing for Phantom Blade Zero surfaced on the Chinese PlayStation Store. The dedicated State of Play a week later - roughly twenty minutes of gameplay deep dive - did not announce a demo, and nothing has been said since. That is the complete public record.</p>"
            "<p>The honest reading: a demo was at some point planned, and either slipped or was cancelled. Absence of an announcement is not a cancellation notice, so this page records it as unannounced rather than as dead.</p>",
        ),
        (
            "event-vs-demo",
            "Event demos are not a demo",
            "<p>S-GAME has run playable sessions at Gamescom and Tokyo Game Show, and journalists have published long hands-on pieces from them - one outlet spent six hours in a near-final build at the studio, another reported a twenty-minute time-limited booth build at TGS 2025. Those are on-site, time-boxed and, for the press sessions, invitation-based.</p>"
            "<p>The distinction matters because the footage those sessions produced circulates as if it were current-gen review material. It is close to the finished game, but the builds were not the shipping build, and the frame-rate reports came from a PC preview, not from a retail PS5.</p>",
        ),
        (
            "try-before-buy",
            "What you can do instead",
            "<ul>"
            "<li>Watch the <strong>20-minute State of Play deep dive</strong>, which is real gameplay rather than a cinematic trailer, and is the closest thing to seeing the combat before buying.</li>"
            "<li>Read the <a href=\"/is-phantom-blade-zero-a-soulslike\">soulslike question</a> and the <a href=\"/difficulty-modes\">four difficulty modes</a> - the single biggest source of buyer regret for this genre is mismatched difficulty expectations, and this game has an explicit story mode.</li>"
            "<li>Check <a href=\"/pc-requirements\">PC requirements</a> before purchase. The install is around 135 GB and the preview build was reported to have rare but severe frame drops on high-end hardware.</li>"
            "<li>Steam refunds apply to games played under two hours within fourteen days, which is the practical safety net in the absence of a demo.</li>"
            "</ul>",
        ),
    ],
)

# ============ 3. 平台与独占 ============
write(
    "platforms",
    "Phantom Blade Zero Platforms - PS5, PC, and What About Xbox and Switch?",
    "Phantom Blade Zero releases on PlayStation 5 and PC via Steam and the Epic Games Store on 29 October 2026. No Xbox version and no Nintendo Switch or Switch 2 version has been announced.",
    "phantom blade zero xbox, phantom blade zero switch 2, is phantom blade zero ps5 exclusive, phantom blade zero platforms, phantom blade zero steam epic",
    [
        ("PlayStation 5", "Confirmed - digital, PS5 Pro Enhanced"),
        ("PC", "Confirmed - Steam and Epic Games Store"),
        ("Xbox Series X|S", "Not announced"),
        ("Nintendo Switch 2", "Not announced"),
        ("Physical disc", "None - see the physical edition page"),
        ("Cross-save between stores", "Not announced"),
        ("Chinese release", "Simultaneous - the game holds a mainland publishing licence"),
    ],
    [
        (
            "confirmed",
            "What is confirmed",
            "<p>Two platforms at launch: <strong>PlayStation 5</strong> and <strong>PC</strong>, with the PC version on both Steam and the Epic Games Store. The PS5 version is listed as PS5 Pro Enhanced, with DualSense adaptive triggers, haptic feedback and Tempest 3D audio called out in Sony's own product page.</p>"
            "<p>There is no Xbox and no Nintendo Switch or Switch 2 entry in any official material. Searches for both appear in the rising query lists, which means people are hoping rather than reacting to news.</p>",
        ),
        (
            "exclusive",
            "Is it a PlayStation exclusive?",
            "<p>Not in the sense that only PlayStation can play it - PC is a launch platform. What is true is that Sony is promoting it unusually hard for a third-party title: a dedicated standalone State of Play, which PlayStation Blog Japan covered in Japanese under the director's own byline, plus first-party-level hardware treatment on the Japanese store page.</p>"
            "<p>Whether there is a timed-exclusivity period on console has not been stated in the official material behind this page, so treat any specific month count as unconfirmed. What can be said with confidence: it is not a PlayStation-only game, because PC ships the same day.</p>",
        ),
        (
            "pc-stores",
            "Steam versus Epic",
            "<p>Both stores sell the same game at the same price, currently listed at $59.99 standard and $69.99 for the Digital Deluxe Edition in the US. The practical differences are launcher habit and friend lists, not features. Note that the PC build ships with <strong>Denuvo anti-tamper</strong>, which is the detail most likely to matter to the people deciding between storefronts.</p>",
        ),
        (
            "languages",
            "Language support, including Japanese and Chinese",
            "<p>The game ships with Simplified Chinese, Traditional Chinese, English, Japanese and other languages, and S-GAME's own site is published in all of them plus Korean, Spanish (two variants), Portuguese (two), French, German, Italian, Russian, Vietnamese and Thai.</p>"
            "<p>For Japanese buyers specifically: the support listed is <strong>interface and subtitles</strong>. Japanese voice acting does not appear in the Steam support table, so if dubbing matters to you, assume it is not there until a store page says otherwise.</p>"
            "<p>China releases simultaneously with the rest of the world because the game holds a mainland publishing licence, which is why the Chinese marketing push is unusually heavy for this kind of launch.</p>",
        ),
    ],
)
