#!/usr/bin/env python3
"""给 /walkthrough 补一节「逐章指引」。

为什么：Bing 侧 "phantom blade zero walkthrough" 是 1,600/月 的最大词，
但 /walkthrough 正文里 walkthrough 只出现 4 次、825 词，撑不住这个词的意图。
补的方式不是堆词，是把「这一章怎么推进、先打谁、什么会漏」写出来。

boss 顺序全部由 src/data/entities/bosses.json 现算，不写死；叙述部分是手写。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOSSES = ROOT / "src" / "data" / "entities" / "bosses.json"
PAGE = ROOT / "src" / "data" / "pages" / "walkthrough.json"

LINK = 'style="color:var(--accent);text-decoration:underline;text-underline-offset:2px"'

# 每章的手写叙述。boss 名不写死，靠 bosses.json 拼。
CHAPTERS = {
    "Prologue & Weeping Creek Valley": {
        "lead": "The walkthrough opens the way the game does: a scripted duel you cannot lose, then a pursuit on the "
                "main road. Zuo Shang's opening fight is a tutorial, so use it to learn what a red flash reads like "
                "rather than to win fast. The Hunt is not killed here, it comes back later. The valley ends at the "
                "Axemaster's Fall, where Peng Meng hands you the Dread Axe, your first Phantom Edge.",
        "detour": "Hua, Deadly Betrothed sits in the Flesh Lily Fields and is the most valuable detour in the region. "
                  "Her Scarlet Wraithblade is scaled for this point; come back at chapter four and the fight is worse "
                  "for the same reward.",
    },
    "Crimson Manor & Crimson Forest": {
        "lead": "Crimson Manor is optional content wrapped around a required trip, which is why people clear it by "
                "accident. The forest proper is where the game teaches its elemental vocabulary: Hua Qianxiao's "
                "drinking shield at the Pangzhen Bridge Overlook, then Jing Ye's horse and blood-draining sword. "
                "Bai Chilian closes the chapter at the Threadbound Great Tree, after the mirror sequence.",
        "detour": "Acolyte Hansui is reached through a scarecrow and is the easiest fight in the region to walk past. "
                  "The Gold-Masked One carries over from the valley and keeps returning through the Lóng Pillar "
                  "trials, so treat each sighting as homework rather than a wall.",
    },
    "Village of Lu": {
        "lead": "The densest optional region and the one most often finished too fast. Zhuo Bi guards the approach; "
                "the Bi brothers split between the Puppet Testing Grounds route and the village itself. Yuzan needs a "
                "drop into the puppet well after Bi Hai, which is the single most missed step in this chapter. "
                "Mu Xiaokui closes it with Yu Yao and Tie present.",
        "detour": "Dusk, the Puppeteer is gated behind Memory Flowers and will not appear until they are collected. "
                  "Acolyte Yanru hides behind a terrace bell on the north side of the rice fields.",
    },
    "Pangzhen": {
        "lead": "The largest region and the widest missable window, which is a bad combination. The story line runs "
                "from the South Gate bridge through the Statue Grounds, the Back Street Archway, the Singing Pond and "
                "up from the Three Ships Well before Chang Hong and Flame close it. Flame is the only story boss in "
                "the game who gates an optional fight: the Flaming Mane he drops opens the way into Pangzhen Slums.",
        "detour": "Acolyte Lei Ting is behind that gate, so skipping Flame's drop costs you a fight permanently. "
                  "You Loong runs through the Green Serpent House and then the water, and is easy to start without "
                  "finishing in the same visit.",
    },
    "Mandate Encampment": {
        "lead": "A shorter chapter that hides one of the game's few formation fights: the Chief Disciple of the "
                "Seven-Stars Formation only becomes available once the surrounding disciples are cleared. Push the "
                "encampment itself first, then clear outward.",
        "detour": "Wu Lengshuang sits off the Path of the Baishan's Fall, away from the main route. Yubi is in the "
                  "Training Grounds past the main gate.",
    },
    "Meigu Lake": {
        "lead": "Only one story boss, which makes Meigu Lake the region people rush and then regret. Grief-Stricken "
                "Jin is the spine of it; everything else here is optional, including the fight that decides whether "
                "the true ending is even open to you.",
        "detour": "Blizzard Blademaster at the Whiteshadow's Fall bell is the true-ending gate. If you leave the lake "
                  "without clearing it, the ending branch closes and the walkthrough's last chapter changes shape.",
    },
    "Mountain of Imprisonment": {
        "lead": "A straight climb with a hard right turn at the end. Iron Butcher, Bi Feng at the Commander's "
                "Platform, then Kui Yanyan hold the ascent; Yu Ding sits in the Mirage Estate training grounds and "
                "belongs to this stretch rather than the next chapter, despite the location name.",
        "detour": "Jade-Face is inside the Lady's Shrine temple ruins, and Huangxing, the Kunlun Renegade is at the "
                  "very end of the region, past the point where most players turn back.",
    },
    "Mirage Estate": {
        "lead": "The shortest chapter in the walkthrough: Lei Dang and Qiu Feng, back to back, with no travel between "
                "them worth mentioning. It exists to set up the climb.",
        "detour": "Mo Yuan is the only optional fight here, and the chapter is short enough that there is no reason "
                  "to skip it.",
    },
    "Mount Soulrend & endgame": {
        "lead": "The point of no return. Leng Tu and Herald of the Veil hold the ascent, Meng Hua sits at the peak "
                "and only exists on the true-ending branch, and Zuo Shang returns as The True Long for the final "
                "fight. The Last Battle triggers immediately after him, so there is no trip back to a bell once the "
                "climb starts.",
        "detour": "The Saw and the Crusher is the only optional fight left in the endgame. Clear it before the final "
                  "climb, not after, because after is not an option.",
    },
}


def boss_link(b):
    return f'<a href="/{b["slug"]}" {LINK}>{b["name"]}</a>'


def build_section():
    bosses = json.loads(BOSSES.read_text())
    by_act = {}
    for b in bosses:
        by_act.setdefault(b["act"], []).append(b)

    parts = [
        "<p>This is the walkthrough in the order you actually play it: nine chapters, 60 encounters, and the three "
        "places where leaving early costs you content permanently. Each chapter below gives the story bosses in "
        "sequence, the optional fights in it, and what closes it. Fight-by-fight detail lives on the individual "
        f'boss pages and on <a href="/boss-order" {LINK}>boss order</a>; the purpose of this walkthrough is to stop '
        "you from walking past something.</p>",
    ]

    n = 0
    for act, ch in CHAPTERS.items():
        items = by_act.get(act, [])
        if not items:
            continue
        n += 1
        story = [b for b in items if b["kind"].startswith("Story") or b["kind"] in ("True ending only",)]
        optional = [b for b in items if b not in story]

        sequence = " &rarr; ".join(boss_link(b) for b in story)
        parts.append(f"<h3>Chapter {n}: {act}</h3>")
        parts.append(f"<p>{ch['lead']}</p>")
        parts.append(f"<p><strong>Story bosses, in order:</strong> {sequence}.</p>")
        if optional:
            names = ", ".join(boss_link(b) for b in optional)
            verb = "is" if len(optional) == 1 else "are"
            noun = "encounter" if len(optional) == 1 else "encounters"
            parts.append(
                f"<p><strong>Optional in this chapter:</strong> {names} "
                f"({len(optional)} of the {len(items)} {noun} here {verb} optional).</p>"
            )
        parts.append(f"<p><strong>Do not leave without:</strong> {ch['detour']}</p>")

    parts.append(
        "<p>One structural note that applies to the whole walkthrough: bells are the fast-travel network, and they "
        "do not work inside the Phantom Illusionist Ruins. That is why the Four Guardians' Mirror realm reads as a "
        "one-way trip in the mission table - it is not a bug in the order, it is a region with the exit disabled "
        "until you clear it.</p>"
    )
    return {
        "id": "chapter-by-chapter",
        "title": "Walkthrough, Chapter by Chapter",
        "content": "".join(parts),
    }


def main():
    page = json.loads(PAGE.read_text())
    sections = [s for s in page["sections"] if s["id"] != "chapter-by-chapter"]
    new = build_section()

    # 插在 mission-order 之后、region-notes 之前：先给顺序表，再逐章展开
    idx = next((i for i, s in enumerate(sections) if s["id"] == "mission-order"), 0) + 1
    sections.insert(idx, new)
    page["sections"] = sections
    PAGE.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n")

    words = len(new["content"].split())
    total = sum(len(s["content"].split()) for s in sections)
    print(f"新增 [{new['id']}] {words} 词，全文现 {total} 词，共 {len(sections)} 节")


if __name__ == "__main__":
    main()
