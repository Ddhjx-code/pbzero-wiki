#!/usr/bin/env python3
"""Pull real monthly search volume for a keyword list from Bing Webmaster Tools.

Why this source: Google Keyword Planner and Google Trends both require an
authenticated browser session, and Trends additionally rate-limits (HTTP 429)
any datacenter IP. Bing Webmaster's keyword research endpoint is the only
free, official source that returns absolute monthly volume over plain HTTP.

Setup (one minute, no cost):
  1. https://www.bing.com/webmasters -> sign in with the account that owns
     pbzero.wiki (the site is already receiving Bing traffic, so it is
     registered there).
  2. Settings -> API access -> API key -> generate.
  3. Save it to .secrets/bwt-key.txt  (that directory is gitignored).

Usage:
  python3 scripts/keyword-volume.py                      # default list
  python3 scripts/keyword-volume.py "phantom blade zero" "pbzero wiki"
  python3 scripts/keyword-volume.py --file keywords.txt  # one per line
  python3 scripts/keyword-volume.py --country gb         # default us
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".secrets", "bwt-key.txt")
KEY_PATH = os.path.abspath(KEY_PATH)
API = "https://ssl.bing.com/webmaster/api.svc/json/GetKeywordStats"

DEFAULTS = [
    "phantom blade zero",
    "phantom blade zero wiki",
    "phantom blade zero boss list",
    "phantom blade zero bosses in order",
    "phantom blade zero weapon tier list",
    "phantom blade zero weapons",
    "phantom blade zero best weapons",
    "phantom blade zero endings",
    "phantom blade zero how many endings",
    "phantom blade zero true ending",
    "phantom blade zero walkthrough",
    "phantom blade zero trophy guide",
    "phantom blade zero new game plus",
    "phantom blade zero bosses ranked",
    "phantom blade zero review",
    "phantom blade zero release date",
]


def api_key():
    if os.environ.get("BWT_KEY"):
        return os.environ["BWT_KEY"].strip()
    if os.path.exists(KEY_PATH):
        return open(KEY_PATH, encoding="utf-8").read().strip()
    raise SystemExit(
        f"missing API key: put it in {KEY_PATH}\n"
        "Bing Webmaster Tools -> Settings -> API access -> API key"
    )


def stats(key, keyword, country="us", language="en"):
    params = urllib.parse.urlencode({
        "q": keyword, "country": country, "language": language, "apikey": key,
    })
    req = urllib.request.Request(f"{API}?{params}", headers={"Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:200]
            if exc.code == 400 and "InvalidApiKey" in body:
                raise SystemExit("API key rejected (InvalidApiKey) - regenerate it in BWT")
            if attempt == 2:
                raise SystemExit(f"HTTP {exc.code} for '{keyword}': {body}")
        except Exception:
            if attempt == 2:
                return None
        time.sleep(2)
    return None


def pick(entry, *names):
    """Bing returns PascalCase keys; be tolerant about which ones exist."""
    for n in names:
        for k in (n, n.lower(), n[0].lower() + n[1:]):
            if k in entry:
                return entry[k]
    return ""


def main():
    args = sys.argv[1:]
    country = "us"
    words = []
    if "--country" in args:
        i = args.index("--country")
        country = args[i + 1]
        del args[i:i + 2]
    if "--file" in args:
        i = args.index("--file")
        words = [w.strip() for w in open(args[i + 1], encoding="utf-8") if w.strip()]
        del args[i:i + 2]
    words += [a for a in args if not a.startswith("-")]
    if not words:
        words = DEFAULTS

    key = api_key()
    rows = []
    for w in words:
        data = stats(key, w, country)
        entries = (data or {}).get("d") or []
        if not entries:
            rows.append([w, "-", "-", "-", "-"])
            print(f"  {w} - no data", file=sys.stderr)
            continue
        e = entries[0]
        rows.append([
            w,
            pick(e, "Nq", "SearchVolume", "Volume"),
            pick(e, "BroadImpression", "Impressions"),
            pick(e, "Cpc", "CPC"),
            pick(e, "Competition"),
        ])
        time.sleep(0.4)

    hdr = ["keyword", "monthly volume", "broad impressions", "cpc", "competition"]
    widths = [max(len(str(r[i])) for r in [hdr] + rows) for i in range(len(hdr))]
    line = "  ".join(str(h[i]).ljust(widths[i]) for i in range(len(h)))
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(str(r[i]).ljust(widths[i]) for i in range(len(hdr))))

    out = os.path.join(os.path.dirname(__file__), "..", "reports", f"keyword-volume-{country}.csv")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(",".join(hdr) + "\n")
        for r in rows:
            fh.write(",".join('"%s"' % str(c).replace('"', "'") for c in r) + "\n")
    print(f"\nCSV -> {out}")


if __name__ == "__main__":
    main()
