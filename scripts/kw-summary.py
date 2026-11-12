#!/usr/bin/env python3
"""Merge the per-site keyword CSVs into one Chinese-language research report."""
import csv
import os
from collections import defaultdict

SITES = [
    ("pbz", "pbzero.wiki", "Phantom Blade Zero", "reports/pbz-brand-raw.csv"),
    ("e33", "expedition33.wiki", "Clair Obscur: Expedition 33", "reports/e33-brand-raw.csv"),
    ("morse", "morsecodenow.com", "Morse code", "reports/morse-brand-raw.csv"),
]

INTENT_CN = {3: "高（wiki 能赢）", 2: "中", 1: "低（IGN/Steam 把持）"}
CLUSTER_CN = {
    "weapons": "武器/装备", "bosses": "Boss", "endings": "结局", "locations": "地点/地图",
    "progression": "二周目/难度/流程", "collect": "收集/成就", "platform": "平台/价格",
    "release": "发售/版本", "mechanic": "机制", "help": "报错/优化", "review": "评测/口碑",
    "other": "其他",
    "chart": "编码表/图表", "letter": "单字符编码", "learn": "学习教程",
    "audio": "音频/声音", "equipment": "电键设备", "decode": "解码/转换工具",
    "in-games": "游戏彩蛋", "history": "历史", "exam": "考试/执照",
}


def load(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    out = []
    w = out.append
    w("# SEO 关键词调研 — 三站合并报告\n")
    w("调研日期 2026-11-10 ｜ 数据来源：Google / Bing / DuckDuckGo / YouTube 自动补全接口（实时抓取）\n")
    w("## 这份数据从哪来，为什么可信\n")
    w("没有用 GSC。GSC 只告诉你「你已经拿到曝光」的词，回答不了「市场上还有什么词在被搜」。")
    w("这里是从四个搜索引擎的**自动补全接口**直接捞真实用户输入：\n")
    w("- Google（`client=chrome`，会返回 `google:suggestrelevance` 热度分，且一次给 15 条）")
    w("- Google（`client=firefox`，与上面互补）")
    w("- Google YouTube 层（`ds=yt`，反映视频意图）")
    w("- Bing OpenSearch 建议、DuckDuckGo 自动补全\n")
    w("补全词是搜索引擎按**真实查询频次排序**返回的，不是模型生成的。用品牌词 + 26 个字母后缀 + ")
    w("45 个意图后缀 + 8 个疑问前缀去撒网，同一个词被越多引擎、越多种前缀独立命中，")
    w("说明它越接近用户真实输入。这就是没有付费词库时最可靠的需求信号。\n")
    w("**Score** = (12 × 命中引擎数 + 1.8 × 被建议次数 + 前三名加成) × 意图价值权重。")
    w("意图权重 0.55 / 1.0 / 1.15 对应低 / 中 / 高：`metacritic` 这种热词在 wiki 站抢不到，")
    w("不该压过 `boss 顺序` 这种冷但能赢的词。\n")
    w("---\n")

    # ---------- overview
    w("## 一、三站需求体量\n")
    w("| 站 | 抓到词 | 已有页覆盖 | 覆盖率 | 需新建 | 可改造 |")
    w("|---|---|---|---|---|---|")
    store = {}
    for key, host, name, path in SITES:
        rows = load(path)
        if not rows:
            continue
        store[key] = rows
        cov = sum(1 for r in rows if r["has_page"] == "1")
        gaps = [r for r in rows if r["has_page"] == "0" and r["intent"] == "3"
                and int(r["n_engines"]) >= 2]
        near = sum(1 for r in gaps if r.get("near_page"))
        w(f"| {host} | {len(rows)} | {cov} | {cov * 100 // len(rows)}% | "
          f"**{len(gaps) - near}** | {near} |")
    w("")
    w("词量本身是市场规模的代理：Expedition 33 一个品牌词能扩出近 3000 个真实查询，")
    w("Phantom Blade Zero 约 1000，Morse code 1300。这直接决定投入优先级。\n")

    for key, host, name, path in SITES:
        rows = store.get(key)
        if not rows:
            continue
        w("---\n")
        w(f"## {host} — {name}\n")

        by_intent = defaultdict(int)
        for r in rows:
            by_intent[int(r["intent"])] += 1
        w("意图结构：" + " ｜ ".join(
            f"{INTENT_CN[i]} {by_intent[i]} 个" for i in (3, 2, 1) if by_intent[i]) + "\n")

        # high-value gaps
        gaps = [r for r in rows if r["has_page"] == "0" and r["intent"] == "3"
                and int(r["n_engines"]) >= 2]
        gaps.sort(key=lambda r: -float(r["score"]))
        n_new = sum(1 for r in gaps if not r.get("near_page"))
        w(f"### 高价值缺口（{len(gaps)} 个：{n_new} 个要新建，"
          f"{len(gaps) - n_new} 个可改造现有页）\n")
        w("「相近页」有值 = 站内已有覆盖部分意图的页，扩写比重建便宜得多。\n")
        w("| # | 查询词 | 分 | 引擎 | 簇 | 词数 | 相近页 |")
        w("|---|---|---|---|---|---|---|")
        for i, r in enumerate(gaps[:25], 1):
            near = r.get("near_page") or "—"
            w(f"| {i} | {r['word']} | {r['score']} | {r['n_engines']} | "
              f"{CLUSTER_CN.get(r['cluster'], r['cluster'])} | {r['n_words']} | {near} |")
        w("")

        # long tail
        long_tail = sorted([r for r in rows if int(r["n_words"]) >= 5 and r["intent"] == "3"],
                           key=lambda r: -float(r["score"]))
        w(f"### 长尾词（5 词以上，{len(long_tail)} 个，取前 20）\n")
        if long_tail:
            w("这些是典型的长尾：搜索量低但意图极准，竞争小，一个页面对一个词就能吃住。\n")
            for r in long_tail[:20]:
                flag = "" if r["has_page"] == "1" else " ← **无页**"
                w(f"- {r['word']}（{r['n_engines']} 引擎，{CLUSTER_CN.get(r['cluster'], r['cluster'])}）{flag}")
        else:
            w("（本次未抓到 5 词以上的高价值长尾）")
        w("")

        # cluster profile
        cl = defaultdict(list)
        for r in rows:
            cl[r["cluster"]].append(r)
        w("### 需求结构（按簇）\n")
        w("| 簇 | 词数 | 无页 | 代表词 |")
        w("|---|---|---|---|")
        for c, items in sorted(cl.items(), key=lambda kv: -len(kv[1]))[:8]:
            nogap = sum(1 for r in items if r["has_page"] == "0")
            sample = ", ".join(r["core_query"] or "(品牌词)" for r in items[:4])
            w(f"| {CLUSTER_CN.get(c, c)} | {len(items)} | {nogap} | {sample} |")
        w("")

    # ---------- cross-site conclusion
    w("---\n")
    w("## 二、跨站结论\n")
    w("**1. 三个站最大的缺口都是「工具页 / 排序页」，不是文章页。**\n")
    w("pbzero 缺 `weapon tier list`、`map`、`bosses ranked`；e33 缺 `builds act 1/2/3`、")
    w("`new game plus`、`bosses ranked`；morse 缺 `decoder`、`converter`、`bug key`。")
    w("这类页面的共同点是**结构化 + 可查询**，一旦排上去很难被替代，而且不吃更新频率。\n")
    w("**2. 现有页铺的是「一个实体一页」，绕开了最值钱的聚合需求。**")
    w("e33 有 460 页、62% 的词已被覆盖，但仍有 38 个要新建、32 个要改造的高价值缺口。")
    w("原因是页面按 Boss / 武器逐个铺，而用户搜的是「全部 Boss 的顺序」「分章节的 build」")
    w("「二周目有什么不同」—— 差的是**聚合页和切片页**，不是实体页。")
    w("pbzero 更极端：1005 个词只覆盖 28%，但全新缺口只剩 5 个 —— 不是没做，")
    w("是它的品牌词盘子本身就小（约为 e33 的三分之一），可扩的增量天花板低。\n")
    w("**3. morse 站的需求结构和游戏站完全不同，不能共用一套内容模板。**")
    w("它的头部需求是**工具**（decoder / converter / translator）、**音频**（sound / beep）、")
    w("**实体设备**（bug key / key types），24 个全新缺口里一半是这类。")
    w("这个站的转化路径天然更短，做工具页比做文章页回报高得多。\n")
    w("**4. 同一个词在三个站价值完全不同，必须看语境定价。**")
    w("`phantom blade zero key` 是 CD key（商业意图，wiki 抢不到，判为低价值）；")
    w("`backstreet courtyard key` 是游戏内钥匙（信息意图，必须做）。")
    w("而 morse 站的 `key` 是电键，是核心内容，判为最高价值。规则按站分开，就是为了这个。\n")

    w("## 三、建议动作\n")
    w("**优先级按「需求确定性 × 能赢的概率 × 复用现有资产」排，不是按分数排。**\n")
    w("1. **pbzero**：只做 5 个全新缺口里最值钱的 —— `weapon tier list`（可复用现有 42 个武器页数据，")
    w("且站内已有 best-build 可改造）、`map`、`backstreet courtyard key`。")
    w("其余 9 个（`bosses ranked`、`final boss`、`secret ending`）都是改造现有页，成本低，顺手做。")
    w("2. **e33**：`bosses ranked` / `bosses in order` 是 4 引擎一致命中且已有 `boss-order` 可改造，")
    w("最省力；`new game plus` 有 3 个变体词（rewards / differences / builds）但站内零覆盖，")
    w("值得做一个完整板块；`builds act 1/2/3` 是分章节切片，直接切现有 build 页。")
    w("3. **morse**：`decoder` / `converter` 是工具型入口，一个页面覆盖一整族查询，")
    w("应优先于任何文章；其次 `bug key` / `key types` 这组设备词，4 引擎一致命中但站内完全空白。")
    w("4. 三站都建议用**聚合页**把现有实体页串起来。这既补内容缺口，也顺带解决内链和收录问题。\n")

    w("## 附：原始数据\n")
    for key, host, name, path in SITES:
        w(f"- `{path}` — 全量词表（word / core_query / score / intent / n_engines / cluster / has_page）")
    w("")
    w("需要重新跑：")
    w("```bash")
    w('python3 scripts/keyword-research.py --seeds "phantom blade zero" \\')
    w('  --brand "phantom blade zero" --site-root . --depth 4 --out-prefix reports/pbz-brand')
    w("```")
    w("`--depth 1` 只查种子词，`2` 加字母扩展，`3` 加 45 个意图后缀，`4` 再加疑问前缀。")
    w("换站改 `--site-root` 和 `--brand`；morse 这类通用词站要加 `--allow-off-brand --profile morse`。")

    path = "reports/seo-keyword-research-2026-11-10.md"
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
