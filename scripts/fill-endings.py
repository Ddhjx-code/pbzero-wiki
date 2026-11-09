#!/usr/bin/env python3
"""Fill the post-launch ending pages.

Replaces the pre-launch "endings are not detailed yet" page with the four
endings that actually exist, and adds a dedicated true-ending checklist page.
Every claim carries its source; where two outlets disagree the page says so
instead of picking one.
"""
import json
import os

PAGES = "src/data/pages"
STAMP = "2026-11-09"


def write(slug, data):
    path = os.path.join(PAGES, f"{slug}.json")
    data["lastUpdated"] = STAMP
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {path}  ({len(json.dumps(data))} bytes)")


LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'

# ---------------------------------------------------------------- endings
endings = {
    "title": "Phantom Blade Zero Endings - All 4 Endings and How to Unlock Them",
    "description": "Phantom Blade Zero has four endings, not eight. Annihilation, Long Roar, the true ending Final Battle, and the secret Undying Grudge - what each one needs, and which mistake locks you out of the platinum.",
    "keyword": "phantom blade zero endings, phantom blade zero how many endings, phantom blade zero true ending, phantom blade zero final battle, phantom blade zero undying grudge",
    "facts": [
        {"label": "Number of endings", "value": "4 - confirmed post-launch, superseding the '8 endings' figure repeated before release"},
        {"label": "Default ending", "value": "Annihilation - triggers if no purple Tales are completed"},
        {"label": "True ending", "value": "Final Battle, called the Perfect Ending internally - needs every purple Tale done before Mount Soulrend"},
        {"label": "Secret ending", "value": "Undying Grudge - only from failing the 66 Days mode"},
        {"label": "Second playthrough needed", "value": "Only for Undying Grudge. The other three come from one save"},
        {"label": "Trophy tie-in", "value": "With Heart and Blood (Gold) needs the true ending; the normal ending has no trophy"},
        {"label": "Point of no return", "value": "The climb to Mount Soulrend, after the Mirage Estate in Pangzhen"},
    ],
    "sections": [
        {
            "id": "short-answer",
            "title": "The Short Answer",
            "content": (
                "<p>Four endings. <strong>Annihilation</strong> is what you get for playing the story and nothing else. "
                "<strong>Long Roar</strong> is the middle tier, unlocked with two specific Tales. "
                "<strong>Final Battle</strong> is the true ending and needs essentially all the purple Tales plus five "
                "Lóng Pillar trials and four Acolyte masks. <strong>Undying Grudge</strong> is a separate secret, "
                "and it does not come from playing well - it comes from wiping out in the 66 Days mode.</p>"
                "<p>Before release this page listed eight endings as a possibility and said none were detailed. "
                "That was wrong. IGN's post-launch ending guide puts the count at four, each with its own cutscene, "
                "and the in-game ending names match across IGN, Polygon and GamingBolt. The eight-ending figure "
                "was never sourced and has been removed from this site.</p>"
            ),
        },
        {
            "id": "all-four",
            "title": "All Four Endings",
            "content": (
                "<table><thead><tr><th>Ending</th><th>In-game name</th><th>What unlocks it</th><th>Trophy</th></tr></thead>"
                "<tbody>"
                "<tr><td><strong>Normal</strong></td><td>Annihilation</td><td>Reach the final boss without completing the purple Tales, "
                "especially <em>Secrets at the Heart of the Lake</em></td><td>None</td></tr>"
                "<tr><td><strong>Middle</strong></td><td>Long Roar</td><td><em>Secrets at the Heart of the Lake</em> plus "
                "<em>Bloodline Awakening</em> - all five pillars, Gold-Masked One beaten five times</td><td><span "
                'style="color:#8a8a99">Not separately tracked</span></td></tr>'
                "<tr><td><strong>True</strong></td><td>Final Battle / Perfect Ending</td><td>Every purple Tale, both Crystal Puppet Eyes, "
                "the Four Guardians' Mirror realm and all five Lóng Pillars, done before the climb to Mount Soulrend</td>"
                "<td>With Heart and Blood (Gold)</td></tr>"
                "<tr><td><strong>Secret</strong></td><td>Undying Grudge (饮恨江湖)</td><td>Unlock 66 Days after any completion, then "
                "lose all 66 lives</td><td>None</td></tr>"
                "</tbody></table>"
                "<p>Only the true ending is tied to a trophy, so a pure platinum run only has to satisfy one of these four branches. "
                "Everything above the true ending row is optional story content, not optional difficulty.</p>"
            ),
        },
        {
            "id": "normal-ending",
            "title": "Annihilation - the Default Ending",
            "content": (
                "<p>The default. Fight to the last boss and finish, without clearing the purple Tales, and the credits roll on "
                "<em>Annihilation</em>. Nothing is locked by choosing it - you can keep exploring after the credits - but the "
                "True Ending fight will not trigger, and several side Tales become unfinishable once Mount Soulrend is behind you.</p>"
                "<p>This is the one ending with no trophy attached. If you are here for the platinum, stopping at Annihilation "
                "means a second run for the story content you skipped.</p>"
            ),
        },
        {
            "id": "long-roar",
            "title": "Long Roar - the Two-Tale Ending",
            "content": (
                "<p>Long Roar sits between the default and the true ending, and it is the one the guides disagree about least. "
                "The two requirements IGN and GamingBolt both name:</p>"
                "<ul>"
                "<li><strong>Secrets at the Heart of the Lake</strong> - the Meigu Lake mirror Tale. Collect all four Acolyte masks, "
                "take a boat to the western edge of the lake, pass through the mirror and clear the realm inside.</li>"
                "<li><strong>Bloodline Awakening</strong> - find and destroy five Lóng Pillars, each guarded by the Gold-Masked One. "
                "The fights get harder as the story advances and you have to win every one.</li>"
                "</ul>"
                "<p>Because the pillar fights scale with progress, players who leave this to the endgame face the hardest version of "
                "five duels back to back. Polygon's recommendation is to do the pillars as you pass them.</p>"
            ),
        },
        {
            "id": "true-ending-summary",
            "title": "Final Battle - the True Ending",
            "content": (
                "<p>The true ending is not a choice, it is a checklist. Clear the purple Tales and the item requirements before "
                "the point of no return and a second boss fight appears after the regular final boss. Win that, and you get the "
                "<strong>With Heart and Blood</strong> trophy.</p>"
                "<p>The long version - every Tale, every mask, every pillar, and the mistakes that quietly void the whole thing - "
                'is on <a href="/true-ending" ' + LINK + ">the true ending checklist</a>. The short version:</p>"
                "<ul>"
                "<li>All purple Tales, including the missable ones in Pangzhen, done before the Mirage Estate</li>"
                "<li>Both Crystal Puppet Eyes - one from the Mountain of Imprisonment, one from the Crimson Manor secret boss</li>"
                "<li>Four Acolyte masks from four scarecrow fights, taken to the mirror at Meigu Lake</li>"
                "<li>Five Lóng Pillars, including the one inside the Four Guardians' Mirror realm</li>"
                "<li>Quick Hand Zhang's fetch requests, all of them</li>"
                "</ul>"
            ),
        },
        {
            "id": "secret-ending",
            "title": "Undying Grudge - the Ending You Get by Losing",
            "content": (
                "<p>The fourth ending is the strangest thing in the game. Finish the story once at any difficulty and "
                "<strong>66 Days</strong> unlocks - a mode that gives you 66 lives for the whole run. Run out and it is a "
                "permanent game over: the save is deleted, not reloaded.</p>"
                "<p>Let that happen and you get <em>Undying Grudge</em>, a unique cutscene that no other route shows. "
                "It is the only ending that requires a separate playthrough, and the only one you cannot reach by being good "
                "at the game. This site has not seen the cutscene itself and is not going to describe it second-hand - "
                "the existence and trigger condition are what IGN and the Chinese guides both confirm.</p>"
            ),
        },
        {
            "id": "mistakes",
            "title": "What Actually Voids the True Ending",
            "content": (
                "<p>Three failure modes come up repeatedly in the guides, and all three are silent - the game does not tell you "
                "that a Tale has expired.</p>"
                "<table><thead><tr><th>Mistake</th><th>Why it costs you</th></tr></thead><tbody>"
                "<tr><td>Doing the purple Tales after Mount Soulrend</td><td>Several expire at the point of no return. "
                "The endgame warning tells you content will lock - it does not tell you which content.</td></tr>"
                "<tr><td>Skipping the Mountain of Imprisonment</td><td>The region is optional for the story, which makes it easy "
                "to walk past. It holds the Yin Crystal Puppet Eye, and without both eyes the Puppet No. 99 step cannot finish.</td></tr>"
                "<tr><td>Taking the endgame warning as proof you failed</td><td>The warning appears even when every prerequisite is "
                "met. Chinese guide 177xz makes this point explicitly - do not restart a good save because of the prompt.</td></tr>"
                "</tbody></table>"
                "<p>One more, less obvious: the pillar inside the Four Guardians' Mirror realm sits where you cannot teleport out with "
                "bells. Polygon advises clearing it before advancing, because the alternative is a long walk back.</p>"
            ),
        },
        {
            "id": "sources",
            "title": "Where This Comes From",
            "content": (
                "<p>Ending names and counts: IGN's <em>All Endings and Requirements</em>, cross-checked against Polygon's true-ending "
                "guide, GamingBolt's prerequisites guide and VGTimes. The 66 Days save-deletion behaviour is described the same way "
                "by IGN and VGTimes. Chinese-language confirmation of the secret ending's name, 饮恨江湖, comes from the same "
                "guides and matches the pre-launch material this site already published.</p>"
                "<p>Not confirmed: whether Long Roar and Final Battle share a cutscene, how many variants exist within each ending, "
                "and whether any ending is difficulty-gated. Nothing found suggests difficulty affects the ending.</p>"
            ),
        },
    ],
}
write("endings", endings)

# ------------------------------------------------------------ true-ending
true_ending = {
    "title": "Phantom Blade Zero True Ending Guide - Every Requirement in Order",
    "description": "The complete checklist for Phantom Blade Zero's true ending, Final Battle: every purple Tale, both Crystal Puppet Eyes, all four Acolyte masks, all five Long Pillars, and the order that stops the point of no return from eating your run.",
    "keyword": "phantom blade zero true ending, phantom blade zero final battle, phantom blade zero perfect ending, phantom blade zero true ending requirements, phantom blade zero bloodline awakening",
    "facts": [
        {"label": "True ending name", "value": "Final Battle - also called the Perfect Ending"},
        {"label": "Reward", "value": "With Heart and Blood (Gold trophy / achievement)"},
        {"label": "Point of no return", "value": "Leaving the Mirage Estate in Pangzhen for the climb up Mount Soulrend"},
        {"label": "Purple Tales required", "value": "9 named Tales, plus Quick Hand Zhang's five fetch requests"},
        {"label": "Masks required", "value": "4 - Blazing (Yanru), Thunder (Lei Ting), Venom (Guhe), Frost (Hansui)"},
        {"label": "Pillars required", "value": "5 - Weeping Creek Valley, Crimson Forest / Mirrorwood, Meigu Lake midlake, Four Guardians' Mirror, Mirage Estate"},
        {"label": "Key items", "value": "Both Crystal Puppet Eyes, the Puppet's Tongue, a restored Illusory Pipa"},
        {"label": "Second playthrough", "value": "Not needed - everything fits in one run, but several steps are missable"},
    ],
    "sections": [
        {
            "id": "overview",
            "title": "How the True Ending Actually Triggers",
            "content": (
                "<p>There is no dialogue choice and no hidden morality counter. Beat the regular final boss with the checklist "
                "complete and a second fight appears immediately afterwards. Win it and the credits play over the true ending, "
                "awarding <strong>With Heart and Blood</strong>. If the second fight does not appear, one requirement is missing - "
                "the game will not tell you which.</p>"
                "<p>That silence is the whole difficulty of this. The checklist spans nine Tales, four boss-gated masks, five pillar "
                "trials and two Crystal Puppet Eyes, and any one of them failing quietly reduces you to the Long Roar or "
                "Annihilation ending. The order below exists to make the failures impossible rather than to make the run fast.</p>"
            ),
        },
        {
            "id": "deadline",
            "title": "The Deadline: Clear Pangzhen Before You Climb",
            "content": (
                "<p>Every source agrees on the cutoff. Polygon: finish the required Tales before reaching the peak of Mount Soulrend. "
                "IGN: complete them before going through the Mirage Estate area in Pangzhen. GamingBolt: the game warns you as you "
                "approach the point of no return, and once past it the side content locks into whatever state you left it in.</p>"
                "<p>Everything up to and including the Mirage Estate is therefore your window. In practice that means doing purple "
                "Tales when they appear rather than banking them - VGTimes' advice, and the one that prevents most failed runs.</p>"
            ),
        },
        {
            "id": "tales",
            "title": "The Purple Tales You Need",
            "content": (
                "<p>IGN lists nine Tales as required, all before the Mirage Estate: <em>Whence the Weeping</em>, "
                "<em>Deep in the Valley</em>, <em>Pillars of Kunlun</em>, <em>Crimson Manor</em>, <em>Illusion of Inanis</em>, "
                "<em>Sha-Chi Powered Boat</em>, <em>Allure of Vanity</em>, <em>Illusory Pipa</em>, and <em>The Herald's Illusion</em>.</p>"
                "<p>Polygon and GamingBolt name three requirements instead of nine - <em>Secrets at the Heart of the Lake</em>, "
                "<em>Bloodline Awakening</em>, and all of Quick Hand Zhang's requests - and treat the rest as enabling steps. "
                "The two lists are not contradictory so much as different resolutions of the same chain: the nine Tales are what "
                "actually unlock the routes, the three are what the game tracks as completion. Treat the nine as the safe answer.</p>"
                "<p><strong>Quick Hand Zhang's fetch requests</strong> run across five encounters. Miss one and the chain breaks. "
                "Deliver each relic the moment he appears rather than carrying it.</p>"
            ),
        },
        {
            "id": "masks",
            "title": "Step 1: Four Acolyte Masks",
            "content": (
                "<p>Four optional bosses, each summoned by interacting with a scarecrow, each dropping an elemental mask. "
                "The scarecrows are spread across four regions and two of them sit behind story gates.</p>"
                "<table><thead><tr><th>Acolyte</th><th>Region</th><th>Scarecrow location</th><th>Mask</th></tr></thead><tbody>"
                "<tr><td>Yanru</td><td>Village of Lu</td><td>North of the Terrace bell, right side, in the rice field</td><td>Blazing Mask</td></tr>"
                "<tr><td>Lei Ting</td><td>Pangzhen</td><td>Use the Flaming Mane to open the way to Pangzhen Slums; from Old Man Gen's House bell "
                "follow the road down toward the lake, scarecrow mid-path</td><td>Thunder Mask</td></tr>"
                "<tr><td>Guhe</td><td>Meigu Lake</td><td>Meigu Village East Dock</td><td>Venom Mask</td></tr>"
                "<tr><td>Hansui</td><td>Crimson Manor</td><td>Inside the manor grounds - save this one for last</td><td>Frost Mask</td></tr>"
                "</tbody></table>"
                "<p>Directions for Yanru, Lei Ting and Guhe are Polygon's. Hansui's region is GamingBolt's, and VGTimes' advice - "
                "leave Crimson Manor until last - is the practical one: by then your build can absorb the fight.</p>"
                "<p>Carry resistance accessories before these fights. Every guide that mentions them says the same thing: they turn "
                "four awkward boss fights into four normal ones.</p>"
            ),
        },
        {
            "id": "mirror",
            "title": "Step 2: The Four Guardians' Mirror",
            "content": (
                "<p>With all four masks, take the boat from Meigu Lake to the western edge of the region, walk on until you find the "
                "mirror, and pass through it. The masks are the key. Inside is a realm holding one of the five Lóng Pillars - "
                "and one Crystal Puppet Eye if you are following the route in order (see the next step; sources differ on which "
                "eye comes from where, and the page handles that).</p>"
                "<p>Clear the pillar <em>before</em> leaving. Bells do not work inside the Phantom Illusionist Ruins, so the realm is "
                "a one-way walk if you skip it. Polygon flags this specifically because it is the step people defer and then lose.</p>"
            ),
        },
        {
            "id": "eyes",
            "title": "Step 3: Both Crystal Puppet Eyes",
            "content": (
                "<p>Two eyes, two locations, and the sources disagree on the mapping. What everyone agrees on is that both are needed "
                "and both go into <strong>Puppet No. 99</strong>.</p>"
                "<ul>"
                "<li><strong>Mountain of Imprisonment</strong> - the Yin eye. The region is optional for the story, which is exactly "
                "why it gets skipped. VGTimes calls ignoring it one of the standard ways to lose the true ending.</li>"
                "<li><strong>Crimson Manor secret boss</strong> - the Yang eye, per VGTimes, which describes taking it from the Manor "
                "and then sailing to the mirror. Polygon's sequence has both eyes coming from the Manor and the Mountain of "
                "Imprisonment without assigning them by name.</li>"
                "</ul>"
                "<p>The discrepancy is minor and does not change the route: clear both the Mountain of Imprisonment and the Crimson "
                "Manor before the point of no return and you have both eyes regardless of which is which.</p>"
            ),
        },
        {
            "id": "pipa",
            "title": "Step 4: The Illusory Pipa and the Three Doors",
            "content": (
                "<p>The <em>Illusory Pipa</em> Tale hands you the pipa itself; restore it, and it becomes the tool that opens the way "
                "through the <em>Herald's Illusion</em>. The same Tale chain is what lets you use the three doors there.</p>"
                "<p>Two more gates run off the same hub: the <strong>Puppet's Tongue</strong> opens the Crimson Manor, and "
                "<strong>Puppet No. 99</strong> takes both eyes. If the Manor will not open, the Tongue is the item you are missing, "
                "not a bug.</p>"
            ),
        },
        {
            "id": "pillars",
            "title": "Step 5: All Five Lóng Pillars",
            "content": (
                "<p>Five pillars, five duels against the Gold-Masked One, and losing any of them means the pillar survives. "
                "Polygon lists each pillar with its nearest bell:</p>"
                "<table><thead><tr><th>Region</th><th>Nearest bell</th></tr></thead><tbody>"
                "<tr><td>Weeping Creek Valley</td><td>Weeping Creek Lóng Pillar</td></tr>"
                "<tr><td>Crimson Forest</td><td>Mirrorwood Lóng Pillar</td></tr>"
                "<tr><td>Meigu Lake</td><td>Midlake Lóng Pillar Dock</td></tr>"
                "<tr><td>Phantom Illusionist Ruins</td><td>Four Guardians' Mirror (no bell teleport inside)</td></tr>"
                "<tr><td>Pangzhen / Mirage Estate</td><td>Mirage Estate Lóng Pillar</td></tr>"
                "</tbody></table>"
                "<p>The Mirage Estate pillar is the last one you can reach, so it is also the natural last check before you commit. "
                "The Gold-Masked One is the same opponent each time with a bigger toolkit - unblockable throws, sword slashes, "
                "kicks - and the answer to the throws is to dodge, not to hold guard.</p>"
            ),
        },
        {
            "id": "final-chain",
            "title": "Step 6: The Endgame Boss Chain",
            "content": (
                "<p>With the checklist complete, ring the bell and work up Mount Soulrend. IGN names the closing sequence: "
                "<strong>Leng Tu</strong>, <strong>Herald of the Veil</strong>, <strong>Meng Hua, the Merciful Lady of the Blossom "
                "Veil</strong>, then <strong>Zuo Shang, The True Long</strong>, then the extra <strong>Final Battle</strong>.</p>"
                "<p>Meng Hua is the checkpoint that matters. Beat her with the requirements met and the hidden fight starts; beat her "
                "without them and you get the ordinary ending. Zuo Shang - the one-handed Aureate blade is his drop - is the hardest "
                "fight in the chain before the true final boss, and the guides that cover him agree on the shape: wear his Sha-Chi "
                "down defensively, do not try to out-trade him, and burst only after a guard break or a freeze.</p>"
            ),
        },
        {
            "id": "checklist",
            "title": "Printable Checklist",
            "content": (
                "<ol>"
                "<li>Do every purple Tale as it appears - do not bank them</li>"
                "<li>Deliver each of Quick Hand Zhang's relics in all five encounters</li>"
                "<li>Beat all four Acolytes at their scarecrows (Yanru, Lei Ting, Guhe, Hansui)</li>"
                "<li>Take the four masks through the Meigu Lake mirror</li>"
                "<li>Clear the Lóng Pillar inside the Four Guardians' Mirror realm before leaving</li>"
                "<li>Clear the Mountain of Imprisonment and the Crimson Manor for both Crystal Puppet Eyes</li>"
                "<li>Restore the Illusory Pipa; open the Crimson Manor with the Puppet's Tongue</li>"
                "<li>Insert both eyes into Puppet No. 99</li>"
                "<li>Destroy all five Lóng Pillars, winning all five duels</li>"
                "<li>Clear the Mirage Estate - the last pillar here is the final check</li>"
                "<li>Climb Mount Soulrend and beat Meng Hua, then the hidden boss</li>"
                "</ol>"
                "<p>Keep a manual save before the Mirage Estate. The game does not offer a warning that distinguishes 'requirements "
                "met' from 'requirements failed', and a save from before the cutoff is the only way to recover from a silent miss.</p>"
            ),
        },
        {
            "id": "sources",
            "title": "Sources and Conflicts",
            "content": (
                "<p>Primary: Polygon's true-ending requirement guide and IGN's <em>All Endings and Requirements</em>, supplemented by "
                "GamingBolt (prerequisite list, mask names) and VGTimes (practical ordering, the Yin eye in the Mountain of "
                "Imprisonment, the endgame warning). Quest and item names are quoted as those guides print them in English.</p>"
                "<p>Conflicts left standing rather than resolved: the number of required Tales (nine vs three named completions), "
                "and which eye comes from which location. Both are recorded above instead of being smoothed over, because a reader "
                "who follows either version across the whole checklist still ends up with both eyes and all the Tales.</p>"
            ),
        },
    ],
}
write("true-ending", true_ending)
