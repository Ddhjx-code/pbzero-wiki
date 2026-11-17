#!/usr/bin/env python3
"""Daily split of pbzero.wiki traffic by acquisition kind.

The KPI conversation moved from "Google organic" to "AI referrals + Bing", so
this pulls GA4 sessionSourceMedium by date and buckets it into AI / Bing /
Google / Direct / other, printing a per-day table plus 7-day halves.

Usage:
  python3 scripts/ai-bing-trend.py [days]
"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rep = load("rep", "ga-gsc-report.py")
allsites = load("allsites", "all-sites-report.py")

AI_TOKENS = ("chatgpt", "openai", "perplexity", "copilot", "gemini", "claude",
             "anthropic", "you.com", "poe.com", "deepseek", "grok", "phind")


def kind(src):
    s = src.lower()
    if any(t in s for t in AI_TOKENS):
        return "AI"
    if "bing" in s or "duckduckgo" in s:
        return "BingDDG"
    if "google" in s:
        return "Google"
    if s.startswith("(direct)") or s == "direct / (none)":
        return "Direct"
    return "Other"


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    host = sys.argv[2] if len(sys.argv) > 2 else "pbzero.wiki"
    allsites.pick_working_proxy()
    with open(rep.SA_PATH, encoding="utf-8") as fh:
        sa = json.load(fh)
    token = rep.access_token(sa)
    rep.MEASUREMENT_ID = next((x["measurement_id"] for x in allsites.SITES if x["host"] == host), rep.MEASUREMENT_ID)
    rep.SITE_HOST = host
    prop, note = rep.find_property(token)
    if not prop:
        raise SystemExit(f"no GA4 property: {note}")

    end = dt.date.today()
    start = end - dt.timedelta(days=days - 1)
    resp = rep.ga4(token, prop, start.isoformat(), end.isoformat(),
                   ["date", "sessionSourceMedium"], ["sessions", "engagedSessions"],
                   limit=500, host=host)
    buckets = {}
    raw = {}
    for _, _, vals, nums in rep.ga4_rows(resp):
        d = f"{vals[0][:4]}-{vals[0][4:6]}-{vals[0][6:]}"
        s, e = int(float(nums[0])), int(float(nums[1]))
        k = kind(vals[1])
        b = buckets.setdefault(d, {})
        b[k] = b.get(k, 0) + s
        b[k + "_e"] = b.get(k + "_e", 0) + e
        raw.setdefault(d, []).append((vals[1], s, e))

    order = ["AI", "BingDDG", "Google", "Direct", "Other"]
    print(f"# {host}  {start} ~ {end}（GA4 property {prop}, host=pbzero.wiki）\n")
    head = "| date | " + " | ".join(order) + " | total |"
    print(head)
    print("|" + "---|" * (len(order) + 2))
    totals = {k: 0 for k in order}
    for d in sorted(buckets):
        b = buckets[d]
        row = [str(b.get(k, 0)) for k in order]
        for k in order:
            totals[k] += b.get(k, 0)
        print(f"| {d} | " + " | ".join(row) + f" | {sum(b.get(k,0) for k in order)} |")
    print(f"| **sum** | " + " | ".join(str(totals[k]) for k in order) + f" | {sum(totals.values())} |")

    print("\n## AI 明细（按 source/medium）")
    for d in sorted(raw):
        ai = [(s, n, e) for s, n, e in raw[d] if kind(s) == "AI"]
        if ai:
            print(f"- {d}: " + ", ".join(f"{s}={n}({e} engaged)" for s, n, e in ai))


if __name__ == "__main__":
    main()
