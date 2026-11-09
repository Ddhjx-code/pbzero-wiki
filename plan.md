# Phantom Blade Zero Wiki — 建站实施计划

## 项目信息

| 项目 | 值 |
|------|------|
| 域名 | pbzero.wiki |
| 游戏 | Phantom Blade Zero（影之刃零） |
| 发售日 | 2026年10月29日 |
| 技术栈 | Next.js 14 + Tailwind CSS + 静态导出 |
| 部署 | Vercel (https://pbzero-wiki.vercel.app) |
| 特效 | canvas-fx（武侠风粒子/流体/glitch）— 待实现 |
| GA | G-W9Y62B3DBM ✅ 已接入验证通过 |
| GSC | 已提交 sitemap.xml |
| GitHub | https://github.com/Ddhjx-code/pbzero-wiki |

---

## 当前进度（2026-08-19）

### 已完成
- [x] 项目初始化 + 技术搭建
- [x] 暗色武侠主题（黑底 + 深红 + 金色）
- [x] GA4 代码接入（G-W9Y62B3DBM）
- [x] sitemap.xml + robots.txt
- [x] SEO 基础（metadata, canonical, OG, JSON-LD）
- [x] 首页（Hero + Key Art背景 + 快捷入口 + 游戏概览）
- [x] P0 内页：Beginner Guide, Characters, Boss Guide, Weapons
- [x] 占位页：best-build, skill-tree, endings, lore, character-creation, map
- [x] RelatedPages 内链组件（所有页面底部）
- [x] 官网图片素材下载（hero-bg, poster, logo, favicon, swordman, preorder）
- [x] 域名注册 + Cloudflare DNS 配置
- [x] Vercel 部署 + SSL 证书签发
- [x] 域名 alias 绑定（pbzero.wiki → Vercel）

### 发售后的攻略补全（2026-11-09）

发售（10-29）已过 11 天，站点核心页仍是"发售前只写已确认"口径，部分已变成错信息。
本轮按真实数据改写，全部内容来源于公开攻略媒体（IGN / Polygon / Game8 / NoobFeed / 游侠网等），
分歧处保留双方说法并标注来源，不做单方面断言。

- [x] `endings` 重写：真实为 **4 个结局**（旧页写"8 个且均未确认"，已删）。
      Annihilation / Long Roar / Final Battle / Undying Grudge。
- [x] 新增 `/true-ending`：真结局完整清单（9 条紫色支线、4 张侍从面具、5 根龙柱、2 只水晶人偶眼、
      不可回头点、终局 Boss 链、6 个静默翻车点）。
- [x] `boss-list` 重写：11 个 → **56 个**，按 8 大区域分表，标注主线/可选、地点、掉落。
- [x] 新增 `/trophy-guide`：PS5 36 奖杯 / Steam 66 成就、白金路线、6 个易错过 Tale 奖杯。
- [x] 新增 `/walkthrough`：8 区域 22 个主线任务顺序、不可回头点、进终局前检查表。
- [x] `how-long-to-beat` 重写：20–25h 主线 / 30–40h 含支线 / 40–45h 全清 / 50–70h 白金，
      并解释"评测 50h vs 导演 20–30h"的口径差异。
- [x] `weapons` 补入真实获取表：26 把主武器 + 16 个 Phantom Edge + 淬魂树。
- [x] 注册：nav-topics / taxonomy / RelatedPages / 搜索索引（48 → 51 页）。
- [ ] **待办**：`npm run build` 未能在本机执行 —— 三个 wiki 的 node_modules 都是残缺的
      （缺 `.bin`、`next` 包内文件不全），重装被沙箱拦下。需在有网络且可写 node_modules 的环境里
      跑一次 build 确认；内容层已过 JSON/HTML 结构校验与 284 条内链校验。
- [ ] **待办**：`src/data/entities/` 仍是空的（除 bosses-prelaunch）。若要走"数据层 → 生成器"的
      正规管道，需要把本轮 Boss/武器数据回填成实体记录，否则生成的会是大量 `Not confirmed` 空页。

### 待完成
- [ ] canvas-fx 武侠风粒子特效（首页 Hero）
- [ ] P1 页面内容：endings, lore, skill-tree
- [ ] 更多图片素材（角色截图、Boss 截图）
- [ ] GSC 验证所有权
- [ ] Service Account 授权给新 GA4 Property
- [ ] 多语言（法/葡/德）
- [ ] Adsterra 广告接入（流量起来后）

---

## Phase 1: 项目初始化

### Task 0: 技术搭建 ✅
- [x] `npx create-next-app` 初始化项目
- [x] 配置 Tailwind CSS
- [x] 配置 `next.config.mjs`（output: export, images: unoptimized）
- [x] 设置暗色主题（武侠风：黑底 + 深红/金色点缀）
- [x] 配置 GA4 代码（原生 script 注入，G-W9Y62B3DBM）
- [x] 配置 sitemap.xml + robots.txt
- [x] SEO 基础（metadata、canonical、OG tags、JSON-LD）

### Task 1: 首页 ✅
- [x] Hero 区域：游戏 Key Art 背景（canvas-fx 特效待加）
- [x] 游戏概览：发售日、平台、开发商、类型
- [x] 快速入口卡片（Guide / Characters / Boss / Weapons）
- [x] About 区域：战斗系统亮点 + 数据统计（30+ 武器、4 角色、66 天等）
- [ ] Footer：社区链接（Steam/Reddit/Discord/X）

### Task 2: Favicon / 品牌
- [ ] 生成 512x512 源图（武侠风刀刃/影境主题）
- [ ] 转换为全套 favicon 文件
- [ ] site.webmanifest

---

## Phase 2: P0 内页（第一批，立即可做）

### 角色页 `/characters`
- [ ] 4 个可玩角色卡片（Soul / Mu Xiaokui / Zuo Shang / The Chord）
- [ ] 每个角色：名称、别名、关系网、战斗风格描述
- [ ] 已知 NPC 列表（Dinghai / Old Beggar / Tang Li 等）
- [ ] 图片：官方角色截图/预告片截帧

### 新手指南 `/guide`
- [ ] 战斗系统核心机制：Parry、连击、Phantom Edge
- [ ] 武器系统概述：3 类主武器 + 20+ Shachi 副武器
- [ ] 66 天生命系统说明
- [ ] 多结局机制介绍
- [ ] 难度系统（含 Hellwalker）

### Boss 攻略框架 `/boss-guide`
- [ ] 已知 Boss 列表（Puppet Boss / String Puppet / Seven Stars / Lion Dance / Drunken Sword / Huangxing / Double Boss）
- [ ] 每个 Boss 卡片：名称、来源（Demo/预告片）、战斗风格预览
- [ ] "发售后更新"标记

### 武器大全 `/weapons`
- [ ] 3 大类武器分类说明（Regular / Long / Dual Sword）
- [ ] Shachi 副武器系统介绍
- [ ] 双武器装备机制
- [ ] 已知武器展示（预告片中出现的）

---

## Phase 3: P1 内页（1-2 周内补充）

- [ ] `/endings` — 8 结局框架 + 66 天系统与结局关系
- [ ] `/skill-tree` — 技能系统框架（Demo 中可见的部分）
- [ ] `/lore` — 世界观"影境"设定、The Order 组织、武侠朋克背景
- [ ] `/all-bosses` — 完整 Boss 索引（持续更新）
- [ ] `/character-creation` — 角色创建/捏脸系统预览

---

## Phase 4: 发售后立即补充（10/29 之后）

- [ ] `/walkthrough` — 全通关流程攻略
- [ ] `/best-build` — 最佳技能/武器搭配
- [ ] `/best-weapons` — 武器 Tier List
- [ ] `/final-boss` — 最终 Boss 详细攻略
- [ ] `/map` — 区域地图 / 互动地图
- [ ] `/trophy-guide` — 全奖杯/成就攻略

---

## Phase 5: 数据监控与变现

- [ ] 接入 GA4（新 Property）
- [ ] 接入 Google Search Console
- [ ] 每周用 site-validator-mcp 查数据复盘
- [ ] 根据 GSC 搜索词补页面
- [ ] 日访问 >500 后接入 AdSense
- [ ] 早期接入 Adsterra 过渡

---

## 设计方向

### 主题色
- 背景：深黑 (#0a0a0f) + 深灰纹理
- 主色：暗红 (#c23028) — 血刃/武侠
- 点缀：金色 (#d4a843) — 江湖/传统
- 文字：白/浅灰

### 视觉特效（canvas-fx）
- 首页 Hero：粒子流（剑气/刀光方向性粒子）
- 页面过渡：轻量 glitch 效果
- Boss 页面：暗色流体背景
- 整体风格：暗黑武侠 + 赛博朋克混搭

### 参考风格
- 竞品 phantombladezero.wiki 的暗色调
- Fextralife 的信息密度
- 黑神话悟空 wiki 的页面结构
- 加入 canvas-fx 特效做差异化

---

## 多语言（后续）

| 优先级 | 语言 | 依据 |
|--------|------|------|
| 1 | English | 主力，覆盖全球 |
| 2 | Français | Trends Rising "date de sortie" |
| 3 | Português | Trends Rising "preço"，巴西市场 |
| 4 | Deutsch | Trends 德国热度高 |

---

## 图片素材来源

| 来源 | 用途 | 获取方式 |
|------|------|----------|
| pbz.s-game.com | Key Art、官方截图 | 直接下载 |
| Steam 商店页 | 截图、胶囊图 | SteamDB 高清版 |
| YouTube 预告片 | 角色/Boss/武器截帧 | yt-dlp + ffmpeg |
| @pbzero_official (X) | 官方发布图 | 保存原图 |
| Demo 录像 | UI/战斗系统截图 | YouTube 截帧 |

---

## 关键数据参考

| 指标 | 数据 |
|------|------|
| 主词 Trends 热度 | 46-100（20-30x GPTs） |
| SEO Difficulty | 54/100 |
| On-Page Difficulty | 18-38/100（内容门槛极低） |
| 竞品最高月流量 | 58/mo（Fandom） |
| 预估发售后月流量 | 3000-8000/mo |
| 参照（黑神话 boss guide） | 1800/mo |

---

## 文件结构

```
pbzero-wiki/
├── public/
│   ├── images/         # 游戏截图、角色图、Boss图
│   ├── favicon.ico
│   └── site.webmanifest
├── src/
│   ├── app/
│   │   ├── layout.tsx          # 全局布局 + GA + 主题
│   │   ├── page.tsx            # 首页
│   │   ├── [slug]/page.tsx     # 动态内页
│   │   ├── robots.txt/route.ts
│   │   └── sitemap.xml/route.ts
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   ├── HeroFx.tsx         # canvas-fx 首页特效
│   │   ├── BossCard.tsx
│   │   ├── CharacterCard.tsx
│   │   └── WeaponCard.tsx
│   ├── content/
│   │   ├── pages.ts           # 所有页面内容数据
│   │   └── characters.ts     # 角色数据
│   └── lib/
│       └── canvas-fx/         # canvas-fx 特效引擎
├── next.config.mjs
├── tailwind.config.ts
├── package.json
└── plan.md
```
