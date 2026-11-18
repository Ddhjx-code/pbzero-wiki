#!/usr/bin/env python3
"""逐 URL 检查 Bing 是否知道、是否抓过。

和 `site:` 查询不同，这里用的是 Webmaster 的 GetUrlInfo，返回的是索引系统的
真实记录：DiscoveryDate（Bing 第一次知道这个 URL）和 LastCrawledDate（最后一次
抓取）。两个都是 .NET 零值就说明 Bing 完全不知道这页存在。

用法:
    python3 scripts/bing-index-coverage.py --site pbzero
    python3 scripts/bing-index-coverage.py --site pbzero --limit 30   # 先摸 30 条
    python3 scripts/bing-index-coverage.py --site pbzero --no-save

接口有 IP 级节流（HTTP 400 ThrottleHost），所以每条之间默认 sleep 1.2s，
遇到节流指数退避重试。
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import importlib.util

_spec = importlib.util.spec_from_file_location("bing", ROOT / "scripts" / "bing-api.py")
bing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bing)


def parse_dotnet(v):
    """返回 (kind, str)。kind ∈ crawled / discovered / unknown。"""
    m = re.search(r"/Date\((-?\d+)", str(v))
    if not m:
        return "unknown", None
    ms = int(m.group(1))
    if ms <= 0:
        return "unknown", None
    return "ok", datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")


def sitemap_urls(site_url):
    """优先读线上 sitemap；Vercel 会拦默认的 Python UA，所以带自定义 UA，
    失败时回退到本地构建产物 out/sitemap.xml。"""
    url = site_url.rstrip("/") + "/sitemap.xml"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pbzero-seo/1.0"})
        with urllib.request.urlopen(req, timeout=45) as r:
            xml = r.read().decode("utf-8", "replace")
    except Exception as e:
        local = ROOT / "out" / "sitemap.xml"
        if not local.exists():
            sys.exit(f"取 sitemap 失败（{e}），本地也没有 {local}")
        print(f"⚠️  线上 sitemap 取不到（{e}），改用本地 out/sitemap.xml\n")
        xml = local.read_text()
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def urlinfo(site_url, page_url, retries=4):
    for attempt in range(retries):
        try:
            d = bing.call("GetUrlInfo", siteUrl=site_url, url=page_url)
            return d if isinstance(d, dict) else {}
        except SystemExit as e:
            if "ThrottleHost" in str(e) and attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
                continue
            return {"__error": str(e)[:120]}
    return {"__error": "retries exhausted"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--delay", type=float, default=1.2)
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args()

    site = bing.site_url(args.site)
    urls = sitemap_urls(site)
    if args.limit:
        urls = urls[: args.limit]
    print(f"{site}：sitemap {len(urls)} 条，逐条查 Bing 索引状态（约 {len(urls) * (args.delay + 0.3) / 60:.1f} 分钟）\n")

    rows = []
    for i, u in enumerate(urls, 1):
        d = urlinfo(site, u)
        if "__error" in d:
            rows.append({"url": u, "state": "error", "error": d["__error"]})
            print(f"  [{i}/{len(urls)}] {u}  ⚠️ {d['__error']}", flush=True)
            continue
        _, disc = parse_dotnet(d.get("DiscoveryDate"))
        _, crawl = parse_dotnet(d.get("LastCrawledDate"))
        state = "crawled" if crawl else ("discovered" if disc else "unknown")
        rows.append({
            "url": u, "state": state,
            "discovered": disc, "last_crawled": crawl,
            "size": d.get("DocumentSize", 0),
        })
        if state != "crawled":
            print(f"  [{i}/{len(urls)}] {u}  {'👁 已知未抓' if disc else '❌ 未知'}", flush=True)
        time.sleep(args.delay)

    counts = Counter(r["state"] for r in rows)
    total = len(rows)
    print(f"\n{'='*56}")
    print(f"Bing 认知覆盖：{site}")
    print(f"{'='*56}")
    print(f"  已抓取   {counts.get('crawled', 0):>4} / {total}  "
          f"{counts.get('crawled', 0) / total:.0%}")
    print(f"  已知未抓 {counts.get('discovered', 0):>4} / {total}  "
          f"{counts.get('discovered', 0) / total:.0%}")
    print(f"  完全未知 {counts.get('unknown', 0):>4} / {total}  "
          f"{counts.get('unknown', 0) / total:.0%}")
    if counts.get("error"):
        print(f"  查询失败 {counts['error']:>4}")

    crawled = [r for r in rows if r["state"] == "crawled"]
    if crawled:
        crawled.sort(key=lambda r: r["last_crawled"], reverse=True)
        print("\n最近抓取的 8 条：")
        for r in crawled[:8]:
            print(f"  {r['last_crawled']}  {r['size']:>7}B  {r['url'].replace('https://', '')}")

    unknown = [r["url"] for r in rows if r["state"] == "unknown"]
    if unknown:
        print(f"\nBing 完全不知道的页面（{len(unknown)} 条，前 15）：")
        for u in unknown[:15]:
            print(f"  {u.replace('https://' + site.split('//')[1].rstrip('/'), '')}")

    if not args.no_save:
        out = ROOT / "reports" / "bing-snapshots" / f"index-coverage-{datetime.now():%Y-%m-%d}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "site": site,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "counts": dict(counts),
            "total": total,
            "rows": rows,
        }, ensure_ascii=False, indent=2) + "\n")
        print(f"\n明细已存 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
