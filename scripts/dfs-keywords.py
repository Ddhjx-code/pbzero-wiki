#!/usr/bin/env python3
"""
DataForSEO 关键词管线 —— 关键词调研的"量 + 能不能赢"那一层。

前置：keyword-research.py 已经用自动补全抓出真实搜索词（证明有人在搜）。
本脚本回答另外两个问题：
  1. 这个词每月到底多少人搜（绝对量，不是相对热度）
  2. 这个词的首页被谁占着（决定做了能不能排上去）

用法:
  python3 scripts/dfs-keywords.py volume --inputs reports/pbz-brand-raw.csv
  python3 scripts/dfs-keywords.py all --site pbz --serp-top 150
  python3 scripts/dfs-keywords.py all --site pbz --dry-run      # 只估算花费

凭证: .secrets/dfs-auth.txt 内容为 "login:password"（app.dataforseo.com/api-access 获取）
      或环境变量 DFS_LOGIN / DFS_PASSWORD

计费（2026-11 官方价）:
  search_volume/live               $0.09 / 次（每次最多 1000 词）
  search_volume/standard           $0.06 / 次（队列 1-3 小时）
  serp/yahoo/organic/live/advanced  $0.004 / 次（10 条结果；Bing 通道有反爬诱饵页，不可用）
  dataforseo_labs/bulk_keyword_difficulty $0.012/task + $0.00012/item
"""

import argparse
import base64
import csv
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://api.dataforseo.com"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# DataForSEO 的接口在国内可直连，走代理只会多一层 TLS reset 的来源。
# 默认直连；需要时用 DFS_PROXY=http://127.0.0.1:7897 显式指定。
PROXY = os.environ.get("DFS_PROXY", "").strip()
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36")

# 单次调用价格（美元），仅用于 dry-run 预估
PRICE = {
    "volume_live": 0.09,
    "volume_standard": 0.06,
    "serp_live": 0.004,   # Yahoo live advanced（Bing 的 $0.002 不能用，见 fetch_serp）
    "kd_task": 0.012,
    "kd_item": 0.00012,
}

LOCATION_US = 2840
LOCATION_UK = 2826
LANG_EN = "en"

# 自己站的域名：用于在 SERP 里识别"我们已经在榜上"和"榜上那个小站是对手"
SITE_HOST = {
    "pbz": "pbzero.wiki",
    "e33": "expedition33.wiki",
    "morse": "morsecodenow.com",
}

# 判断 SERP 是否跑题用的品牌词：Bing 偶发会返回完全无关的结果（实测过），
# 必须用品牌词校验，否则脏数据会被当成"可攻"。
SITE_BRAND = {
    "pbz": ["phantom blade"],
    "e33": ["expedition 33", "clair obscur"],
    "morse": ["morse"],
}

# 占据 SERP 首页的"大站"——这些域名在场就说明这个词被巨头锁死。
# 按后缀匹配，因为真实返回的是 phantom-blade.fandom.com / en.wikipedia.org 这类子域名。
AUTHORITY = {
    "fandom.com", "ign.com", "reddit.com", "youtube.com", "game8.co",
    "gamefaqs.gamespot.com", "powerpyx.com", "gamerant.com", "screenrant.com",
    "steamcommunity.com", "store.steampowered.com", "wikipedia.org",
    "facebook.com", "tiktok.com", "nexusmods.com", "pushsquare.com",
    "pcgamer.com", "gamesradar.com", "thegamer.com", "dexerto.com",
    "sportskeeda.com", "beebom.com", "gamerguides.com", "segmentnext.com",
    "gameskinny.com", "primagames.com", "dotesports.com", "si.com",
    "eurogamer.net", "polygon.com", "metacritic.com", "opencritic.com",
    # 游戏 wiki 领域的既有大网，体量等同 fandom
    "fextralife.com", "neoseeker.com", "gamepressure.com", "gamesatlas.com",
    "holdtoreset.com", "steamcommunity.com", "xbox.com", "playstation.com",
    "nintendo.com", "twitch.tv", "amazon.com", "ebay.com", "imdb.com",
}


def is_auth(domain):
    """子域名也算命中：phantom-blade.fandom.com 属于 fandom.com。"""
    return any(domain == a or domain.endswith("." + a) for a in AUTHORITY)


# ---------------------------------------------------------------- transport
def auth_header():
    login = os.environ.get("DFS_LOGIN")
    pw = os.environ.get("DFS_PASSWORD")
    if not (login and pw):
        p = os.path.join(ROOT, ".secrets", "dfs-auth.txt")
        if not os.path.exists(p):
            sys.exit(f"缺少凭证: 把 \"login:password\" 写进 {p}\n"
                     f"或设置 DFS_LOGIN / DFS_PASSWORD 环境变量。\n"
                     f"（app.dataforseo.com/api-access 页面可以拿到）")
        raw = open(p).read().strip()
        if ":" not in raw:
            sys.exit(f"{p} 格式应为 login:password")
        login, pw = raw.split(":", 1)
    token = base64.b64encode(f"{login}:{pw}".encode()).decode()
    return f"Basic {token}"


def _request(method, path, payload=None, timeout=90, tries=4):
    """统一的 JSON 请求，带重试。返回解析后的 dict。"""
    data = json.dumps(payload).encode() if payload is not None else None
    handlers = [urllib.request.ProxyHandler(
        {"http": PROXY, "https": PROXY})] if PROXY else []
    opener = urllib.request.build_opener(*handlers)
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(
            BASE + path, data=data, method=method,
            headers={
                "Authorization": auth_header(),
                "Content-Type": "application/json",
                # 不加这句会被 gzip 卡死（在这个项目里踩过两次）
                "Accept-Encoding": "identity",
                "User-Agent": UA,
            })
        try:
            with opener.open(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try:
                return json.loads(body)
            except Exception:
                last = f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 + attempt * 3)
    sys.exit(f"请求失败 {method} {path} -> {last}")


def post(path, payload, timeout=90, tries=4):
    return _request("POST", path, payload, timeout, tries)


def get(path, timeout=90, tries=4):
    """task_get / tasks_ready 在 DataForSEO v3 里是 GET，用 POST 会返回 40400。"""
    return _request("GET", path, None, timeout, tries)


def check(resp, label):
    """DataForSEO 的错都在 body 里，HTTP 状态码经常还是 200。"""
    code = resp.get("status_code")
    if code not in (20000,):
        msg = resp.get("status_message", "")
        hint = {
            40100: "凭证不对。.secrets/dfs-auth.txt 要用 app.dataforseo.com/api-access "
                   "页面给的 API login/password，不是登录邮箱。",
            40104: "账号还没验证。去 app.dataforseo.com 用户面板点验证（查邮箱里的确认信），"
                   "验证完成后 API 才会放行。",
            40200: "余额不足。app.dataforseo.com 充值，最低 $50（余额不过期）。",
            40201: "余额不足。app.dataforseo.com 充值，最低 $50（余额不过期）。",
            40501: "请求体字段有问题，检查 location_code / language_code。",
        }.get(code)
        sys.exit(f"[{label}] API 报错 {code}: {msg}" + (f"\n  → {hint}" if hint else ""))
    return resp


# ---------------------------------------------------------------- steps
def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def vol_ok(kw):
    """Google Ads 接口对单词数/长度有硬限制，一个不合规的词会让整批 1000 个词被拒。"""
    return 1 <= len(kw.split()) <= 10 and len(kw) <= 80


def clean_kw(w):
    """规范化成接口能接受的形式。

    自动补全抓来的词里混着撇号（collector's）、尾随引号、
    越南语/葡萄牙语（khi nào ra mắt）——这些都算 invalid character，
    会让整批 1000 个词一起被拒。这里统一清洗，非拉丁字符直接抹掉；
    清洗后为空或变形的词由调用方决定是否跳过。
    """
    w = w.lower().replace("\u2019", "'").replace("\u2018", "'")
    w = w.replace("\u201c", '"').replace("\u201d", '"')
    # 越南语/葡语这类非拉丁字符，抹掉后只剩残词（"khi nào ra mắt" -> "khi n o ra m t"），
    # 发过去只会换回 0 量并污染结果，直接判空跳过。
    if re.search(r"[^\x00-\x7F]", w):
        return ""
    w = re.sub(r"[\"'`]", "", w)          # 撇号/引号
    w = re.sub(r"[^a-z0-9\s+-]", " ", w)
    return re.sub(r"\s+", " ", w).strip()


_last_call = [0.0]


def throttle(gap):
    """全局节流。二分重试会短时间打多次，不打散就会被判异常。"""
    wait = gap - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def fetch_volume(keywords, mode="live"):
    """返回 {keyword: {volume, cpc, competition, monthly}}。"""
    out, spent = {}, 0.0
    per = 1000
    batches = [b for b in chunk(keywords, per)]
    total = len(batches)
    n = 0

    def run(batch, depth=0):
        """一批被拒就二分重试——别因为一个坏词丢掉 999 个好词。"""
        nonlocal spent
        throttle(5.5 if mode == "live" else 1.0)  # live 限 12 次/分钟
        task = {"keywords": batch, "location_code": LOCATION_US,
                "language_code": LANG_EN, "search_partners": False}
        resp = check(post("/v3/keywords_data/google_ads/search_volume/" + mode,
                          [task]), "volume")
        spent += float(resp.get("cost") or 0)
        bad = False
        for t in resp.get("tasks", []):
            if t.get("status_code") != 20000:
                bad = True
                msg = t.get("status_message") or ""
                if len(batch) > 1 and depth < 12:
                    mid = len(batch) // 2
                    print(f"  ! 批次被拒（{msg[:60]}），二分重试", file=sys.stderr)
                    run(batch[:mid], depth + 1)
                    run(batch[mid:], depth + 1)
                else:
                    print(f"  ! 丢弃 {batch[0]!r}: {msg[:80]}", file=sys.stderr)
                continue
            for item in (t.get("result") or []):
                kw = (item.get("keyword") or "").lower()
                if not kw:
                    continue
                out[kw] = {
                    "volume": item.get("search_volume"),
                    "cpc": item.get("cpc"),
                    "competition": item.get("competition"),
                    "monthly": item.get("monthly_searches") or [],
                }
        return bad

    for batch in batches:
        n += 1
        run(batch)
        print(f"  volume {n}/{total} 批（{len(batch)} 词）已花 ${spent:.4f}，"
              f"累计拿到 {len(out)} 个词", file=sys.stderr)
    return out, spent


def fetch_kd(keywords):
    """Google 关键词难度 0-100。返回 {keyword: {kd, kd_level}}。"""
    out, spent = {}, 0.0
    for batch in chunk(keywords, 700):
        throttle(1.0)
        task = {"keywords": batch, "location_code": LOCATION_US,
                "language_code": LANG_EN}
        resp = check(post("/v3/dataforseo_labs/google/bulk_keyword_difficulty/live",
                          [task]), "kd")
        spent += float(resp.get("cost") or 0)
        for t in resp.get("tasks", []):
            for item in (t.get("result") or []):
                for it in (item.get("items") or []):
                    kw = (it.get("keyword") or "").lower()
                    if kw:
                        out[kw] = {"kd": it.get("keyword_difficulty"),
                                   "kd_level": it.get("difficulty")}
        print(f"  kd 已花 ${spent:.4f}", file=sys.stderr)
    return out, spent


def _serp_once(keyword, depth=10):
    """单次取首页，不做校验。走 Yahoo。"""
    task = {"keyword": keyword, "location_code": LOCATION_US,
            "language_code": LANG_EN, "depth": depth, "device": "desktop"}
    resp = check(post("/v3/serp/yahoo/organic/live/advanced", [task]), "serp")
    cost = float(resp.get("cost") or 0)
    items = []
    for t in resp.get("tasks", []):
        for r in (t.get("result") or []):
            for it in (r.get("items") or []):
                if it.get("type") != "organic":
                    continue
                items.append({
                    "rank": it.get("rank_absolute"),
                    "domain": (it.get("domain") or "").lower(),
                    "url": it.get("url") or "",
                    "title": (it.get("title") or "")[:80],
                })
    items.sort(key=lambda x: x["rank"] or 999)
    return items, cost


def _on_topic(items, brand_tokens):
    """有多少条结果确实在讲这个游戏。Bing 偶发会返回完全无关的页面。"""
    if not brand_tokens:
        return len(items)
    n = 0
    for i in items:
        blob = (i["domain"] + " " + i["url"] + " " + i["title"]).lower()
        if any(b in blob for b in brand_tokens):
            n += 1
    return n


def fetch_serp(keyword, depth=10, brand_tokens=(), tries=4):
    """取首页前 10 名，带跑题校验与退避重试。

    为什么用 Yahoo 而不是 Google / Bing（三个都实测过）：
    - Google：url 全被包装成 google.com/goto?url=<加密串>，拿不到域名，本地也解不开
    - Bing  ：实测 7 个词有 3 个返回反爬诱饵页（www.manitoba.ca、
              wordle-hint-today.com、nytimes.com），同一词隔几秒重试也会再中；
              批量跑下来约 5 成是噪声，不可用
    - Yahoo ：同一批词 7/7 全干净，且它的索引就是 Bing 的，排名可代表同一套结果；
              这三个站的有机流量本来也来自 Bing/DDG/Ecosia/Yahoo，Google 只有 0-3 次点击

    仍然保留品牌词命中校验：任何引擎都可能偶发返回无关页，一旦命中过低就重试
    （间隔 3s / 10s / 25s），取命中数最高的一次，实在不行标记为"脏数据"排除排序。
    """
    best_items, best_hits, cost_total = [], -1, 0.0
    backoff = [0, 3, 10, 25]
    for attempt in range(tries):
        wait = backoff[attempt] if attempt < len(backoff) else 25
        if wait:
            time.sleep(wait)
        items, c = _serp_once(keyword, depth)
        cost_total += c
        hits = _on_topic(items, brand_tokens)
        if hits > best_hits:
            best_items, best_hits = items, hits
        if not brand_tokens or hits >= max(3, len(items) // 2):
            break
    return best_items, cost_total, best_hits


def serp_profile(items, own_domain=None, brand_tokens=()):
    """从首页构成推断这个词能不能打。

    判定不只看"大站占几个"，更看"有没有小站挤进去了"——后者才是最硬的证据。
    游戏站最常见的首页就是 10 个位置里 7-8 个被 fandom/ign/reddit/youtube 占着，
    但只要还能看到一个非大站在前 5，说明这条路是通的。

    同一个域名可能在首页出现多次（目录页 + 内容页），按域名去重，否则大站数虚高。
    """
    if not items:
        return {"n_auth": 0, "best_small": 0, "n_small": 0, "domains": "",
                "auth_domains": "", "small_top3": False, "own_rank": 0,
                "on_topic": 0, "verdict": "无数据"}
    on_topic = _on_topic(items, brand_tokens)
    if brand_tokens and on_topic < 3:
        # 首页结果跟这个词无关，任何"可攻/锁死"的判断都是噪声
        return {"n_auth": 0, "best_small": 0, "n_small": 0,
                "domains": "|".join(i["domain"] for i in items),
                "auth_domains": "", "small_top3": False, "own_rank": 0,
                "on_topic": on_topic, "verdict": "脏数据"}
    seen, uniq = set(), []
    for i in items:
        d = i["domain"]
        if not d or d in seen:
            continue
        seen.add(d)
        uniq.append(i)

    own_rank = 0
    if own_domain:
        own = own_domain.lower()
        for i in uniq:
            if i["domain"] == own or i["domain"].endswith("." + own):
                own_rank = i["rank"] or 0
                break

    domains = [i["domain"] for i in uniq]
    auth = [d for d in domains if is_auth(d)]
    small = [(i["rank"], i["domain"]) for i in uniq
             if not is_auth(i["domain"]) and i["domain"] != (own_domain or "").lower()]
    best_small = min([r for r, _ in small], default=0)
    n_auth = len(auth)
    small_top3 = bool(best_small and best_small <= 3)

    if own_rank and own_rank <= 3:
        verdict = "已占据"      # 自己的站已经在榜首，不需要再做
    elif n_auth >= 9 and not small_top3:
        verdict = "锁死"        # 10 个位置几乎全是大站，做了也排不上去
    elif small_top3:
        verdict = "可攻"        # 已有小站进前 3，这个位置能抢
    elif n_auth >= 6:
        verdict = "难"
    elif best_small and best_small <= 6:
        verdict = "有机会"
    elif n_auth >= 3:
        verdict = "中"
    else:
        verdict = "有机会"
    return {"n_auth": n_auth, "best_small": best_small,
            "n_small": len(small), "domains": "|".join(domains),
            "auth_domains": "|".join(auth), "small_top3": small_top3,
            "own_rank": own_rank, "on_topic": on_topic, "verdict": verdict}


# ---------------------------------------------------------------- io
def apply_serp_to_row(m, prof):
    """把 serp_profile() 的结果写进 CSV 行字段（字段名与主流程合并处一致）。"""
    m["serp_verdict"] = prof.get("verdict", "")
    m["serp_n_auth"] = prof.get("n_auth", "")
    m["serp_best_small_rank"] = prof.get("best_small", "")
    m["serp_small_top3"] = "1" if prof.get("small_top3") else ""
    m["serp_own_rank"] = prof.get("own_rank", "")
    m["serp_domains"] = prof.get("domains", "")


def load_keywords(paths):
    """读 keyword-research.py 产出的 CSV，保留元数据。"""
    rows, seen = [], set()
    for p in paths:
        if not os.path.exists(p):
            print(f"跳过不存在的文件 {p}", file=sys.stderr)
            continue
        with open(p) as f:
            for r in csv.DictReader(f):
                w = (r.get("word") or "").strip().lower()
                if not w or w in seen:
                    continue
                seen.add(w)
                rows.append(r)
    return rows


def pick_serp_targets(rows, top, gaps_only, vol=None, min_volume=0):
    """挑要跑 SERP 的词：优先"没页面 + 高意图 + 多引擎一致"。

    拿到搜索量之后一定要再按量筛一遍：SERP 是这里最贵的接口（$0.004/词），
    而 10-50 量的词就算排到第一，一天也带不来一个点击。花的钱要和可能拿到的
    流量对得上，所以 vol 传进来时只用"量 ≥ min_volume"的词。
    """
    cand = [r for r in rows if (r.get("has_page") == "0" or not gaps_only)]
    if vol is not None:
        vget = lambda r: vol.get((r.get("word") or "").strip().lower(), {})
        cand = [r for r in cand if isinstance(vget(r).get("volume"), int)
                and vget(r)["volume"] >= min_volume]
        cand.sort(key=lambda r: (-float(r.get("intent") or 0),
                                 -vget(r)["volume"]))
    else:
        cand.sort(key=lambda r: (-float(r.get("intent") or 0),
                                 -float(r.get("score") or 0)))
    return cand[:top]


def write_csv(path, rows):
    if not rows:
        return
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", nargs="?", choices=["volume", "kd", "serp", "all"],
                    help="跑哪一步；用 --rerank 时可以省略")
    ap.add_argument("--inputs", nargs="+", default=None)
    ap.add_argument("--site", default=None, help="站点前缀，用于输出文件名")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 个词")
    ap.add_argument("--serp-top", type=int, default=120,
                    help="对多少个词跑 SERP 竞争分析")
    ap.add_argument("--all-keywords", action="store_true",
                    help="SERP 不限于无页面的词")
    ap.add_argument("--mode", default="live", choices=["live", "standard"])
    ap.add_argument("--out-prefix", default=None)
    ap.add_argument("--own-domain", default=None,
                    help="自己站的域名，用于识别 SERP 里是否已有自己（默认按 --site 推断）")
    ap.add_argument("--serp-delay", type=float, default=2.0,
                    help="两次 SERP 请求之间的间隔秒数，太短会触发抓取端截断查询串")
    ap.add_argument("--rerank", default=None,
                    help="只重算排序与报告，不请求接口。传入上一轮的 CSV 路径")
    ap.add_argument("--min-volume", type=int, default=100,
                    help="只对月搜 ≥ 该值的词跑 SERP（默认 100；0 = 不筛）")
    ap.add_argument("--resume", default=None,
                    help="接着上一轮 CSV 跑：只补\"有量但没看过 SERP\"的词，"
                         "已有的量/KD/判定全部沿用，不重复花钱")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    own_domain = args.own_domain or SITE_HOST.get(args.site or "")
    brand_tokens = SITE_BRAND.get(args.site or "", [])

    if args.rerank:
        merged = load_prev_csv(args.rerank)
        prefix = args.out_prefix or args.rerank.rsplit(".", 1)[0]
        n_serp = sum(1 for m in merged if m.get("serp_verdict"))
        return score_and_report(merged, prefix, args, 0.0, own_domain,
                                len(merged), n_serp)

    if args.resume:
        # 续跑：只补"已经知道有量、但还没看过首页"的词。
        # 量/KD/已有判定全部沿用，不再重复请求——补 290 个词就是 290 × $0.004。
        merged = load_prev_csv(args.resume)
        prefix = args.out_prefix or args.resume.rsplit(".", 1)[0]
        todo = [m for m in merged if not m.get("serp_verdict")
                and isinstance(m.get("volume"), int)
                and m["volume"] >= args.min_volume]
        todo.sort(key=lambda m: -m["volume"])   # 先把有量的看完，量大的先看
        if args.serp_top:
            todo = todo[:args.serp_top]
        est = len(todo) * PRICE["serp_live"]
        print(f"续跑 {args.resume}：月搜 ≥{args.min_volume} 且未验首页的有 "
              f"{len(todo)} 个词，预估 ${est:.3f}"
              f"（{len(todo)} 次 × ${PRICE['serp_live']}）", file=sys.stderr)
        if args.dry_run:
            print("dry-run，未发起请求。", file=sys.stderr)
            return 0
        spent = 0.0
        for i, m in enumerate(todo, 1):
            items, c, hits = fetch_serp(m["keyword"], brand_tokens=brand_tokens)
            spent += c
            apply_serp_to_row(m, serp_profile(items, own_domain, brand_tokens))
            if i % 10 == 0 or i == len(todo):
                print(f"  serp {i}/{len(todo)} 已花 ${spent:.4f}",
                      file=sys.stderr)
            time.sleep(args.serp_delay)
        n_serp = sum(1 for x in merged if x.get("serp_verdict"))
        return score_and_report(merged, prefix, args, spent, own_domain,
                                len(merged), n_serp)

    inputs = args.inputs or [
        os.path.join(ROOT, "reports", f"{args.site}-brand-raw.csv")]
    rows = load_keywords(inputs)
    if not rows:
        sys.exit("没有读到关键词")
    if args.limit:
        rows = rows[:args.limit]
    words = [r["word"].strip().lower() for r in rows]
    # 清洗 + 限长。保留 清洗后→原始 的映射，结果按原始词回填，
    # 否则 collector's 这种被清洗过的词在合并时会对不上号。
    pairs, seen_send = [], set()
    for w in words:
        c = clean_kw(w)
        if not c or not vol_ok(c) or c in seen_send:
            continue
        seen_send.add(c)
        pairs.append((c, w))
    words_send = [c for c, _ in pairs]
    remap = {c: w for c, w in pairs}
    skipped = len(words) - len(pairs)
    # all 模式先拉到量再挑 SERP 目标（见下面），其余模式只能按意图/分数挑。
    serp_targets = (None if args.step == "all" else
                    pick_serp_targets(rows, args.serp_top, not args.all_keywords))

    # ---- 预估（按实际要跑的步骤算，别把没跑的部分也算进去）
    n_vol = (len(words_send) + 999) // 1000
    n_kd = (len(words_send) + 699) // 700
    c_vol = n_vol * PRICE["volume_" + args.mode] if args.step in ("volume", "all") else 0
    c_kd = (n_kd * PRICE["kd_task"] + len(words_send) * PRICE["kd_item"]) \
        if args.step in ("kd", "all") else 0
    c_serp = (len(serp_targets) * PRICE["serp_live"]
              if serp_targets is not None and args.step in ("serp", "all") else 0)
    est = c_vol + c_kd + c_serp
    parts = []
    if c_vol:
        parts.append(f"volume {n_vol} 次 × ${PRICE['volume_' + args.mode]}")
    if c_kd:
        parts.append(f"kd {n_kd} 次")
    if c_serp:
        parts.append(f"serp {len(serp_targets)} 次 × ${PRICE['serp_live']}")
    print(f"关键词 {len(words)} 个（{skipped} 个超长已跳过）· "
          f"SERP 抽样 "
          f"{len(serp_targets) if serp_targets is not None else args.serp_top}"
          f" 个（月搜 ≥{args.min_volume} 才跑）", file=sys.stderr)
    if serp_targets is None:
        print(f"预估固定部分 ${est:.3f}（{'; '.join(parts)}）；"
              f"SERP 目标要等拿到量才知道实际几个，上限 "
              f"${args.serp_top * PRICE['serp_live']:.3f}", file=sys.stderr)
    else:
        print(f"预估花费 ${est:.3f}（{'; '.join(parts) or '无'}）", file=sys.stderr)
    if args.dry_run:
        print("dry-run，未发起请求。", file=sys.stderr)
        return 0

    prefix = args.out_prefix or os.path.join(
        ROOT, "reports", f"dfs-{args.site or 'all'}-{time.strftime('%Y-%m-%d')}")
    vol, kd, serp = {}, {}, {}
    spent = 0.0

    if args.step in ("volume", "all"):
        print("→ 拉绝对搜索量", file=sys.stderr)
        vol, c = fetch_volume(words_send, mode=args.mode)
        spent += c
        # 统一用小写做键：合并、按量挑 SERP 目标都按小写查，避免大小写对不上丢量
        vol = {(remap.get(k, k) or k).strip().lower(): v for k, v in vol.items()}
        print(f"  拿到 {len(vol)} 个词的量", file=sys.stderr)

    if args.step in ("kd", "all"):
        print("→ 拉关键词难度", file=sys.stderr)
        kd, c = fetch_kd(words_send)
        spent += c
        kd = {remap.get(k, k): v for k, v in kd.items()}

    if args.step in ("serp", "all"):
        if serp_targets is None:
            # 量到手了才挑：SERP 是最贵的一步，不值得花在没量或量太小的词上
            serp_targets = pick_serp_targets(rows, args.serp_top,
                                             not args.all_keywords,
                                             vol, args.min_volume)
            print(f"  按月搜 ≥{args.min_volume} 筛出 {len(serp_targets)} 个词，"
                  f"预计 ${len(serp_targets) * PRICE['serp_live']:.3f}",
                  file=sys.stderr)
        print(f"→ 跑首页竞争（{len(serp_targets)} 个词）", file=sys.stderr)
        for i, t in enumerate(serp_targets, 1):
            items, c, hits = fetch_serp(t["word"], brand_tokens=brand_tokens)
            spent += c
            serp[t["word"]] = serp_profile(items, own_domain, brand_tokens)
            if i % 10 == 0 or i == len(serp_targets):
                print(f"  serp {i}/{len(serp_targets)} 已花 ${spent:.4f}",
                      file=sys.stderr)
            time.sleep(args.serp_delay)

    # ---- 合并
    merged = []
    for r in rows:
        w = r["word"].strip().lower()
        v = vol.get(w, {})
        k = kd.get(w, {})
        s = serp.get(w, {})
        volume = v.get("volume")
        merged.append({
            "keyword": r["word"],
            "volume": volume if volume is not None else "",
            "cpc": v.get("cpc", ""),
            "competition": v.get("competition", ""),
            "kd": k.get("kd", ""),
            "serp_verdict": s.get("verdict", ""),
            "serp_n_auth": s.get("n_auth", ""),
            "serp_best_small_rank": s.get("best_small", ""),
            "serp_small_top3": ("1" if s.get("small_top3") else "") if s else "",
            "serp_own_rank": s.get("own_rank", ""),
            "serp_domains": s.get("domains", ""),
            "cluster": r.get("cluster", ""),
            "intent": r.get("intent", ""),
            "n_engines": r.get("n_engines", ""),
            "has_page": r.get("has_page", ""),
            "near_page": r.get("near_page", ""),
            "score": r.get("score", ""),
        })

    return score_and_report(merged, prefix, args, spent, own_domain,
                            len(words), len(serp))


INTENT_WEIGHT = {"3": 1.0, "2": 0.7, "1": 0.2}

# 上游分类太宽：wallpaper / gamestop / epic games 这类被算成"中意图"，
# 但它们是要买、要图、要跳转别家商店，wiki 站既抢不到也不该抢。本地再压一层。
NOT_FOR_WIKI = re.compile(
    r"\bwallpaper|gamestop|cdkeys?|cd key|epic games|steam key|green ?man gaming|"
    r"cheap|discount|sale\b|buy\b|price|download|crack|torrent|reddit|metacritic|"
    r"amazon|ebay|fortnite skin|trainer|cheat engine|mod menu|apk\b|torrent")


def score_and_report(merged, prefix, args, spent, own_domain, n_words, n_serp):
    """打分 + 写 CSV/MD。拆出来是为了 --rerank 能复用，不必重复请求接口。"""
    # 机会分 = 量 × 好不好打 × 站内有没有页 × 这个意图 wiki 能不能吃。
    # 没做过 SERP 的词不参与排序，否则默认权重会把"还没验证"的词排到已验证词前面。
    def opportunity(m):
        vol_ = m["volume"] if isinstance(m["volume"], int) else 0
        if vol_ <= 0 or not m["serp_verdict"]:
            return 0.0
        base = math.log10(vol_ + 1)
        weight = {"可攻": 1.0, "有机会": 0.75, "中": 0.55, "难": 0.3,
                  "锁死": 0.08, "已占据": 0.0, "脏数据": 0.0}.get(
                      m["serp_verdict"], 0.3)
        if m["serp_small_top3"] == "1":
            weight = min(1.0, weight * 1.25)
        gap = 1.0 if m["has_page"] == "0" else 0.35
        # 意图权重：wallpaper / gamestop / cdkeys 这类词再热也轮不到 wiki，
        # 不压权重的话 Top 20 会全是抢不到的商业词。
        intent = str(m.get("intent", ""))
        if NOT_FOR_WIKI.search(m["keyword"].lower()):
            intent = "1"
        iw = INTENT_WEIGHT.get(intent, 0.5)
        return round(base * weight * gap * iw * 10, 2)

    for m in merged:
        m["opportunity"] = opportunity(m)
    merged.sort(key=lambda m: -m["opportunity"])

    csv_path = prefix + ".csv"
    write_csv(csv_path, merged)
    print(f"\n写了 {csv_path}", file=sys.stderr)

    have_vol = [m for m in merged if isinstance(m["volume"], int) and m["volume"] > 0]
    analyzed = [m for m in merged if m["opportunity"] > 0]
    pending = [m for m in merged if not m["serp_verdict"] and
               isinstance(m["volume"], int) and m["volume"] > 0]

    md_path = prefix + ".md"
    with open(md_path, "w") as f:
        f.write(f"# DataForSEO 关键词验证 — {args.site or 'all'}\n\n")
        f.write(f"- 输入词 {n_words} 个，有绝对量的 {len(have_vol)} 个，"
                f"做过首页竞争的 {n_serp} 个\n")
        # 重排模式不请求接口，写 0 会让人误以为真的免费跑了一轮
        f.write(f"- 本次实际花费 **${spent:.3f}**\n" if spent > 0
                else "- 本轮为**重排**（未请求接口，不产生费用）\n")
        f.write(f"- 生成时间 {time.strftime('%Y-%m-%d %H:%M')}\n")
        if have_vol:
            # 这条必须写：Google Ads 的 search_volume 是 12 个月均值，且月更滞后。
            # 刚上线的游戏会被前面的冷启动月份摊平，峰值体现不出来（实测差 3-9 倍）。
            f.write("- 月搜是 **过去 12 个月的平均值**（Google Ads 口径），"
                    "最新完整月份通常滞后 1–2 个月\n")
            f.write("- 刚上线/刚公布的游戏会被此前的冷启动月份摊平，"
                    "看趋势用 `scripts/dfs-trend.py`（逐月明细）\n")
        dirty = [m for m in merged if m["serp_verdict"] == "脏数据"]
        if dirty:
            f.write(f"- 重试仍跑题的词 **{len(dirty)} 个**，已排除在排序之外"
                    f"（引擎偶发返回无关首页）\n")
        if n_serp:
            f.write("- 首页竞争取自 **Yahoo**（索引即 Bing；Bing 直连通道实测有反爬诱饵页，"
                    "Google 结果 url 被包装成 goto 跳转拿不到域名）\n")
            if getattr(args, "min_volume", 0):
                f.write(f"- SERP 只跑月搜 **≥{args.min_volume}** 的词："
                        f"首页查询 $0.004/词，小量词排第一也带不来点击\n")
        if own_domain:
            f.write(f"- 自身域名：`{own_domain}`\n")
        f.write("\n")
        if have_vol:
            f.write("## 量级分布\n\n")
            buckets = [(0, 10), (10, 50), (50, 100), (100, 500),
                       (500, 1000), (1000, 10**9)]
            for lo, hi in buckets:
                c = sum(1 for m in have_vol if lo < m["volume"] <= hi) \
                    if lo else sum(1 for m in have_vol if m["volume"] <= hi)
                label = f"{lo}–{hi}" if hi < 10**9 else f"{lo}+"
                f.write(f"- {label}: {c}\n")
            f.write("\n")

        f.write("## 机会排序（已做首页竞争分析）\n\n")
        f.write("机会分 = log10(月搜索量) × 可打权重 × 缺口权重 × 意图权重"
                "（意图 3=1.0 / 2=0.7 / 1=0.2）。只列已经看过 SERP 的词。\n\n")
        if analyzed:
            f.write("| # | 关键词 | 月搜 | KD | 首页判定 | 大站数 | 小站最好名次 "
                    "| 站内 | 意图 | 簇 |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")
            for i, m in enumerate(analyzed[:40], 1):
                page = "无" if m["has_page"] == "0" else "有"
                f.write(f"| {i} | {m['keyword']} | {m['volume']} | {m['kd']} | "
                        f"{m['serp_verdict']} | {m['serp_n_auth']} | "
                        f"{m['serp_best_small_rank'] or '—'} | {page} | "
                        f"{m['intent']} | {m['cluster']} |\n")
        else:
            f.write("（本次没有跑 SERP，加 `--serp-top N` 补上）\n")

        if pending:
            f.write(f"\n## 有量但还没看 SERP（{len(pending)} 个，按量排序前 30）\n\n")
            f.write("这些词已经知道有人在搜、月搜多少，但还没验证首页打不打得过。"
                    "下一轮 `--serp-top` 应该从这里取。\n\n")
            f.write("| 关键词 | 月搜 | KD | 站内 | 簇 |\n|---|---|---|---|---|\n")
            pending.sort(key=lambda m: -m["volume"])
            for m in pending[:30]:
                page = "无" if m["has_page"] == "0" else "有"
                f.write(f"| {m['keyword']} | {m['volume']} | {m['kd']} | "
                        f"{page} | {m['cluster']} |\n")

        if n_serp:
            f.write("\n## 首页被谁占着（抽样明细）\n\n")
            f.write("| 关键词 | 判定 | 前 5 名域名 |\n|---|---|---|\n")
            for m in [x for x in merged if x["serp_verdict"]][:30]:
                d = m["serp_domains"].split("|")[:5]
                f.write(f"| {m['keyword']} | {m['serp_verdict']} | "
                        f"{', '.join(d)} |\n")
    print(f"写了 {md_path}", file=sys.stderr)
    return 0


def load_prev_csv(path):
    """把上一轮跑出来的 CSV 读回来，让 --rerank 能只重排不重跑接口。"""
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            m = dict(r)
            for k in ("volume", "kd", "serp_n_auth", "serp_best_small_rank",
                      "serp_own_rank"):
                v = m.get(k, "")
                m[k] = int(v) if str(v).strip().lstrip("-").isdigit() else ""
            out.append(m)
    return out


if __name__ == "__main__":
    sys.exit(main())
