#!/usr/bin/env python3
"""Rewrite the core pbzero.wiki pages from a pre-launch to a post-launch stance.

Why this exists
---------------
The game shipped on 2026-10-29. Five of the highest-traffic pages were still
written as "the game has not shipped yet", last touched between 2026-10-16 and
2026-10-22. Search Console showed 3 clicks / 81 impressions over 28 days, and
the URL Inspection API reported 12 of 15 sampled URLs as "Discovered - currently
not indexed". A page that says "coming October 29" a fortnight after launch is
the clearest possible staleness signal to a crawler, and it also loses every
post-launch query ("is it out", "patch notes", "physical edition 2027").

All facts below are sourced from post-launch reporting dated 2026-11-02 to
2026-11-09 and are labelled by source inside the page. Nothing is invented: where
S-GAME has not published something, the page says so.

Idempotent: re-running rewrites the same five pages plus patch-notes from
scratch, so it can be used again after the next patch.

    python3 scripts/post-launch-refresh.py --dry-run
    python3 scripts/post-launch-refresh.py
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "src", "data", "pages")
TODAY = "2026-11-11"

# --------------------------------------------------------------------- data

SALES_TABLE = """
<table>
<thead><tr><th>Date</th><th>What was published</th><th>Source</th></tr></thead>
<tbody>
<tr><td>October 28-29, 2026</td><td>Digital launch, PS5 and PC. Unlock at 02:00 UTC, which is the evening of 28 October in the US.</td><td>S-GAME / store listings</td></tr>
<tr><td>November 1, 2026</td><td>Steam concurrent peak of 833,921 players, the highest point of launch weekend.</td><td>SteamPeaks</td></tr>
<tr><td>November 2, 2026</td><td>Four million copies sold across all platforms in the first 72 hours.</td><td>S-GAME (@pbzero_official)</td></tr>
<tr><td>November 4, 2026</td><td>First post-launch patch, version 1.0302256.</td><td>Steam news / S-GAME</td></tr>
</tbody>
</table>
"""

PLATFORM_TABLE = """
<table>
<thead><tr><th>Platform</th><th>Status on 11 November 2026</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>PlayStation 5</td><td><strong>Available now</strong></td><td>Digital on the PlayStation Store; PS5 Pro Enhanced</td></tr>
<tr><td>Windows PC</td><td><strong>Available now</strong></td><td>Steam and Epic Games Store; Denuvo is listed on Steam</td></tr>
<tr><td>Xbox Series X|S</td><td>Not announced</td><td>No date, no window, no statement of intent</td></tr>
<tr><td>Nintendo Switch 2</td><td>Not announced</td><td>Nothing from S-GAME either way</td></tr>
<tr><td>Physical PS5 disc</td><td>2027, no date</td><td>Confirmed direction only; no month, price or disc layout</td></tr>
</tbody>
</table>
"""

PATCH_TABLE = """
<table>
<thead><tr><th>Change</th><th>Platform</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Hua, Deadly Betrothed</td><td>All</td><td>Uses grab attacks less often on Wayfarer and Pathbreaker only. Other difficulties unchanged.</td></tr>
<tr><td>Ray tracing shaders</td><td>PC</td><td>No longer compiled at start-up, which cuts launch time. If ray tracing was off, expect one short recompile on first launch after the patch.</td></tr>
<tr><td>Hit Sound Intensity / Hit Impact Sound Intensity</td><td>All</td><td>Two new sliders in the audio menu; weapon hit feedback was also strengthened.</td></tr>
<tr><td>Interact / Talk remapping</td><td>PC</td><td>Now remappable on keyboard and controller.</td></tr>
<tr><td>Bluetooth controller stutter</td><td>PC</td><td>Reduced.</td></tr>
<tr><td>NVIDIA Reflex</td><td>PC</td><td>Now works when set to Auto with V-Sync enabled.</td></tr>
<tr><td>Hair rendering</td><td>All</td><td>Fixed on certain AMD cards with specific driver versions.</td></tr>
<tr><td>Progression blockers</td><td>All</td><td>Fixed cases where the story could not advance, plus spots where the character could get stuck.</td></tr>
<tr><td>Third-party mods</td><td>PC</td><td>S-GAME warns some mods are not compatible with this build; remove them if you hit problems.</td></tr>
</tbody>
</table>
"""

# ------------------------------------------------------------------- pages

PAGE_DATA = {
    "release-date": {
        "slug": "release-date",
        "title": "Phantom Blade Zero Release Date - Out Now on PS5 and PC",
        "description": (
            "Phantom Blade Zero released on October 29, 2026 for PS5 and PC and is out now. "
            "Launch sales, the Steam peak, the first patch, and why some pages still list September 9."
        ),
        "keyword": "phantom blade zero release date, when does phantom blade zero come out, is phantom blade zero out, phantom blade zero release",
        "lastUpdated": TODAY,
        "facts": [
            {"label": "Released", "value": "October 29, 2026 - out now"},
            {"label": "Platforms", "value": "PlayStation 5, Windows PC (Steam, Epic)"},
            {"label": "Copies sold", "value": "4 million in 72 hours"},
            {"label": "Steam concurrent peak", "value": "833,921 on November 1, 2026"},
            {"label": "First patch", "value": "1.0302256, November 4, 2026"},
            {"label": "Physical disc", "value": "2027, no date"},
        ],
        "sections": [
            {
                "id": "status",
                "title": "The Short Answer: It Is Out Now",
                "content": (
                    "<p>Phantom Blade Zero released on <strong>October 29, 2026</strong> for PlayStation 5 and Windows PC "
                    "through Steam and the Epic Games Store. There is no countdown left to wait for: the digital game is on "
                    "sale, it has been patched once, and the disc version is the only thing still in the future.</p>"
                    "<p>Unlock time was 02:00 UTC on 29 October. That lands on the evening of 28 October in the United States, "
                    "which is why some pages still say the 28th. Both dates are correct for their region and the game has "
                    "been live on both since.</p>"
                    "<p>If you are here to decide whether to buy, the practical questions are price, platform and length. "
                    "The <a href=\"/pre-order-guide\">buying guide</a> covers editions and what is actually on sale now, "
                    "the <a href=\"/platforms\">platform page</a> covers Xbox and Switch 2, and "
                    "<a href=\"/how-long-to-beat\">how long to beat</a> covers playtime.</p>"
                ),
            },
            {
                "id": "first-two-weeks",
                "title": "What Happened After Launch",
                "content": (
                    "<p>These are the numbers S-GAME and the storefronts published in the first fortnight, rather than "
                    "pre-release estimates:</p>" + SALES_TABLE +
                    "<p>Two cautions on those figures. Four million is a combined digital total; S-GAME has not split it by "
                    "platform. Third-party estimates put the split at roughly 3.1 million on Steam and 1.2 million on "
                    "PlayStation by 3 November, but that is a model built from store signals rather than studio data, and it "
                    "excludes Epic. Concurrent players are PC only, so 833,921 is not a sales number either.</p>"
                ),
            },
            {
                "id": "patch",
                "title": "The First Patch Arrived on November 4",
                "content": (
                    "<p>Version 1.0302256 is the first post-launch update. It is mostly quality-of-life work rather than a "
                    "balance overhaul: one boss made less punishing on the two lower difficulties, faster PC start-up, new "
                    "audio sliders, and fixes for progression blockers. The full breakdown, including the shader change that "
                    "will make your first PC launch after updating look slow, is on the "
                    "<a href=\"/patch-notes\">patch notes page</a>.</p>"
                ),
            },
            {
                "id": "september-9",
                "title": "Why You Still See September 9, 2026",
                "content": (
                    "<p>September 9 was the original date, announced on stage at The Game Awards in December 2025. The 9/9 "
                    "symbolism was deliberate: it mirrors the 66-day premise of the story. In June 2026 S-GAME moved the "
                    "release to October 29 to allow more development time.</p>"
                    "<p>Any page still presenting September 9 as the date has not been updated since that June announcement. "
                    "There was only ever one delay, and there has been no second delay and no further movement since.</p>"
                ),
            },
            {
                "id": "physical",
                "title": "The Disc Version Is 2027, Not Now",
                "content": (
                    "<p>On 22 October, alongside the launch trailer, S-GAME said the physical PlayStation 5 edition arrives "
                    "in 2027. There is still no month, no price and no note on disc layout or whether the build is on the "
                    "disc or downloaded. Everything on sale today is digital.</p>"
                    "<p>Details on what the boxed version is expected to contain, and what to do if you specifically want a "
                    "disc, are on the <a href=\"/physical-edition\">physical edition page</a>.</p>"
                ),
            },
            {
                "id": "timeline",
                "title": "Full Release Timeline",
                "content": (
                    "<table>"
                    "<thead><tr><th>Date</th><th>Event</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>24 May 2023</td><td>Revealed at the PlayStation Showcase with a debut trailer</td></tr>"
                    "<tr><td>January 2025</td><td>A trailer confirms a release date will be announced during 2025</td></tr>"
                    "<tr><td>December 2025</td><td>Release date announced at The Game Awards: September 9, 2026</td></tr>"
                    "<tr><td>June 2026</td><td>Release moved to October 29, 2026 for additional polish</td></tr>"
                    "<tr><td>11 August 2026</td><td>Pre-orders open</td></tr>"
                    "<tr><td>October 2026</td><td>PS5 download size of 134.857 GB surfaces from store backend data; preload window announced</td></tr>"
                    "<tr><td>22 October 2026</td><td>S-GAME confirms a physical PS5 edition for 2027</td></tr>"
                    "<tr><td>29 October 2026</td><td>Digital launch on PS5 and PC</td></tr>"
                    "<tr><td>1 November 2026</td><td>Steam concurrent peak of 833,921</td></tr>"
                    "<tr><td>2 November 2026</td><td>S-GAME announces 4 million copies sold in 72 hours</td></tr>"
                    "<tr><td>4 November 2026</td><td>Patch 1.0302256 released</td></tr>"
                    "</tbody>"
                    "</table>"
                ),
            },
            {
                "id": "faq",
                "title": "Release Date Questions",
                "content": (
                    "<h3>When does Phantom Blade Zero come out?</h3>"
                    "<p>It came out on October 29, 2026 and is available now on PS5 and PC.</p>"
                    "<h3>Is Phantom Blade Zero out yet?</h3>"
                    "<p>Yes. The digital release went live at 02:00 UTC on 29 October 2026, with the first patch following "
                    "on 4 November.</p>"
                    "<h3>Was Phantom Blade Zero delayed?</h3>"
                    "<p>Once. It moved from September 9, 2026 to October 29, 2026 in June 2026, and has not moved since.</p>"
                    "<h3>Is there a physical version at launch?</h3>"
                    "<p>No. Launch was digital only; the boxed PS5 edition is a 2027 release with no date yet.</p>"
                ),
            },
            {
                "id": "where-next",
                "title": "Where to Go Next",
                "content": (
                    "<ul>"
                    "<li><a href=\"/reviews\">Reviews and scores</a> - what the critics said and what players report about performance</li>"
                    "<li><a href=\"/pc-requirements\">PC requirements and performance</a> - including the Steam Deck situation</li>"
                    "<li><a href=\"/boss-list\">The boss list</a> - every encounter in order</li>"
                    "<li><a href=\"/trophy-guide\">Trophy guide</a> - the platinum path and what is missable</li>"
                    "<li><a href=\"/difficulty-modes\">Difficulty modes</a> - what each setting actually changes</li>"
                    "</ul>"
                ),
            },
        ],
    },

    "platforms": {
        "slug": "platforms",
        "title": "Phantom Blade Zero Platforms - PS5 and PC Now, Xbox Not Announced",
        "description": (
            "Phantom Blade Zero is out on PS5 and PC via Steam and Epic. Xbox and Switch 2 have never been announced, "
            "the PS5 disc version is 2027, and this page tracks the status of every platform."
        ),
        "keyword": "phantom blade zero xbox, phantom blade zero platforms, is phantom blade zero coming to xbox, phantom blade zero switch 2, phantom blade zero pc, phantom blade zero steam",
        "lastUpdated": TODAY,
        "facts": [
            {"label": "PlayStation 5", "value": "Available now - digital, PS5 Pro Enhanced"},
            {"label": "PC", "value": "Available now - Steam and Epic Games Store"},
            {"label": "Xbox Series X|S", "value": "Not announced"},
            {"label": "Nintendo Switch 2", "value": "Not announced"},
            {"label": "Physical disc", "value": "PS5, 2027, no date"},
            {"label": "Price", "value": "$59.99 / GBP 49.99 / EUR 59.99"},
        ],
        "sections": [
            {
                "id": "status",
                "title": "Platform Status Right Now",
                "content": (
                    "<p>Phantom Blade Zero shipped on 29 October 2026 on exactly two platforms, and both are live. "
                    "The table is the whole answer; everything below it is the detail behind the \"not announced\" rows.</p>"
                    + PLATFORM_TABLE
                ),
            },
            {
                "id": "xbox",
                "title": "Is Phantom Blade Zero Coming to Xbox?",
                "content": (
                    "<p>No Xbox version has been announced. Not a date, not a window, not a stated intention. That has been "
                    "true since the game was revealed at the PlayStation Showcase in 2023, and launching on two platforms "
                    "has not changed it.</p>"
                    "<p>Two things are worth keeping separate. First, \"not announced\" is not \"exclusive forever\": "
                    "S-GAME has never described the game as a permanent PlayStation exclusive, and the PC version ships on "
                    "Epic as well as Steam, which shows the studio is not tying itself to one storefront. Second, there is "
                    "no timed-exclusivity window in any public document, so anyone quoting \"Xbox in six months\" or "
                    "\"Xbox in a year\" is inventing it.</p>"
                    "<p>If an Xbox version is announced it will be posted here and on the <a href=\"/news\">news page</a> "
                    "the same day. Until then, treat any date you see elsewhere as unsourced.</p>"
                ),
            },
            {
                "id": "switch",
                "title": "Switch 2",
                "content": (
                    "<p>Nothing announced. The game is an Unreal Engine 5 title that does not hold 30 frames per second on "
                    "Steam Deck in a post-patch retest, so a Switch 2 port would be a substantial technical project rather "
                    "than a straight conversion. There is no evidence one is in progress.</p>"
                ),
            },
            {
                "id": "pc-stores",
                "title": "Steam or Epic?",
                "content": (
                    "<p>Both sell the same game at the same price. Steam is the version with the larger public player "
                    "count, workshop-adjacent modding, and the store page that carries the Denuvo label. Epic is the "
                    "alternative storefront with the same build.</p>"
                    "<p>Practically: if you care about mods, controller remapping tools or refunds through playtime, Steam "
                    "is the safer default. Nothing about the game's content differs between them.</p>"
                ),
            },
            {
                "id": "performance",
                "title": "Platform Performance Notes",
                "content": (
                    "<p><strong>PS5.</strong> The console version is the one S-GAME tuned first; the launch patch notes mark "
                    "several fixes as PC-only, which implies the console build did not need them. PS5 Pro Enhanced is "
                    "listed on the store page.</p>"
                    "<p><strong>PC.</strong> The 4 November patch changed shader compilation, so start-up is faster but the "
                    "first launch after updating can pause for a recompile if you play with ray tracing off. Bluetooth "
                    "controller stutter was reduced in the same build, and NVIDIA Reflex now works on Auto with V-Sync on. "
                    "The <a href=\"/pc-requirements\">PC requirements page</a> covers hardware and the Deck situation.</p>"
                ),
            },
            {
                "id": "faq",
                "title": "Platform Questions",
                "content": (
                    "<h3>Is Phantom Blade Zero coming to PC?</h3>"
                    "<p>It is already on PC. Steam and Epic Games Store both sell it at the same price as the PS5 version.</p>"
                    "<h3>Is Phantom Blade Zero a PlayStation exclusive?</h3>"
                    "<p>It launched on PS5 and PC on the same day, so no. It is a console launch exclusive at most, and "
                    "S-GAME has never described the arrangement as permanent.</p>"
                    "<h3>Will Phantom Blade Zero be on Xbox?</h3>"
                    "<p>Not announced. There is no date, no window and no stated plan.</p>"
                    "<h3>Does it run on Steam Deck?</h3>"
                    "<p>It is playable but does not hold 30 frames per second in a post-patch retest, so it is not a "
                    "comfortable Deck game.</p>"
                ),
            },
        ],
    },

    "pre-order-guide": {
        "slug": "pre-order-guide",
        "title": "Phantom Blade Zero Editions, Price and Pre-Order Bonus - What You Can Still Buy",
        "description": (
            "Pre-orders closed at launch on October 29, 2026. What the pre-order bonus was, what each edition contains, "
            "current prices on PS5 and PC, and whether the bonus is still obtainable in-game."
        ),
        "keyword": "phantom blade zero preorder, phantom blade zero pre order, phantom blade zero editions, phantom blade zero price, phantom blade zero deluxe edition",
        "lastUpdated": TODAY,
        "facts": [
            {"label": "Pre-orders", "value": "Closed - game released October 29, 2026"},
            {"label": "Pre-order bonus", "value": "Treasure Basin accessory (+10% Remnant Dust drop rate) + Legacy appearance"},
            {"label": "Bonus exclusivity", "value": "Obtainable in-game; the two Deluxe outfits are labelled exclusive"},
            {"label": "Standard price", "value": "$59.99 / GBP 49.99 / EUR 59.99"},
            {"label": "China pricing", "value": "CNY 268 standard, CNY 328 deluxe"},
            {"label": "Deluxe upgrade", "value": "Sold separately in most regions"},
        ],
        "sections": [
            {
                "id": "now",
                "title": "Pre-Orders Are Over - Here Is What That Changes",
                "content": (
                    "<p>Pre-orders opened on 11 August 2026 and closed when the game released on 29 October 2026. "
                    "You can still buy the game; you cannot still buy it early, and the pre-order bonus is no longer tied "
                    "to a purchase.</p>"
                    "<p>That matters less than it sounds. The bonus item, the Treasure Basin accessory, is also obtainable "
                    "inside the game, so nothing about a late purchase locks you out of a build. The two Deluxe outfits are "
                    "the only items described as exclusive, and those come with the Deluxe edition rather than with timing.</p>"
                ),
            },
            {
                "id": "editions",
                "title": "What Each Edition Contains",
                "content": (
                    "<table>"
                    "<thead><tr><th>Edition</th><th>Contents</th><th>Who it is for</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Standard</td><td>Base game</td><td>Anyone who just wants to play; the deluxe extras are cosmetic and convenience, not content</td></tr>"
                    "<tr><td>Deluxe</td><td>Base game, two outfits labelled exclusive, plus the digital extras bundled in that tier</td><td>Collectors of cosmetics and anyone who wants the outfit set complete</td></tr>"
                    "<tr><td>Physical PS5</td><td>Not on sale yet - S-GAME says 2027</td><td>Disc collectors only, and only if you can wait</td></tr>"
                    "</tbody>"
                    "</table>"
                    "<p>The upgrade path matters here: in most regions the Deluxe content is sold as a separate upgrade, "
                    "so buying Standard now and upgrading later costs the same as buying Deluxe up front. There is no "
                    "reason to decide under time pressure.</p>"
                ),
            },
            {
                "id": "worth",
                "title": "Is the Deluxe Edition Worth It?",
                "content": (
                    "<p>Nothing in the Deluxe tier changes what you can do in the game. There are no exclusive bosses, "
                    "no weapons behind the paywall, no difficulty gates. If you are choosing on value, Standard is the "
                    "correct answer and the upgrade can be added whenever you decide you want the outfits.</p>"
                    "<p>The one group that should think twice is disc collectors: the boxed PS5 version is a 2027 item, "
                    "so waiting for it means waiting a year. The <a href=\"/physical-edition\">physical edition page</a> "
                    "covers what is and is not known about that release.</p>"
                ),
            },
            {
                "id": "where",
                "title": "Where to Buy",
                "content": (
                    "<ul>"
                    "<li><strong>PlayStation 5</strong> - PlayStation Store, digital only until 2027</li>"
                    "<li><strong>PC</strong> - Steam or Epic Games Store, same price on both</li>"
                    "<li><strong>China</strong> - CNY 268 standard and CNY 328 deluxe on the domestic storefronts</li>"
                    "</ul>"
                    "<p>Regional pricing varies, so the numbers above are list prices rather than promises. Store links, "
                    "platform differences and the PS5 Pro situation are on the <a href=\"/platforms\">platforms page</a>.</p>"
                ),
            },
            {
                "id": "faq",
                "title": "Buying Questions",
                "content": (
                    "<h3>Can I still pre-order Phantom Blade Zero?</h3>"
                    "<p>No. Pre-orders closed when the game released on 29 October 2026, but the game itself is on sale "
                    "at the same price.</p>"
                    "<h3>Is the pre-order bonus still available?</h3>"
                    "<p>The Treasure Basin accessory is obtainable inside the game regardless of when you buy, so you have "
                    "not missed a build-defining item.</p>"
                    "<h3>How much does Phantom Blade Zero cost?</h3>"
                    "<p>$59.99 in the US, GBP 49.99 in the UK and EUR 59.99 in the eurozone, with the Deluxe tier above "
                    "that. In China it is CNY 268 standard and CNY 328 deluxe.</p>"
                    "<h3>Should I wait for the physical edition?</h3>"
                    "<p>Only if you specifically want a disc. The boxed PS5 version is a 2027 release with no date, and "
                    "everything on sale now is digital.</p>"
                ),
            },
        ],
    },

    "physical-edition": {
        "slug": "physical-edition",
        "title": "Phantom Blade Zero Physical Edition - PS5 Disc Is a 2027 Release",
        "description": (
            "The PS5 physical edition of Phantom Blade Zero is confirmed for 2027, with no month, price or disc layout "
            "yet. What S-GAME has said, what a boxed release normally means, and how to play now if you want a disc."
        ),
        "keyword": "phantom blade zero physical release, phantom blade zero physical copy, phantom blade zero ps5 disc, phantom blade zero physical edition",
        "lastUpdated": TODAY,
        "facts": [
            {"label": "Physical PS5", "value": "2027 - three tiers announced, no date"},
            {"label": "Tiers", "value": "Standard, Deluxe, Ultimate (collector's steelbook)"},
            {"label": "Physical PC", "value": "Not announced"},
            {"label": "Digital release", "value": "October 29, 2026 - available now"},
            {"label": "Price", "value": "Not announced for any boxed tier"},
        ],
        "sections": [
            {
                "id": "status",
                "title": "Where the Disc Version Stands",
                "content": (
                    "<p>S-GAME announced on 21-22 October 2026, alongside the launch trailer, that physical PlayStation 5 "
                    "editions are coming in 2027. Three tiers were named: a <strong>standard edition</strong>, a "
                    "<strong>Deluxe edition</strong>, and an <strong>Ultimate edition in a collector's steelbook</strong>. "
                    "Gematsu, 3DM and 4Gamer all carry the same three tiers, so this is a confirmed announcement rather "
                    "than a rumour.</p>"
                    "<p>What was not announced is everything else: no month, no day, no price, no regional availability, "
                    "and no statement on whether the disc carries the full build or a download stub. The launch itself "
                    "was digital only, so anyone who wants a box is waiting, and the honest answer to \"when can I buy a "
                    "disc\" is still \"sometime in 2027\".</p>"
                    "<table>"
                    "<thead><tr><th>Tier</th><th>Status</th><th>Contents published?</th></tr></thead>"
                    "<tbody>"
                    "<tr><td>Standard (PS5)</td><td>Announced for 2027</td><td>No</td></tr>"
                    "<tr><td>Deluxe (PS5)</td><td>Announced for 2027</td><td>No - digital Deluxe extras assumed, not confirmed</td></tr>"
                    "<tr><td>Ultimate (PS5, collector's steelbook)</td><td>Announced for 2027</td><td>No</td></tr>"
                    "</tbody>"
                    "</table>"
                ),
            },
            {
                "id": "play-asia",
                "title": "The Play-Asia Listing That Disappeared",
                "content": (
                    "<p>Before the announcement, Play-Asia - a retailer that routinely stocks Asian imports - listed a "
                    "physical edition and then removed the listing, reportedly after being told a physical version would "
                    "not be available. That sequence is why the 2027 news should be read carefully rather than as a "
                    "reversal: a boxed version appears to have been planned, cancelled, and then announced again for a "
                    "different year.</p>"
                    "<p>The accurate summary of the record is that a physical release exists as an announcement now, and "
                    "that nothing about it - date, contents, regions - has been published in enough detail to plan a "
                    "purchase around.</p>"
                ),
            },
            {
                "id": "why-2027",
                "title": "Why a Disc a Year Later",
                "content": (
                    "<p>A 2027 date for a game that shipped digitally in 2026 is unusual but not inexplicable. Pressing "
                    "discs requires a build to be frozen and certified, manufacturing slots to be booked, and retail "
                    "distribution to be arranged per region - none of which the digital launch needed. A studio that "
                    "prioritised a simultaneous global digital launch would naturally schedule the box afterwards.</p>"
                    "<p>It also means a 2027 disc would ship with a year of patches baked in or downloadable, which is "
                    "usually the better version to own. That is the argument for waiting, if you are on the fence.</p>"
                ),
            },
            {
                "id": "play-now",
                "title": "If You Want to Play Before 2027",
                "content": (
                    "<p>There is no way to get a disc now. The options are the PlayStation Store for PS5, or Steam and "
                    "Epic for PC. Prices, regional differences and the Deluxe contents are on the "
                    "<a href=\"/pre-order-guide\">buying guide</a>, and the platform breakdown is on the "
                    "<a href=\"/platforms\">platforms page</a>.</p>"
                    "<p>One practical note for collectors: buying digital now does not disqualify you from buying the disc "
                    "later, but it does mean paying twice if you want both. There is no announced upgrade or disc-for-digital "
                    "programme.</p>"
                ),
            },
            {
                "id": "unknown",
                "title": "What Is Still Unknown",
                "content": (
                    "<ul>"
                    "<li>Month, price and regional availability of the 2027 disc</li>"
                    "<li>Whether the disc build is complete or requires a download</li>"
                    "<li>What the boxed Deluxe and Ultimate tiers contain beyond the case and steelbook</li>"
                    "<li>Whether a physical PC release will follow</li>"
                    "</ul>"
                    "<p>Those four items are the whole list of open questions. Anything else you read about the boxed "
                    "version, including prices and box art, is speculation until S-GAME publishes it.</p>"
                    "<p>One detail worth keeping straight meanwhile: the digital Deluxe edition is a separate product "
                    "from the boxed tiers and is on sale now. It contains the two outfits (Wulin Legend and Blood-Steel "
                    "Form), a digital artbook and the digital soundtrack - see the "
                    "<a href=\"/pre-order-guide\">buying guide</a> for the full comparison.</p>"
                ),
            },
            {
                "id": "faq",
                "title": "Physical Edition Questions",
                "content": (
                    "<h3>When is the Phantom Blade Zero physical edition out?</h3>"
                    "<p>2027. S-GAME confirmed the year on 22 October 2026 and has not published a month or a day since.</p>"
                    "<h3>Is there a physical copy available now?</h3>"
                    "<p>No. The launch was digital only on PS5, Steam and Epic.</p>"
                    "<h3>Will there be a collector's edition?</h3>"
                    "<p>Yes - an Ultimate edition in a collector's steelbook was named in the announcement. Its contents "
                    "have not been published.</p>"
                    "<h3>Is a physical PC version coming?</h3>"
                    "<p>Not announced. Only PS5 discs have been confirmed.</p>"
                ),
            },
        ],
    },

    "patch-notes": {
        "slug": "patch-notes",
        "title": "Phantom Blade Zero Patch Notes - Version 1.0302256",
        "description": (
            "The first post-launch Phantom Blade Zero patch, version 1.0302256, arrived on November 4, 2026. Full "
            "change list, the Hua nerf, the shader change that slows your first launch, and what is still unpatched."
        ),
        "keyword": "phantom blade zero patch notes, phantom blade zero update, phantom blade zero 1.0302256, phantom blade zero new patch, phantom blade zero hua nerf",
        "lastUpdated": TODAY,
        "facts": [
            {"label": "Latest patch", "value": "1.0302256, November 4, 2026"},
            {"label": "PS5 build", "value": "1.302.289 (as reported)"},
            {"label": "PC download", "value": "~3.7 GB"},
            {"label": "Balance changes", "value": "Hua grab frequency, Wayfarer and Pathbreaker only"},
            {"label": "Biggest technical change", "value": "Ray tracing shaders no longer compile at start-up"},
        ],
        "sections": [
            {
                "id": "what",
                "title": "What Version 1.0302256 Changes",
                "content": (
                    "<p>S-GAME published the notes on its official site on 3 November and on Steam on 4 November. It is a "
                    "stability and comfort patch rather than a content patch: no new areas, no new weapons, one boss "
                    "adjustment, and a meaningful change to how the PC build starts up.</p>"
                    + PATCH_TABLE
                ),
            },
            {
                "id": "hua",
                "title": "The Hua Change, Explained",
                "content": (
                    "<p>Hua, Deadly Betrothed now uses grab attacks less often - but only on Wayfarer and Pathbreaker. "
                    "The two higher difficulties are untouched, which tells you what the complaint was: not that the fight "
                    "is unfair, but that it punishes players who are still learning the deflect window.</p>"
                    "<p>Hua is the first optional boss and gates a quest tied to the true ending, so players who bounced "
                    "off her early were also locking themselves out of a major branch. If you gave up on her before the "
                    "patch, retry on Wayfarer. The <a href=\"/boss-list\">boss list</a> has her position in the order, and "
                    "the <a href=\"/true-ending\">true ending page</a> covers the quest she unlocks.</p>"
                ),
            },
            {
                "id": "shaders",
                "title": "Why Your First Launch After Updating Is Slow",
                "content": (
                    "<p>Ray tracing shaders are no longer compiled at start-up. That is the single biggest start-up "
                    "improvement in the patch, and it has one side effect worth knowing:</p>"
                    "<ul>"
                    "<li><strong>Ray tracing was off</strong> - you will recompile shaders once on the first launch after "
                    "updating. S-GAME says it is short. Do not force-quit during it.</li>"
                    "<li><strong>Ray tracing was on</strong> - no recompile, you can launch straight in.</li>"
                    "<li><strong>You turn ray tracing on later</strong> - the ray tracing shaders compile separately at the "
                    "next restart.</li>"
                    "</ul>"
                    "<p>Mods are the other thing to watch. S-GAME warns that some third-party mods are not compatible with "
                    "this build and advises removing them if the game misbehaves after updating. If you run an "
                    "Ultra-style graphics mod, expect to reinstall it after the patch.</p>"
                ),
            },
            {
                "id": "unpatched",
                "title": "What the Patch Does Not Fix",
                "content": (
                    "<p>The notes do not mention performance on Steam Deck, and a post-patch retest still could not hold "
                    "30 frames per second. If Deck performance is your deciding factor, that has not changed. "
                    "The <a href=\"/pc-requirements\">PC requirements page</a> tracks it.</p>"
                    "<p>Nothing in the patch addresses the PS5 build number reported as 1.302.289, and S-GAME has not said "
                    "whether the console version received every item on this list. Several entries are tagged PC-only, and "
                    "the rest carry no platform note at all.</p>"
                ),
            },
        ],
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    written = []
    for slug, data in PAGE_DATA.items():
        path = os.path.join(PAGES, f"{slug}.json")
        old = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                old = json.load(fh)
        body = dict(data)
        body.setdefault("slug", slug)
        words = sum(len(s["content"].split()) for s in body["sections"])
        status = "改写" if old else "新建"
        prev = sum(len(s["content"].split()) for s in old["sections"]) if old else 0
        print(f"{status} {slug:<18} {prev:>4}词 → {words:>4}词  {body['title'][:56]}")
        if not args.dry_run:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(body, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
        written.append(slug)

    print(f"\n共 {len(written)} 页。{'（dry-run，未写入）' if args.dry_run else '已写入 src/data/pages/'}")
    if not args.dry_run:
        print("下一步：npm run build 验证，然后跑 scripts/submit-index.py 推送新页。")


if __name__ == "__main__":
    sys.exit(main())
