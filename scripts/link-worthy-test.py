#!/usr/bin/env python3
"""外链词测试：一个题目到底有没有"被人引用"的价值。

方法出自 Authority Hacker 课程第 8 步（52出海 有编译版）：把候选词的前 10 名
拿出来，累加引荐域名（RD）。总和 > 100 说明这个题目上大家普遍互相引用，值得
投入；总和很低，说明写得再好也只是自己排着，没人会链。

两种用法：

  1) 直接查一组 URL（可靠，推荐）
       python3 scripts/link-worthy-test.py --targets https://a.com/x https://b.com/y

  2) 按关键词跑整个流程（SERP → 前 10 → 累加 RD）
       python3 scripts/link-worthy-test.py --topics "phantom blade zero bosses"

注意：Google SERP 接口有时返回 google.com/goto?url=... 的跳转壳，真实地址在
breadcrumb 里，拿不到完整路径就没法查 RD。遇到这种情况改用 --targets。

单次 backlinks/summary 约 $0.02，SERP 约 $0.002；脚本会先打印将要查询的条数。
"""
import argparse
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.dataforseo.com"


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
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def summary(target):
    """backlinks/summary 一次只接受一个 task，所以逐个查。"""
    res = call("/v3/backlinks/summary/live", [{"target": target, "internal_list_limit": 1}])
    task = res["tasks"][0]
    if task.get("status_code") != 20000:
        return None, task.get("status_message")
    r0 = (task.get("result") or [{}])[0]
    return {"rd": r0.get("referring_domains") or 0, "bl": r0.get("backlinks") or 0}, None


def serp_top(keyword, engine="google", depth=10):
    res = call(f"/v3/serp/{engine}/organic/live/advanced", [{
        "keyword": keyword,
        "location_name": "United States",
        "language_code": "en",
        "depth": depth,
    }])
    task = res["tasks"][0]
    if task.get("status_code") != 20000:
        return None, task.get("status_message")
    items = (task.get("result") or [{}])[0].get("items") or []
    urls = [i["url"] for i in items if i.get("type") == "organic" and i.get("url")]
    return urls[:depth], None


def show(targets):
    print(f"将查询 {len(targets)} 个 target，约 ${len(targets) * 0.02:.2f}\n")
    total = 0
    rows = []
    for t in targets:
        d, err = summary(t)
        if err:
            print(f"{'?':>6}  {t[:80]}  {err}")
            continue
        total += d["rd"]
        rows.append((d["rd"], d["bl"], t))
        time.sleep(0.3)
    for rd, bl, t in sorted(rows, reverse=True):
        print(f"{rd:6d} RD {bl:6d} BL  {t[:80]}")
    print(f"\n合计引荐域名 {total}")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", nargs="*")
    ap.add_argument("--topics", nargs="*")
    ap.add_argument("--engine", default="google", choices=["google", "bing"])
    ap.add_argument("--depth", type=int, default=10)
    ap.add_argument("--threshold", type=int, default=100)
    a = ap.parse_args()

    if a.targets:
        show(a.targets)
        return

    if not a.topics:
        sys.exit("给 --targets 或 --topics，例如 --topics \"phantom blade zero bosses\"")

    for kw in a.topics:
        urls, err = serp_top(kw, a.engine, a.depth)
        if err:
            print(f"\n## {kw}\n  SERP 失败: {err}")
            continue
        if any("/goto?url=" in u or u.startswith("https://google.com/") for u in urls):
            print(f"\n## {kw}\n  SERP 返回的是跳转壳，拿不到真实地址；改用 --targets。")
            continue
        print(f"\n## {kw}")
        total = show(urls)
        print(f"  → {'值得做' if total > a.threshold else '不值得'}（门槛 {a.threshold}）")


if __name__ == "__main__":
    main()
