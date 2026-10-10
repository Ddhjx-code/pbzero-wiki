# 上线日数据管道（2026-10-29）

本站在发售前只写"已公布"内容。发售当天，boss / 武器 / 角色 / 任务 / 奖杯的真实数据
通过本管道进入站点，**不需要手写页面**。

## 分层

```
src/data/entities/*.json   数据层：一条记录 = 一个实体
        ↓ scripts/gen-entity-pages.py
src/data/pages/*.json      渲染层：生成器产出，不手改
        ↓ scripts/wire-entities.py
内链 + 导航盒注册
```

数据层与渲染层分离是灰机 wiki 的做法。它的意义不是优雅，而是**发售当天加一个 boss 是
加一条记录，而不是复制一个 200 行的页面**。

## 五种类型

```bash
python3 scripts/gen-entity-pages.py src/data/entities/bosses.json --type boss
python3 scripts/gen-entity-pages.py src/data/entities/weapons.json --type weapon
python3 scripts/gen-entity-pages.py src/data/entities/characters.json --type character
python3 scripts/gen-entity-pages.py src/data/entities/quests.json --type quest
python3 scripts/gen-entity-pages.py src/data/entities/trophies.json --type trophy
```

`--type` 取错值会直接报错退出并列出可用类型，不会静默按 boss 处理。

## 字段

所有字段都是可选的（除 `slug` / `name` / `summary`）。**未提供的字段渲染成
"Not confirmed post-launch"，或者整段省略 —— 绝不用默认值填。**

### boss
| 字段 | 含义 |
|---|---|
| `weak` / `resists` / `absorbs` | 元素关系。`weak` 缺省即未知 |
| `location` / `act` / `level` | 位置、章节、推荐等级 |
| `source` | 首次公布来源（demo / 预告片 / State of Play） |
| `drops` | 掉落列表 |
| `observed` | **列表**： footage 里确实出现过的机制 |
| `tips` | **列表**：实测打法 |

`weak` 用哨兵值 `"__not_confirmed__"` 表示"未知"，与"确认无弱点"（`"None"`）严格区分。
这是本管道最重要的一条设计 —— 把未知写成"无弱点"会直接误导配装决策。

### weapon
`slot`（Primary blade / Phantom Edge）、`category`、`damage`、`scaling`、`property`、
`speed`、`range`、`moveset`（列表）、`obtained`、`source`。

### character
`playable`（**三态**：`true` / `false` / 缺省=未知）、`role`、`affiliation`、
`portrayed_by`、`weapon`、`observed`（列表）。

`playable` 必须显式判断。发售前有整批站点把 S-Game 手游里的可玩角色表（含 The Chord）
错安到本作上，而本作是单人、只有 Soul 可操控。生成器对 `playable: false` 会主动写出
这条纠正，对缺省则写"未确认"。

### quest
`giver`、`location`、`trigger`、`kind`（Main / Side）、`reward`（列表或字符串）、
`steps`（列表）。

任务页固定包含一节"是否影响剧情"，只引用官方那句 side quests「might even open up new
story paths」，不对单个任务做断言。

### trophy
`rarity`、`missable`、`hidden`、`glitchable`、`how`、`steps`（列表）。

奖杯列表发售前完全不存在，所以这一族在 10-29 之前保持空文件。

## 生成之后必须做的三步

```bash
python3 scripts/wire-entities.py src/data/entities/bosses.json "Bosses" \
  --pages "boss-guide,combat,guide,faq,release-date"
# 重建搜索索引
python3 - <<'PY'
import json, os
idx = []
for f in sorted(os.listdir("src/data/pages")):
    if not f.endswith(".json"): continue
    d = json.load(open(f"src/data/pages/{f}"))
    facts = {x["label"]: x["value"] for x in d.get("facts", [])}
    kind = facts.get("Type") or facts.get("Kind") or ("Boss" if "Weak to" in facts else "Page")
    idx.append({"s": f[:-5], "t": d["title"].split(" - ")[0], "d": d["description"][:150],
                "k": kind, "x": " ".join(f"{k}: {v}" for k, v in facts.items())[:180]})
json.dump(idx, open("public/search-index.json", "w"), ensure_ascii=False)
print(len(idx))
PY
npm run build && vercel --prod --yes   # 不要加 --prebuilt
```

最后推 IndexNow（key 在 `public/2f630f456deb4989a6cda8422a24aace.txt`）。

## 本管道踩过的坑（都是真实事故）

1. **`--type` 缺省是 boss。** 早期版本没有校验，`--type wepon` 拼错会静默按 boss 生成。
2. **跨站词汇污染。** 从 e33 移植过来的第一版生成器把 `Colour of Lumina`、
   `Chroma Catalyst` 这些**《光与影》道具名**写进了本作奖励区。现在生成器里没有任何
   默认物品名、默认弱点、默认奖励。
3. **skip-if-exists 会覆盖。** 生成器对已存在文件是跳过，但地区页生成器曾把
   `sirene` / `visages` 两个 boss 页覆盖掉（slug 冲突）。批量生成前先查 slug 撞车。
4. **只改 sections 会漏掉 facts。** 修"4 个可玩角色"这个虚构时，我改了 5 个页面的
   sections，但 `how-long-to-beat` 的 **facts 数组**里 `Playable characters = 4` 一直留着。
   信息卡是读者最先看到的地方。任何事实修正都要同时扫 sections 和 facts。
5. **校验不能用裸文本匹配。** 页面 HTML 里 `href=\"...\"` 是转义的、React 会在相邻文本
   节点间插 `<!-- -->`、`&ldquo;` 是实体。一律 `json.load()` 或去标签后再判断。
6. **shell 通配符会吞掉整条命令链。** `rm -f /tmp/x/*.json` 在无匹配时 zsh 直接报错中断
   `&&` 链，导致后面的步骤没执行，而检查又 glob 了空目录 → **假通过**。批量校验请写在
   Python 里。
