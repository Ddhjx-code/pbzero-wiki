# pbzero.wiki 信息架构（依灰机 wiki 模型）

> 依据 `keyword-validator-mcp/信息站建设经验总结.md`（实测拆解灰机 ff14 分站：
> 13,246 篇 / 2,311,262 次编辑）。
> **本文档定顺序**：先统一骨架 → 再建分类索引 → 再补消歧义 → 最后批量铺实体。
> 顺序错了要返工。

---

## 一、三级层级（本站现状与目标）

```
第1级  总览 Hub        「我该去哪」
第2级  分类索引        「这一类的全貌」        ← 本站当前完全缺失
第3级  实体            「就是这个」
```

| 主题 | 第1级 Hub | 第2级分类索引 | 第3级实体 |
|---|---|---|---|
| Boss | `/boss-guide` | `/bosses-by-class`、`/boss-drops` | `/{name}-boss` ✅ 7 页 |
| 武器 | `/weapons` | `/blades`、`/phantom-edges` | `/{weapon}` |
| 角色 | `/characters` | `/playable-characters`、`/npcs` | `/{name}` |
| 任务 | `/quests` | `/side-quests`、`/story-paths` | `/{quest}` |
| 奖杯 | `/trophies` | `/trophy-roadmap`、`/missable-trophies` | `/{trophy}` |
| 机制 | `/combat` | — | `/sha-chi`、`/phantom-edge`（概念页） |

**每级必须上下互通**：实体页尾→同级导航盒；实体页首→面包屑回索引；索引页→链到每个实体。

第2级为什么不能省：长尾词绝大多数是「实体名 + 属性」（`thunder eveque location` 那种），
一个实体页靠信息卡就能吃下多个；但 `all bosses` / `boss list` / `weapon types` 这类
**列表型长尾**只有独立索引页能接。

---

## 二、L2 骨架：每种实体的固定章节序列

**核心要求：同一类型的页面，section id 序列必须完全一致。** 这是能规模化的唯一前提 ——
没有它，"加一个实体"就永远是"手写一篇文章"。

生成器 `scripts/gen-entity-pages.py` 按类型输出下列序列，**不要手改单页去偏离它**。

### boss
```
overview → how-to-find → weakness → rewards → strategy → status
```
（对应灰机「实体/Boss」标准骨架：概述 → 位置 → 弱点抗性 → 掉落 → 打法 → 同类导航）

### weapon
```
overview → classification → stats → combo → acquisition → status
```
（对应「物品/装备」：属性 → 获取方式 → 用途 → 同类导航）

### character
```
overview → background → playable → relationships → appearances → status
```
（对应「人物」：简介 → 背景故事 → 关系网 → 出场 → 同类导航）

### quest
```
overview → walkthrough → requirements → rewards → branching → status
```

### trophy
```
overview → how → details → status
```

### 机制页（手写，但同型也要一致）
```
overview → calculation → examples → misconceptions → status
```
（对应「机制」：是什么 → 怎么算 → 实例 → 常见误区 → 同类导航）

`status` 一节固定承担两件事：说明本页信息的来源边界，以及链回第1/第2级。

---

## 三、L3 数据层

```
src/data/entities/{bosses,weapons,characters,quests,trophies}.json
        ↓ scripts/gen-entity-pages.py <file> --type <t>
src/data/pages/*.json
        ↓ scripts/wire-entities.py <file> <主题名> --pages <候选宿主>
内链 + 导航盒注册
```

**字段规则（不可违反）**

1. 除 `slug` / `name` / `summary` 外全部可选。
2. 未提供的字段渲染为 `Not confirmed post-launch`，或整节省略。
3. **生成器里不允许存在任何默认物品名、默认弱点、默认奖励。**
   移植自 e33 的第一版曾把《光与影》的 `Colour of Lumina`、`Chroma Catalyst`
   写进本作奖励区 —— 那就是默认值造成的编造。
4. `weak` 用哨兵值 `"__not_confirmed__"` 表示"未知"，与 `"None"`（确认无弱点）严格区分。
5. `playable` 是**三态**：`true` / `false` / 缺省=未知。发售前有整批站点把 S-Game
   手游的可玩角色表（含 The Chord）错安到本作，而本作是单人、只有 Soul 可操控。

---

## 四、L4 信息卡字段规范

卡片放在正文之前，让用户扫一眼就有八成答案。字段顺序跨页统一，且**字段值要能带内链**。

| 类型 | 卡片字段（按顺序） |
|---|---|
| boss | Location → Appears in → Recommended level → **Weak to** → Resists → Absorbs → First shown → Drops |
| weapon | Slot → Class → Damage → Scaling → Special property → How to obtain → First shown |
| character | **Playable** → Role → Affiliation → Portrayed by → Weapon |
| quest | Given by → Location → How to start → Type → Reward |
| trophy | Rarity → Missable → Hidden |

一个 URL 靠卡片同时命中「实体+location」「实体+weakness」「实体+drops」等多个长尾 ——
前提是正文里真的写了这些词，而不是堆砌。

---

## 五、L5 导航盒：按主题聚类，不做全站轮转

| 主题名 | 收录页面 |
|---|---|
| `Bosses` | `/boss-guide` + 各 `/{name}-boss` |
| `Weapons` | `/weapons`、`/blades`、`/phantom-edges` + 各武器页 |
| `Characters` | `/characters`、`/protagonist` + 各角色页 |
| `Quests` | `/quests` + 各任务页 |
| `Trophies` | `/trophies` + 各奖杯页 |
| `Guides` | `/guide`、`/combat`、`/difficulty-modes`、`/endings`、`/release-date` 等 |

**为什么必须聚类**：轮转只保证"每页有链接"，但同类页面永远聚不到一起，不产生层次。
长尾词单个搜索量极低，靠单词权威度永远排不上；**唯一能排上去的理由是"这个主题你有
系统性覆盖"**，导航盒就是向搜索引擎声明这件事。

---

## 六、L6 索引页自动生成

第2级分类页的表格由 `src/data/entities/*.json` 派生，**绝不手工维护清单** —— 手工清单必然过期。

---

## 七、消歧义（已知的真实需求）

| 词 | 冲突 | 处理 |
|---|---|---|
| **Seven Stars** | 既作为 boss 名出现，也在别处作为**阵型/编成**名出现 | `/seven-stars` 消歧义页，分流到 `/seven-stars-boss` 与后续阵型页 |
| **Soul** | 主角名，同时是系列手游《影之刃》语境里的通用词 | 主角页需明确"本作唯一可玩角色"，并说明手游角色表不适用于本作 |
| **Mó Yuan / Mowan / Mo Yuan** | 同一角色多种罗马拼法 | 页面内统一一种拼写并在正文标注其他写法，暂不做消歧义页 |

---

## 八、发售当天（2026-10-29）的填装顺序

```bash
# 1. 填数据（只填已实测确认的，未知就留空）
vim src/data/entities/bosses.json weapons.json characters.json quests.json trophies.json

# 2. 生成页面
for t in boss weapon character quest trophy; do
  python3 scripts/gen-entity-pages.py src/data/entities/${t}s.json --type $t
done

# 3. 注册内链与导航盒（按类型选主题，见 scripts/wire-entities.py --help）
python3 scripts/wire-entities.py src/data/entities/bosses.json     Bosses     --pages "boss-guide,guide,faq"
python3 scripts/wire-entities.py src/data/entities/weapons.json    Weapons    --pages "weapons,combat,guide"
python3 scripts/wire-entities.py src/data/entities/characters.json Characters --pages "characters,guide,faq"
python3 scripts/wire-entities.py src/data/entities/quests.json     Quests     --pages "quests,guide"
python3 scripts/wire-entities.py src/data/entities/trophies.json   Trophies   --pages "trophies,how-long-to-beat"

# 4. 重建第2级索引页表格 + 搜索索引 → build → 部署（不要 --prebuilt）→ IndexNow
```

---

## 九、自查清单（对应灰机十项落地清单）

| # | 检查项 | 本站现状 |
|---|---|---|
| 1 | 每个专有名词有独立 URL | 部分 —— boss 7 页有；武器/角色/任务/奖杯实体待发售 |
| 2 | 同类型页面章节序列一致 | ✅ boss 7 页 1 种骨架 |
| 3 | 数据与视图分离 | ✅ 实体 = 一条 JSON 记录 |
| 4 | 每个实体有关键信息卡片 | ✅ 卡片在正文前，字段顺序跨页统一 |
| 5 | 页尾有同类导航 | ✅ 导航盒 |
| 6 | 卡片字段值带内链 | ✅ `fact-links` |
| 7 | **三级层级完整** | 部分 —— 第2级已建 `/blades`、`/phantom-edges`、`/npcs`；boss 分类页待发售数据 |
| 8 | 清单页自动生成 | ✅ `scripts/gen-index-pages.py`，幂等，空表显式声明未确认 |
| 9 | 有消歧义页 | ❌ Seven Stars 需要 |
| 10 | 社区入口收敛 | ✅ 只有 contact 一处 |
