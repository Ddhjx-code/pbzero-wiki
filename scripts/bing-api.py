#!/usr/bin/env python3
"""Bing Webmaster API 客户端。

用法:
    python3 scripts/bing-api.py sites                    # 账号下所有站点
    python3 scripts/bing-api.py feeds    --site pbzero   # sitemap 登记状态
    python3 scripts/bing-api.py traffic  --site pbzero   # 每日点击/曝光
    python3 scripts/bing-api.py queries  --site pbzero   # 关键词表现
    python3 scripts/bing-api.py crawl    --site pbzero   # 抓取统计
    python3 scripts/bing-api.py issues   --site pbzero   # 抓取错误
    python3 scripts/bing-api.py urlinfo  --site pbzero --url https://pbzero.wiki/map
    python3 scripts/bing-api.py submit-feed --site pbzero
    python3 scripts/bing-api.py submit-url  --site pbzero --urls /map,/boss-order

    # 快照：把当期数字存成 JSON，供日后机械比对
    python3 scripts/bing-api.py snapshot --site pbzero --out reports/bing-snapshots/2026-11-17.json
    python3 scripts/bing-api.py snapshot --site pbzero \
        --compare reports/bing-snapshots/2026-11-17.json

--site 用短名（pbzero / e33 / morse）或完整域名。
API Key 读 .secrets/bing-api.txt（已在 .gitignore）。
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://ssl.bing.com/webmaster/api.svc/json/"

SITES = {
    "pbzero": "https://pbzero.wiki/",
    "e33": "https://expedition33.wiki/",
    "morse": "https://morsecodenow.com/",
}

FEED_URLS = {
    "pbzero": "https://pbzero.wiki/sitemap.xml",
    "e33": "https://expedition33.wiki/sitemap.xml",
    "morse": "https://morsecodenow.com/sitemap.xml",
}

# 快照要盯的目标词。改这些页面之后，它们的曝光/点击/位置是最直接的读数。
TARGET_QUERIES = [
    "phantom blade zero wiki",
    "phantom blade zero walkthrough",
    "phantom blade zero all bosses",
    "phantom blade zero bosses",
    "phantom blade zero boss order",
    "phantom blade zero map",
    "phantom blade zero all weapons",
    "phantom blade zero weapons",
    "phantom blade zero 66 days",
    "phantom blade zero best build",
    "phantom blade zero trophy guide",
    "phantom blade zero difficulty",
]


def api_key():
    p = ROOT / ".secrets" / "bing-api.txt"
    if not p.exists():
        sys.exit("缺 .secrets/bing-api.txt")
    return p.read_text().strip()


def site_url(name):
    return SITES.get(name, name)


def dotnet_date(v):
    """.NET JSON 日期 /Date(1789033042000)/ → 2026-09-08。零值返回 '-'。"""
    if not v:
        return "-"
    import re
    from datetime import datetime, timedelta
    m = re.search(r"/Date\((-?\d+)", str(v))
    if not m:
        return str(v)[:10]
    ms = int(m.group(1))
    if ms <= 0:
        return "-"
    return (datetime(1970, 1, 1) + timedelta(milliseconds=ms)).strftime("%Y-%m-%d")


def call(method, **params):
    q = {"apikey": api_key()}
    q.update({k: v for k, v in params.items() if v is not None})
    url = BASE + method + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "pbzero-seo/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        sys.exit(f"HTTP {e.code} on {method}\n{detail}")
    if not body.strip():
        return None
    data = json.loads(body)
    return data.get("d", data)


def cmd_sites(args):
    rows = call("GetUserSites") or []
    for s in rows:
        flag = "✅" if s.get("IsVerified") else "❌"
        print(f"{flag} {s['Url']}")
    print(f"\n共 {len(rows)} 个站点")


def cmd_feeds(args):
    rows = call("GetFeeds", siteUrl=site_url(args.site)) or []
    if not rows:
        print("⚠️  Bing 侧没有登记任何 sitemap —— 这就是「站点没有 sitemap」提示的来源")
        return
    for f in rows:
        print(f"  {f.get('Url')}\n    状态={f.get('Status')} "
              f"类型={f.get('Type') or '-'} 上次抓取={dotnet_date(f.get('LastCrawled'))}")


def cmd_traffic(args):
    rows = call("GetRankAndTrafficStats", siteUrl=site_url(args.site)) or []
    rows = [r for r in rows if r.get("Date")]
    rows.sort(key=lambda r: r["Date"])
    print(f"{'日期':<12}{'点击':>6}{'曝光':>8}")
    for r in rows[-30:]:
        print(f"{dotnet_date(r['Date']):<12}{r.get('Clicks', 0):>6}{r.get('Impressions', 0):>8}")
    tc = sum(r.get("Clicks", 0) for r in rows)
    ti = sum(r.get("Impressions", 0) for r in rows)
    print(f"\n合计 {len(rows)} 天：{tc} 点击 / {ti} 曝光")


def cmd_queries(args):
    params = {"siteUrl": site_url(args.site)}
    if args.start:
        params["startDate"] = args.start
    if args.end:
        params["endDate"] = args.end
    rows = call("GetQueryStats", **params) or []
    rows.sort(key=lambda r: -(r.get("Impressions") or 0))
    print(f"{'关键词':<48}{'曝光':>7}{'点击':>6}{'均位':>7}")
    for r in rows[: args.limit]:
        print(f"{(r.get('Query') or '')[:46]:<48}{r.get('Impressions', 0):>7}"
              f"{r.get('Clicks', 0):>6}{round(r.get('AvgImpressionPosition') or 0, 1):>7}")
    print(f"\n共 {len(rows)} 个 query")


def cmd_crawl(args):
    rows = call("GetCrawlStats", siteUrl=site_url(args.site)) or []
    rows = [r for r in rows if r.get("Date")]
    rows.sort(key=lambda r: r["Date"])
    for r in rows[-14:]:
        print(f"  {dotnet_date(r['Date'])}  抓取={r.get('CrawledPages', 0)}  "
              f"错误={r.get('CrawlErrors', 0)}  DNS={r.get('DnsErrors', 0)}")


def cmd_issues(args):
    rows = call("GetCrawlIssues", siteUrl=site_url(args.site)) or []
    if not rows:
        print("没有抓取错误")
        return
    for r in rows[:40]:
        print(f"  [{r.get('HttpCode')}] {(r.get('Url') or '')[:80]}\n"
              f"        {r.get('IssueType')} / {str(r.get('Details'))[:120]}")
    print(f"\n共 {len(rows)} 条")


def cmd_urlinfo(args):
    rows = call("GetUrlInfo", siteUrl=site_url(args.site), url=args.url)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def _agg(rows):
    return {
        "days": len(rows),
        "clicks": sum(r["clicks"] for r in rows),
        "impressions": sum(r["impressions"] for r in rows),
    }


def take_snapshot(site):
    """把当期 Bing 数字折成一个 dict，既能存盘也能直接比对。"""
    snap = {"site": site, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")}

    # sitemap 登记状态：这是 11-17 之前最大的坑，必须每次都看
    feeds = call("GetFeeds", siteUrl=site) or []
    snap["feeds"] = [
        {"url": f.get("Url"), "status": f.get("Status"),
         "last_crawled": dotnet_date(f.get("LastCrawled"))}
        for f in feeds
    ]

    traffic = [r for r in (call("GetRankAndTrafficStats", siteUrl=site) or []) if r.get("Date")]
    traffic.sort(key=lambda r: r["Date"])
    daily = [
        {"date": dotnet_date(r["Date"]), "clicks": r.get("Clicks", 0),
         "impressions": r.get("Impressions", 0)}
        for r in traffic
    ]
    snap["traffic_daily"] = daily
    snap["traffic_total"] = _agg(daily)
    snap["traffic_last7"] = _agg(daily[-7:])
    snap["traffic_prev7"] = _agg(daily[-14:-7])

    # 关键词：全量 + 目标词逐条
    rows = call("GetQueryStats", siteUrl=site) or []
    snap["query_count"] = len(rows)
    snap["query_impressions"] = sum(r.get("Impressions") or 0 for r in rows)
    snap["query_clicks"] = sum(r.get("Clicks") or 0 for r in rows)
    low = {(r.get("Query") or "").lower(): r for r in rows}

    targets = {}
    for kw in TARGET_QUERIES:
        r = low.get(kw)
        if r:
            targets[kw] = {
                "match": "exact",
                "query": r.get("Query"),
                "impressions": r.get("Impressions") or 0,
                "clicks": r.get("Clicks") or 0,
                "position": round(r.get("AvgImpressionPosition") or 0, 1),
            }
            continue
        # 精确命中不了时，记下包含该短语的最近候选，避免"没曝光"和"词形不同"混为一谈
        near = [q for q in low if kw in q]
        if near:
            near.sort(key=lambda q: -(low[q].get("Impressions") or 0))
            r = low[near[0]]
            targets[kw] = {
                "match": "substring",
                "query": r.get("Query"),
                "impressions": r.get("Impressions") or 0,
                "clicks": r.get("Clicks") or 0,
                "position": round(r.get("AvgImpressionPosition") or 0, 1),
            }
        else:
            targets[kw] = None
    snap["targets"] = targets

    crawl = [r for r in (call("GetCrawlStats", siteUrl=site) or []) if r.get("Date")]
    crawl.sort(key=lambda r: r["Date"])
    snap["crawl_last7"] = {
        "pages": sum(r.get("CrawledPages") or 0 for r in crawl[-7:]),
        "errors": sum(r.get("CrawlErrors") or 0 for r in crawl[-7:]),
    }
    snap["crawl_last_day"] = (
        {"date": dotnet_date(crawl[-1]["Date"]),
         "pages": crawl[-1].get("CrawledPages") or 0} if crawl else None
    )

    issues = call("GetCrawlIssues", siteUrl=site) or []
    snap["issue_count"] = len(issues)
    return snap


def _fmt(v, unit=""):
    return "—" if v is None else f"{v}{unit}"


def _delta(now, before):
    if now is None or before is None:
        return ""
    d = now - before
    if d == 0:
        return "  (=)"
    return f"  ({d:+g})"


def compare_snapshots(now, before):
    """把两次快照的差异打成人能看的一段。"""
    b = before.get("traffic_total", {})
    n = now.get("traffic_total", {})
    print(f"\n{'='*66}")
    print(f"对比基线 {before.get('generated_at')}  →  现在 {now.get('generated_at')}")
    print(f"{'='*66}")

    print("\n[窗口累计]")
    for k, label in (("impressions", "曝光"), ("clicks", "点击")):
        print(f"  {label}\t{b.get(k, 0)} → {n.get(k, 0)}"
              f"{_delta(n.get(k), b.get(k))}")
    b7, n7 = before.get("traffic_last7", {}), now.get("traffic_last7", {})
    print(f"  近 7 天曝光\t{b7.get('impressions', 0)} → {n7.get('impressions', 0)}"
          f"{_delta(n7.get('impressions'), b7.get('impressions'))}")
    print(f"  近 7 天点击\t{b7.get('clicks', 0)} → {n7.get('clicks', 0)}"
          f"{_delta(n7.get('clicks'), b7.get('clicks'))}")

    print("\n[词覆盖]  ← 判断「每页 1.1 个词」有没有松动的主指标")
    print(f"  query 总数\t{before.get('query_count', 0)} → {now.get('query_count', 0)}"
          f"{_delta(now.get('query_count'), before.get('query_count'))}")

    print("\n[目标词]")
    bt, nt = before.get("targets", {}), now.get("targets", {})
    print(f"  {'词':<46}{'曝光':>10}{'位置':>10}")
    for kw in TARGET_QUERIES:
        o, c = bt.get(kw), nt.get(kw)
        oi = o["impressions"] if o else 0
        ci = c["impressions"] if c else 0
        if not o and not c:
            print(f"  {kw[:44]:<46}{'—':>10}{'仍无曝光':>10}")
            continue
        pos = f"位 {c['position']}" if c else "—"
        flag = "  ← 新出现" if (c and not o) else ""
        print(f"  {kw[:44]:<46}{f'{oi} → {ci}':>10}{pos:>10}"
              f"{_delta(ci, oi) if o else ''}{flag}")

    print("\n[sitemap]")
    bm = {f["url"]: f for f in before.get("feeds", [])}
    for f in now.get("feeds", []):
        old = bm.get(f["url"], {})
        print(f"  {f['url']}\n    {old.get('status', '—')} → {f['status']}"
              f"  上次抓取 {old.get('last_crawled', '—')} → {f['last_crawled']}")

    bc, nc = before.get("crawl_last7", {}), now.get("crawl_last7", {})
    print("\n[抓取]")
    print(f"  近 7 天抓取页数\t{bc.get('pages', 0)} → {nc.get('pages', 0)}")
    print(f"  抓取错误数\t{before.get('issue_count', 0)} → {now.get('issue_count', 0)}")


def cmd_snapshot(args):
    site = site_url(args.site)
    snap = take_snapshot(site)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n")
        print(f"快照已写入 {out}")
    else:
        print(json.dumps(snap, ensure_ascii=False, indent=2))

    t = snap["traffic_total"]
    print(f"{site}：{t['days']} 天 {t['impressions']} 曝光 / {t['clicks']} 点击，"
          f"{snap['query_count']} 个 query")

    if args.compare:
        p = Path(args.compare)
        if not p.exists():
            print(f"\n⚠️  基线 {p} 不存在，无法比对。reports/ 在 .gitignore 里，"
                  f"换机器或清理过的目录会丢基线文件。", file=sys.stderr)
            return
        before = json.loads(p.read_text())
        compare_snapshots(snap, before)


def cmd_submit_feed(args):
    feed = FEED_URLS[args.site] if args.site in FEED_URLS else args.site
    post_json("SubmitFeed", {"siteUrl": site_url(args.site), "feedUrl": feed})
    print(f"已提交 sitemap: {feed}")


def post_json(method, payload):
    """Bing 的写接口要 POST + JSON body；GET 会返回 405。"""
    req = urllib.request.Request(
        BASE + method + "?apikey=" + api_key(),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.status


def cmd_submit_url(args):
    urls = [u if u.startswith("http") else site_url(args.site).rstrip("/") + "/" + u.lstrip("/")
            for u in args.urls.split(",")]
    payload = {"siteUrl": site_url(args.site), "urlList": urls}
    req = urllib.request.Request(
        BASE + "SubmitUrlbatch?apikey=" + api_key(),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        print(f"提交 {len(urls)} 条，HTTP {r.status}")
    for u in urls:
        print(f"  {u}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sites")

    for name in ("feeds", "traffic", "crawl", "issues"):
        p = sub.add_parser(name)
        p.add_argument("--site", required=True)

    p = sub.add_parser("queries")
    p.add_argument("--site", required=True)
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--limit", type=int, default=30)

    p = sub.add_parser("urlinfo")
    p.add_argument("--site", required=True)
    p.add_argument("--url", required=True)

    p = sub.add_parser("snapshot")
    p.add_argument("--site", required=True)
    p.add_argument("--out")
    p.add_argument("--compare")

    p = sub.add_parser("submit-feed")
    p.add_argument("--site", required=True)

    p = sub.add_parser("submit-url")
    p.add_argument("--site", required=True)
    p.add_argument("--urls", required=True)

    args = ap.parse_args()
    globals()["cmd_" + args.cmd.replace("-", "_")](args)


if __name__ == "__main__":
    main()
