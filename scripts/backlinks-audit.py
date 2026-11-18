#!/usr/bin/env python3
"""外链反查：自家站 + 竞品的引荐域名，按权威度排序。

为什么需要这个：判断"某人/某站有外链优势"时，看 referal domain 的**数量**会
被骗。2026-11-18 查 pbzero 时发现，e33 的 53 个引荐域名里 50 个是 rank=0 的
垃圾（短链站、博彩站、seolinkagency.shop 之类），而同一个网络也在打我们所有
站。数量好看，质量为零。

DataForSEO 的 rank 是 0–1000 量表，0 = 无权威度。判断一个引荐域名值不值得看：
  rank >= 50                 可能有价值
  rank 0 且域名像短链/博彩/SEO 服务  垃圾网络
  一个域名给同一目标贡献几十条正文内链  真编辑关系（重点看这个）

用法:
    python3 scripts/backlinks-audit.py                 # 默认：自家三站
    python3 scripts/backlinks-audit.py --with-rivals   # 加上竞品
    python3 scripts/backlinks-audit.py --target example.com
    python3 scripts/backlinks-audit.py --detail expedition33.wiki   # 看锚文本明细
"""
import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.dataforseo.com"

OWN = ["pbzero.wiki", "expedition33.wiki", "morsecodenow.com"]
RIVALS = [
    "phantombladeatlas.com",
    "bladezero.org",
    "phantom-blade-zero.org",
    "phantombladezero-guide.com",
    "metabot.gg",
]

JUNK_HINTS = (
    "shortener", "shortenurl", "seolink", "backlink", "seo-", "-seo", "seonix",
    "rank-", "rankvance", "bet", "casino", "slot", "ufabet", "poker", "link",
    "backlinks", "traffic", "guestpost",
)


def auth_header():
    p = ROOT / ".secrets" / "dfs-auth.txt"
    if not p.exists():
        sys.exit("缺 .secrets/dfs-auth.txt（内容 login:password）")
    return "Basic " + base64.b64encode(p.read_text().strip().encode()).decode()


def call(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Authorization": auth_header(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def looks_junk(domain):
    d = domain.lower()
    return any(h in d for h in JUNK_HINTS)


def refdomains(target, limit=60):
    res = call("/v3/backlinks/referring_domains/live",
               [{"target": target, "limit": limit, "order_by": ["rank,desc"]}])
    task = res["tasks"][0]
    if task.get("status_code") != 20000:
        return None, task.get("status_message")
    r0 = task["result"][0]
    return (r0.get("total_count"), r0.get("items") or []), None


def anchor_detail(target, limit=12):
    res = call("/v3/backlinks/backlinks/live",
               [{"target": target, "limit": limit, "mode": "as_is", "order_by": ["rank,desc"]}])
    task = res["tasks"][0]
    if task.get("status_code") != 20000:
        return []
    return task["result"][0].get("items") or []


def report(target):
    data, err = refdomains(target)
    if err:
        print(f"\n=== {target} === {err}")
        return
    total, items = data
    real = [i for i in items if (i.get("rank") or 0) >= 50]
    junk = [i for i in items if looks_junk(i.get("domain", ""))]
    print(f"\n=== {target} ===")
    print(f"  引荐域名 {total} 个（本次取前 {len(items)}）  "
          f"rank>=50 的 {len(real)} 个  疑似垃圾网络 {len(junk)} 个")
    for it in items[:15]:
        flag = "★" if (it.get("rank") or 0) >= 50 else ("×" if looks_junk(it.get("domain", "")) else " ")
        print(f"  {flag} {it.get('domain','')[:38]:<40} rank={it.get('rank') or 0:<5} "
              f"links={it.get('backlinks') or 0:<5} 首见={(it.get('first_seen') or '')[:10]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-rivals", action="store_true")
    ap.add_argument("--target", action="append")
    ap.add_argument("--detail")
    args = ap.parse_args()

    targets = args.target or (OWN + RIVALS if args.with_rivals else OWN)
    for t in targets:
        report(t)

    if args.detail:
        print(f"\n=== {args.detail} 锚文本明细 ===")
        for it in anchor_detail(args.detail):
            print(f"  来源 {it.get('domain_from','')[:34]}")
            print(f"    页面 {(it.get('url_from') or '')[:76]}")
            print(f"    anchor=\"{it.get('anchor')}\"  dofollow={it.get('dofollow')}  "
                  f"目标={(it.get('url_to') or '')[:52]}")


if __name__ == "__main__":
    main()
