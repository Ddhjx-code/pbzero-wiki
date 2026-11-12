#!/usr/bin/env python3
"""三站的 GSC 收录状况：站点地图状态 + 逐 URL 检查（URL Inspection API）。

为什么不用 GSC 后台的"已编入索引"数字：那个是旧版覆盖率报告的口径，早就
停止更新了。唯一可信的是 URL Inspection API 的 coverageState，它直接告诉你
Google 现在把这条 URL 当什么。

用法:
  python3 scripts/gsc-index-status.py                # 每站抽 25 条
  python3 scripts/gsc-index-status.py --sample 60    # 每站抽 60 条

配额: URL Inspection 每站点每天 2000 次，60×3 远够。
"""
import argparse
import datetime as dt
import importlib.util
import json
import os
import random
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "rep", os.path.join(HERE, "ga-gsc-report.py"))
rep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rep)

ROOT = os.path.dirname(HERE)
PROPS = {
    "pbzero.wiki": "sc-domain:pbzero.wiki",
    # e33 是「网址前缀」资源，不是域资源，写错会 403（服务账号是 siteFullUser 也没用）
    "expedition33.wiki": "https://expedition33.wiki/",
    "morsecodenow.com": "sc-domain:morsecodenow.com",
}
API = "https://www.googleapis.com/webmasters/v3"


def sitemaps(token, site):
    enc = urllib.parse.quote(site, safe="")
    try:
        resp = rep.http_json(f"{API}/sites/{enc}/sitemaps", token)
    except RuntimeError as exc:
        return None, str(exc)
    return resp.get("sitemap") or [], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=25)
    args = ap.parse_args()

    if not os.path.exists(rep.SA_PATH):
        sys.exit(f"缺少服务账号密钥: {rep.SA_PATH}")
    token = rep.access_token(json.load(open(rep.SA_PATH)))

    lines = [f"# GSC 收录状况 — {dt.date.today()}", ""]
    for host, site in PROPS.items():
        print(f"→ {host}", file=sys.stderr)
        sms, err = sitemaps(token, site)
        lines.append(f"## {host}")
        lines.append("")
        if err:
            lines.append(f"- 站点地图接口报错：`{err[:120]}`（服务账号可能没有该资源权限）")
            lines.append("")
            continue

        if not sms:
            lines.append("- **没有任何已提交的站点地图**")
        for sm in sms:
            contents = sm.get("contents") or []
            submitted = sum(int(c.get("submitted") or 0) for c in contents)
            indexed = sum(int(c.get("indexed") or 0) for c in contents)
            lines.append(
                f"- `{sm.get('path')}`｜类型 {sm.get('type')}｜"
                f"提交 {submitted} 条 / 标记已索引 {indexed} 条｜"
                f"上次下载 {(sm.get('lastDownloaded') or '未下载')[:19]}｜"
                f"错误 {sm.get('errors')} 警告 {sm.get('warnings')}")
        lines.append("")

        urls = rep.sitemap_urls(site)
        lines.append(f"- 站点地图里能读到的 URL：**{len(urls)} 条**")
        if urls:
            random.seed(7)
            sample = urls if len(urls) <= args.sample else random.sample(
                urls, args.sample)
            rows = []
            for u in sample:
                rows.append(rep.index_audit(token, site, [u])[0])
                time.sleep(0.4)      # 别把配额和连接打满
            from collections import Counter
            cnt = Counter(r[1] for r in rows)
            lines.append(f"- 抽查 {len(rows)} 条，状态分布：")
            for state, n in cnt.most_common():
                lines.append(f"  - {state}: {n}")
            lines.append("")
            lines.append("| URL | 状态 | 最后抓取 |")
            lines.append("|---|---|---|")
            for u, state, crawled in sorted(rows, key=lambda r: r[1]):
                lines.append(f"| {u.replace('https://', '')} | {state} | {crawled or '—'} |")
        lines.append("")

    out = os.path.join(ROOT, "reports", f"gsc-index-status-{dt.date.today()}.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"写了 {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
