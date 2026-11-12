#!/usr/bin/env python3
"""
查关键词的 12 个月搜索量明细 —— 用来判断"月均值被摊平"。

Google Ads 的 search_volume 字段是**过去 12 个月的平均值**。刚上线的游戏，
上线当月的爆发会被前 11 个月的冷启动摊薄，平均下来可能只有真实峰值的 1/10。
这个脚本把 monthly_searches 明细打出来，看趋势到底长什么样。

用法:
  python3 scripts/dfs-trend.py "phantom blade zero" "phantom blade zero release date"
  python3 scripts/dfs-trend.py --from-csv reports/dfs-pbz-2026-11-11.csv --top 15
  python3 scripts/dfs-trend.py --location 2826 "phantom blade zero"   # 英国

计费: 一次请求 $0.09（最多 1000 个词，live）
"""
import argparse
import base64
import csv
import json
import os
import sys
import urllib.request

BASE = "https://api.dataforseo.com"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROXY = os.environ.get("DFS_PROXY", "").strip()


def auth_header():
    p = os.path.join(ROOT, ".secrets", "dfs-auth.txt")
    login, pw = open(p).read().strip().split(":", 1)
    return "Basic " + base64.b64encode(f"{login}:{pw}".encode()).decode()


def post(path, payload):
    handlers = ([urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})]
                if PROXY else [])
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={"Authorization": auth_header(),
                 "Content-Type": "application/json",
                 # 不带 identity 会被 gzip 卡死，本项目踩过两次
                 "Accept-Encoding": "identity"},
        method="POST")
    opener = urllib.request.build_opener(*handlers)
    with opener.open(req, timeout=120) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords", nargs="*")
    ap.add_argument("--from-csv", default=None)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--location", type=int, default=2840, help="2840=US 2826=UK")
    args = ap.parse_args()

    kws = list(args.keywords)
    if args.from_csv:
        rows = list(csv.DictReader(open(args.from_csv)))
        rows = [r for r in rows if r["volume"].isdigit() and int(r["volume"]) > 0]
        rows.sort(key=lambda r: -int(r["volume"]))
        kws += [r["keyword"] for r in rows[:args.top]]
    kws = list(dict.fromkeys(k for k in kws if k))
    if not kws:
        sys.exit("没有关键词")

    task = {"keywords": kws[:1000], "location_code": args.location,
            "language_code": "en", "search_partners": False}
    resp = post("/v3/keywords_data/google_ads/search_volume/live", [task])
    print(f"花费 ${resp.get('cost')}｜{len(kws)} 个词", file=sys.stderr)

    for t in resp.get("tasks", []):
        for item in (t.get("result") or []):
            kw = item.get("keyword")
            avg = item.get("search_volume")
            ms = [m for m in (item.get("monthly_searches") or [])]
            ms.sort(key=lambda m: (m["year"], m["month"]))
            series = [m["search_volume"] or 0 for m in ms]
            peak = max(series) if series else 0
            last = series[-1] if series else 0
            print(f"\n{kw}")
            print(f"  12 个月平均 {avg}｜最近一月 {last}｜峰值 {peak}"
                  f"｜峰值/均值 {peak / avg:.1f}x" if avg else "")
            if ms:
                labels = [f"{m['year']}-{m['month']:02d}" for m in ms]
                print("  " + "  ".join(f"{l}:{v}" for l, v in zip(labels, series)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
