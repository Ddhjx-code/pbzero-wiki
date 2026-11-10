#!/usr/bin/env python3
"""Push pbzero.wiki at the search engines that accept a direct nudge.

  python3 scripts/submit-index.py              # GSC sitemap + Bing IndexNow
  python3 scripts/submit-index.py --gsc        # only re-submit the sitemap
  python3 scripts/submit-index.py --indexnow   # only IndexNow
  python3 scripts/submit-index.py --dry-run

Two different mechanisms, often confused:

- Search Console has no "recrawl this URL" API for ordinary sites. What it
  does expose is a sitemap re-submission, which only tells Google the file
  changed. It is a nudge, not a priority signal.
- IndexNow is a push protocol: Bing, Yandex, Seznam and Naver fetch the URL
  almost immediately. Google does not participate.

IndexNow needs a key file at the site root named after the key, containing
the key. This repo keeps it in public/, so it is served at /<key>.txt.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rep", os.path.join(HERE, "ga-gsc-report.py"))
rep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rep)

HOST = "pbzero.wiki"
GSC_SITE = "sc-domain:pbzero.wiki"
SITEMAP = f"https://{HOST}/sitemap.xml"
ROOT = os.path.dirname(HERE)


def find_indexnow_key():
    """IndexNow key: 8-128 hex chars, file named after it, contents equal to it."""
    for path in glob.glob(os.path.join(ROOT, "public", "*.txt")):
        name = os.path.basename(path)[:-4]
        if not (8 <= len(name) <= 128 and all(c in "0123456789abcdef" for c in name.lower())):
            continue
        with open(path, encoding="utf-8") as fh:
            body = fh.read().strip()
        if body == name:
            return name
    return None


def resubmit_sitemap(token):
    site = urllib.parse.quote(GSC_SITE, safe="")
    feed = urllib.parse.quote(SITEMAP, safe="")
    url = f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
    req = urllib.request.Request(
        url, data=b"", method="PUT", headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status


def sitemap_state(token):
    site = urllib.parse.quote(GSC_SITE, safe="")
    data = rep.http_json(f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps", token)
    for entry in data.get("sitemap", []):
        if entry.get("path") == SITEMAP:
            return entry
    return {}


def submit_indexnow(key, urls, dry_run=False):
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": urls,
    }
    if dry_run:
        print(f"[dry-run] IndexNow 将提交 {len(urls)} 条 URL 到 api.indexnow.org")
        print(f"[dry-run] keyLocation = {payload['keyLocation']}")
        return None
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return f"HTTP {exc.code}: {exc.read().decode(errors='replace')[:300]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gsc", action="store_true")
    ap.add_argument("--indexnow", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    do_gsc = args.gsc or not args.indexnow
    do_indexnow = args.indexnow or not args.gsc

    if not os.path.exists(rep.SA_PATH):
        raise SystemExit(f"missing service-account key: {rep.SA_PATH}")
    with open(rep.SA_PATH, encoding="utf-8") as fh:
        sa = json.load(fh)

    # writing a sitemap needs the non-readonly webmasters scope
    rep.SCOPES = "https://www.googleapis.com/auth/webmasters"
    token = rep.access_token(sa)

    if do_gsc:
        before = sitemap_state(token).get("lastSubmitted")
        try:
            status = resubmit_sitemap(token)
            print(f"GSC sitemap 重新提交: HTTP {status}（提交前 lastSubmitted = {before}）")
        except urllib.error.HTTPError as exc:
            print(f"GSC sitemap 提交失败: HTTP {exc.code} {exc.read().decode()[:200]}")
        except Exception as exc:
            print(f"GSC sitemap 提交失败: {type(exc).__name__} {str(exc)[:150]}")
        after = sitemap_state(token)
        print(f"  提交后 lastSubmitted = {after.get('lastSubmitted')}")
        print(f"  最近抓取          = {after.get('lastDownloaded')}")
        print(f"  warnings/errors   = {after.get('warnings')}/{after.get('errors')}")

    if do_indexnow:
        key = find_indexnow_key()
        if not key:
            raise SystemExit("public/ 下找不到合法的 IndexNow 密钥文件")
        urls = rep.sitemap_urls(GSC_SITE)
        if not urls:
            raise SystemExit("取不到 URL 清单（sitemap 与本地页面清单都失败）")
        print(f"IndexNow: key={key}, {len(urls)} 条 URL")
        status = submit_indexnow(key, urls, args.dry_run)
        if status is not None:
            print(f"  api.indexnow.org 返回: {status}")
            if status in (200, 202):
                print("  已接受（Bing / Yandex / Seznam / Naver 会各自来抓）")
            elif status == 403:
                print("  密钥校验失败：检查 /%s.txt 是否可访问且内容一致" % key)
            elif status == 422:
                print("  URL 不属于该 host，或格式不合法")
            elif status == 429:
                print("  提交过于频繁，稍后重试")


if __name__ == "__main__":
    main()
