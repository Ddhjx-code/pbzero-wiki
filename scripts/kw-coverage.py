#!/usr/bin/env python3
"""关键词覆盖审计：目标词在 187 个页面里的落位情况。

为什么要这个：Bing 侧实测 pbzero 每页只覆盖 1.1 个 query（e33 是 5.8），
但标题/正文里到底缺哪些词，靠眼睛看不出来。

用法:
    python3 scripts/kw-coverage.py              # 全部目标词
    python3 scripts/kw-coverage.py --kw walkthrough
    python3 scripts/kw-coverage.py --gaps       # 只显示覆盖不足的
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "data" / "pages"

# 目标词 → Google Ads 10 月 US 月量
TARGETS = {
    "walkthrough": 1600,
    "wiki": 1300,
    "bosses": 1300,
    "map": 1000,
    "all bosses": 480,
    "66 days": 480,
    "endings": 210,
    "boss order": 170,
    "true ending": 140,
    "best build": 110,
    # Bing 后台实际产生过曝光的词，同等重要
    "all weapons": 0,
    "weapon list": 0,
    "characters": 0,
    "builds": 0,
    "zuo shang": 0,
    "boss list": 0,
    "trophy": 0,
}

# 首页在这一组里挑词，不参与"某页没覆盖"的判定
BRAND = "phantom blade zero"


def load_pages():
    out = {}
    for p in sorted(PAGES.glob("*.json")):
        try:
            d = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        body = " ".join(s.get("content", "") for s in d.get("sections", []))
        facts = " ".join(f"{f.get('label','')} {f.get('value','')}" for f in d.get("facts", []))
        out[p.stem] = {
            "slug": d.get("slug", p.stem),
            "title": d.get("title", ""),
            "desc": d.get("description", ""),
            "body": body + " " + facts,
            "words": len((body + " " + facts).split()),
        }
    return out


def count(hay, phrase):
    """整词计数，避免 'map' 命中 'mapping' 之类。"""
    return len(re.findall(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", hay.lower()))


def audit(pages, only=None):
    rows = []
    for kw, vol in TARGETS.items():
        if only and kw != only:
            continue
        full = f"{BRAND} {kw}"
        in_title, in_desc, in_body = [], [], []
        for slug, p in pages.items():
            if count(p["title"], full) or count(p["title"], kw):
                in_title.append(slug)
            if count(p["desc"], full) or count(p["desc"], kw):
                in_desc.append(slug)
            n = count(p["body"], full) + count(p["body"], kw)
            if n:
                in_body.append((slug, n))
        in_body.sort(key=lambda x: -x[1])
        rows.append({
            "kw": kw, "vol": vol,
            "title": in_title, "desc": in_desc,
            "body": in_body,
            "total_hits": sum(n for _, n in in_body),
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kw")
    ap.add_argument("--gaps", action="store_true")
    args = ap.parse_args()

    pages = load_pages()
    rows = audit(pages, args.kw)

    print(f"共 {len(pages)} 个页面，正文平均 {sum(p['words'] for p in pages.values())//len(pages)} 词\n")

    for r in sorted(rows, key=lambda x: -x["vol"]):
        weak = r["total_hits"] < 5 or not r["title"]
        if args.gaps and not weak:
            continue
        flag = "⚠️ " if weak else "✅ "
        print(f"{flag}{r['kw']:<16} 月量{r['vol']:>5}  正文命中{r['total_hits']:>4}  "
              f"标题({len(r['title'])}) 描述({len(r['desc'])})")
        if r["title"]:
            print(f"     标题含此词: {', '.join('/' + s for s in r['title'][:6])}")
        if r["body"]:
            top = ", ".join(f"/{s}×{n}" for s, n in r["body"][:5])
            print(f"     正文分布: {top}")
        if weak and not r["body"]:
            print("     ❗ 全站正文零出现")


if __name__ == "__main__":
    main()
