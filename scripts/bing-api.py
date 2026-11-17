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

--site 用短名（pbzero / e33 / morse）或完整域名。
API Key 读 .secrets/bing-api.txt（已在 .gitignore）。
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
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

    p = sub.add_parser("submit-feed")
    p.add_argument("--site", required=True)

    p = sub.add_parser("submit-url")
    p.add_argument("--site", required=True)
    p.add_argument("--urls", required=True)

    args = ap.parse_args()
    globals()["cmd_" + args.cmd.replace("-", "_")](args)


if __name__ == "__main__":
    main()
