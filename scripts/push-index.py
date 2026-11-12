#!/usr/bin/env python3
"""Nudge the crawlers for any of the three sites from one command.

    python3 scripts/push-index.py --dry-run                    # 看一下要推什么
    python3 scripts/push-index.py --mode indexnow --paths /patch-notes
    python3 scripts/push-index.py --mode sitemap --host all
    python3 scripts/push-index.py                              # 三个站：sitemap + 整站 IndexNow

Two mechanisms, different engines:

- GSC sitemap re-submission is a PUT against the Webmasters API. Google does not
  offer a per-URL priority push for ordinary sites, so this only tells Google the
  file changed. It is a nudge, not a crawl order.
- IndexNow is a real push: Bing, Yandex, Seznam and Naver fetch the listed URLs
  almost immediately. Google does not participate.

Why all three sites live here: they share one service account and one IndexNow
key (2f630f456deb4989a6cda8422a24aace.txt, identical in each public/), so there
is no reason to keep three copies of the same logic in sync.

URLs are read from the live sitemap, never from the local page list, because the
whole point is to push URLs that already exist on the origin. A URL that 404s
teaches IndexNow to distrust the key.
"""
import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rep", os.path.join(HERE, "ga-gsc-report.py"))
rep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rep)

HOSTS = {
    "pbzero": "pbzero.wiki",
    "e33": "expedition33.wiki",
    "morse": "morsecodenow.com",
}
KEY_FILE = "2f630f456deb4989a6cda8422a24aace"

# GSC property string per host. Default is the domain property; anything listed
# here overrides it.
PROPERTY = {
    "expedition33.wiki": "https://expedition33.wiki/",
}


def live_urls(host, timeout=30):
    """Pull <loc> entries out of the live sitemap. Empty list on any failure."""
    req = urllib.request.Request(
        f"https://{host}/sitemap.xml",
        headers={"User-Agent": "Mozilla/5.0 (compatible; site-ops/1.0)", "Accept-Encoding": "identity"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        print(f"  读取 https://{host}/sitemap.xml 失败: {type(exc).__name__} {str(exc)[:120]}")
        return []
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)


def resubmit_sitemap(host, token):
    # Not every site is a domain property. expedition33.wiki only exists in GSC as
    # a URL-prefix property, and PUT against sc-domain:expedition33.wiki returns 403
    # because the service account was never granted that property.
    site = urllib.parse.quote(PROPERTY.get(host, f"sc-domain:{host}"), safe="")
    feed = urllib.parse.quote(f"https://{host}/sitemap.xml", safe="")
    req = urllib.request.Request(
        f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}",
        data=b"",
        method="PUT",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        return f"HTTP {exc.code} {exc.read().decode(errors='replace')[:160]}"
    except Exception as exc:
        return f"{type(exc).__name__} {str(exc)[:120]}"


def indexnow(host, urls, dry_run=False):
    payload = {
        "host": host,
        "key": KEY_FILE,
        "keyLocation": f"https://{host}/{KEY_FILE}.txt",
        "urlList": urls,
    }
    if dry_run:
        return f"[dry-run] {len(urls)} 条 URL"
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        return f"HTTP {exc.code} {exc.read().decode(errors='replace')[:200]}"
    except Exception as exc:
        return f"{type(exc).__name__} {str(exc)[:120]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="all", help="pbzero | e33 | morse | all")
    ap.add_argument("--mode", default="both", choices=["sitemap", "indexnow", "both"])
    ap.add_argument("--paths", nargs="*", default=None,
                    help="只推这些路径，例如 /patch-notes /missables；默认推整站")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = list(HOSTS.items()) if args.host == "all" else [(args.host, HOSTS[args.host])]

    token = None
    if args.mode in ("sitemap", "both") and not args.dry_run:
        with open(rep.SA_PATH, encoding="utf-8") as fh:
            sa = json.load(fh)
        rep.SCOPES = "https://www.googleapis.com/auth/webmasters"
        token = rep.access_token(sa)

    for nick, host in targets:
        print(f"\n=== {nick}  {host} ===")
        urls = live_urls(host)
        if not urls:
            print("  线上 sitemap 拿不到 URL，先确认部署完成。跳过 IndexNow。")
        elif args.paths:
            wanted = {f"https://{host}{p if p.startswith('/') else '/' + p}" for p in args.paths}
            urls = [u for u in urls if u in wanted]
            missing = wanted - set(urls)
            if missing:
                print(f"  ⚠ 线上 sitemap 里没有: {', '.join(sorted(missing))}（还没部署？）")
        print(f"  线上 URL {len(urls)} 条")

        if args.mode in ("sitemap", "both"):
            if args.dry_run:
                print(f"  [dry-run] GSC sitemap 重新提交 sc-domain:{host}")
            else:
                print(f"  GSC sitemap 重新提交: {resubmit_sitemap(host, token)}")

        if args.mode in ("indexnow", "both") and urls:
            if len(urls) > 10000:
                urls = urls[:10000]
                print("  超出 1 万条上限，已截断")
            print(f"  IndexNow: {indexnow(host, urls, args.dry_run)}")


if __name__ == "__main__":
    sys.exit(main())
