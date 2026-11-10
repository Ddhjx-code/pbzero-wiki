#!/usr/bin/env python3
"""Pull GA4 and Search Console numbers for every site on this account.

Usage:
  python3 scripts/all-sites-report.py                      # last 28 days
  python3 scripts/all-sites-report.py 2026-10-13 2026-11-09

Reuses the transport and JWT signing in ga-gsc-report.py, so it needs the same
service-account key at .secrets/gcp-sa.json and the same two APIs enabled.

One GA4 property can carry several web streams (549933418 has both
expedition33.wiki and pbzero.wiki), so every query is pinned to a single
hostName - an unfiltered run silently blends the sites together.
"""
import datetime as dt
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rep", os.path.join(HERE, "ga-gsc-report.py"))
rep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rep)

SITES = [
    {
        "key": "expedition33",
        "host": "expedition33.wiki",
        "measurement_id": "G-MZ867GJT24",
        "gsc": ["https://expedition33.wiki/", "sc-domain:expedition33.wiki"],
    },
    {
        "key": "pbzero",
        "host": "pbzero.wiki",
        "measurement_id": "G-W9Y62B3DBM",
        "gsc": ["sc-domain:pbzero.wiki", "https://pbzero.wiki/"],
    },
    {
        "key": "morsecodenow",
        "host": "morsecodenow.com",
        "measurement_id": "G-1SWWLW57DQ",
        "gsc": ["sc-domain:morsecodenow.com", "https://morsecodenow.com/"],
    },
]

TOP_N = 10


def num(value, decimals=0):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{f:,.0f}" if f == int(f) else f"{f:,.2f}"


def ga4_block(token, site, start, end, prev_start, prev_end, lines):
    rep.MEASUREMENT_ID = site["measurement_id"]
    rep.SITE_HOST = site["host"]
    prop, note = rep.find_property(token)
    if not prop:
        lines += [f"### GA4", "", f"_(skipped: {note})_", ""]
        return None

    totals = {}
    try:
        cur = rep.ga4(
            token, prop, start.isoformat(), end.isoformat(), [],
            ["activeUsers", "sessions", "screenPageViews", "engagementRate", "engagedSessions", "averageSessionDuration"],
        )
        prev = rep.ga4(
            token, prop, prev_start.isoformat(), prev_end.isoformat(), [], ["activeUsers", "sessions", "screenPageViews"]
        )
        cvals = [float(m["value"]) for m in cur["rows"][0]["metricValues"]] if cur.get("rows") else [0] * 6
        pvals = [float(m["value"]) for m in prev["rows"][0]["metricValues"]] if prev.get("rows") else [0, 0, 0]
    except (RuntimeError, KeyError, IndexError) as exc:
        lines += ["### GA4", "", f"_(failed: {str(exc)[:200]})_", ""]
        return None

    totals = {
        "users": cvals[0],
        "sessions": cvals[1],
        "views": cvals[2],
        "eng": cvals[3] if len(cvals) > 3 else 0,
        "engaged": cvals[4] if len(cvals) > 4 else 0,
        "duration": cvals[5] if len(cvals) > 5 else 0,
        "days": (end - start).days + 1,
    }

    def d(a, b):
        return f"{int(a)} ({(int(a) - int(b)):+d})" if b else str(int(a))

    rows = [
        ["active users", d(cvals[0], pvals[0]), int(pvals[0]) if len(pvals) > 0 else 0],
        ["sessions", d(cvals[1], pvals[1]), int(pvals[1]) if len(pvals) > 1 else 0],
        ["page views", d(cvals[2], pvals[2]), int(pvals[2]) if len(pvals) > 2 else 0],
        ["engagement rate", f"{totals['eng'] * 100:.1f}%", "-"],
        ["engaged sessions", f"{int(totals['engaged'])}", "-"],
        ["avg session duration", f"{totals['duration']:.0f}s", "-"],
        ["**sessions / day**", f"**{totals['sessions'] / totals['days']:.1f}**", "-"],
        ["**engaged sessions / day**", f"**{totals['engaged'] / totals['days']:.1f}**", "-"],
    ]
    lines += [
        f"### GA4 (property {prop}, hostName={site['host']})",
        "",
        rep.table(["metric", "current", "previous"], rows, 1),
    ]

    def fmt(metric, value):
        if metric == "engagementRate":
            return f"{float(value) * 100:.1f}%"
        if metric == "averageSessionDuration":
            return f"{float(value):.0f}s"
        return num(value)

    for title, dim, mets in [
        ("Channels (with engaged sessions)", "sessionDefaultChannelGroup",
         ["sessions", "engagedSessions", "engagementRate", "averageSessionDuration"]),
        ("Sources", "sessionSourceMedium", ["sessions"]),
        ("Devices", "deviceCategory", ["sessions", "engagedSessions"]),
        ("Top pages", "pagePath", ["screenPageViews", "activeUsers"]),
        ("Countries", "country", ["activeUsers"]),
    ]:
        try:
            resp = rep.ga4(token, prop, start.isoformat(), end.isoformat(), [dim], mets, limit=TOP_N)
            rows = [[v[0], *[fmt(met, n) for met, n in zip(mets, nums)]] for _, _, v, nums in rep.ga4_rows(resp)]
        except RuntimeError as exc:
            lines += [f"#### {title}", "", f"_(failed: {str(exc)[:160]})_", ""]
            continue
        lines += [f"#### {title}", "", rep.table([dim, *mets], rows), ""]

    return totals


def gsc_block(token, site, start, end, available, lines):
    props = [p for p in site["gsc"] if p in available]
    if not props:
        lines += ["### Search Console", "", "_（该站点未在此账号下验证）_", ""]
        return None
    prop = props[0]
    try:
        data = rep.gsc(token, prop, start.isoformat(), end.isoformat(), [], limit=1)
    except RuntimeError as exc:
        lines += ["### Search Console", "", f"_(failed: {str(exc)[:200]})_", ""]
        return None

    rows = data.get("rows", [])
    if not rows:
        lines += [f"### Search Console ({prop})", "", "_(28 天内无曝光)_", ""]
        return {"clicks": 0, "impressions": 0, "ctr": 0, "pos": 0}

    r = rows[0]
    tot = {"clicks": r["clicks"], "impressions": r["impressions"], "ctr": r["ctr"], "pos": r["position"]}
    lines += [
        f"### Search Console ({prop})",
        "",
        rep.table(
            ["clicks", "impressions", "ctr", "avg position"],
            [[str(tot["clicks"]), str(tot["impressions"]), f"{tot['ctr'] * 100:.2f}%", f"{tot['pos']:.1f}"]],
            -1,
        ),
    ]

    for title, dim in [("Top queries", "query"), ("Top pages", "page"), ("Countries", "country")]:
        try:
            d = rep.gsc(token, prop, start.isoformat(), end.isoformat(), [dim], limit=TOP_N)
            rows = [
                [
                    row.get("keys", ["-"])[0],
                    str(row.get("clicks", 0)),
                    str(row.get("impressions", 0)),
                    f"{row.get('ctr', 0) * 100:.1f}%",
                    f"{row.get('position', 0):.1f}",
                ]
                for row in d.get("rows", [])
            ]
        except RuntimeError as exc:
            lines += [f"#### {title}", "", f"_(failed: {str(exc)[:160]})_", ""]
            continue
        lines += [f"#### {title}", "", rep.table([dim, "clicks", "impressions", "ctr", "position"], rows), ""]

    return tot


def main():
    if not os.path.exists(rep.SA_PATH):
        raise SystemExit(f"missing service-account key: {rep.SA_PATH}")

    today = dt.date.today()
    if len(sys.argv) >= 3:
        start = dt.date.fromisoformat(sys.argv[1])
        end = dt.date.fromisoformat(sys.argv[2])
    else:
        end = today - dt.timedelta(days=1)
        start = end - dt.timedelta(days=27)
    span = (end - start).days + 1
    prev_end = start - dt.timedelta(days=1)
    prev_start = prev_end - dt.timedelta(days=span - 1)

    with open(rep.SA_PATH, encoding="utf-8") as fh:
        sa = json.load(fh)
    token = rep.access_token(sa)
    print(f"service account: {sa['client_email']}")
    print(f"window: {start} .. {end}")

    available = []
    try:
        sites = rep.http_json("https://www.googleapis.com/webmasters/v3/sites", token)
        available = [s.get("siteUrl") for s in sites.get("siteEntry", [])]
    except RuntimeError as exc:
        print(f"GSC site list failed: {str(exc)[:160]}")

    body = []
    summary = []
    for site in SITES:
        print(f"  pulling {site['host']} ...")
        lines = [f"## {site['host']}", ""]
        ga = ga4_block(token, site, start, end, prev_start, prev_end, lines)
        sc = gsc_block(token, site, start, end, available, lines)
        body += lines + [""]
        summary.append((site["host"], ga, sc))

    out = [
        "# 三个站点的 GA4 / Search Console",
        "",
        f"- window: **{start} to {end}** ({span} 天)",
        f"- compared with: {prev_start} to {prev_end}",
        f"- pulled: {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## 汇总",
        "",
    ]
    rows = []
    for host, ga, sc in summary:
        rows.append(
            [
                host,
                num(ga["users"]) if ga else "-",
                num(ga["sessions"]) if ga else "-",
                f"**{ga['sessions'] / ga['days']:.1f}**" if ga else "-",
                num(ga["engaged"]) if ga else "-",
                f"**{ga['engaged'] / ga['days']:.1f}**" if ga else "-",
                f"{ga['eng'] * 100:.0f}%" if ga else "-",
                str(sc["clicks"]) if sc else "-",
                str(sc["impressions"]) if sc else "-",
                f"{sc['pos']:.1f}" if sc else "-",
            ]
        )
    out += [
        rep.table(
            [
                "site", "GA4 users", "sessions", "sessions/day",
                "engaged", "engaged/day", "engagement",
                "GSC clicks", "impressions", "avg position",
            ],
            rows,
        ),
        "",
        "> sessions 含未知爬虫与预渲染；engaged sessions 是 GA4 认定的互动会话"
        "（≥10 秒、或 ≥2 次浏览、或触发关键事件），更接近真实读者。",
        "",
        "---",
        "",
    ]
    out += body

    os.makedirs(rep.OUT_DIR, exist_ok=True)
    path = os.path.join(rep.OUT_DIR, f"{today:%Y-%m-%d}-all-sites.md")
    report = "\n".join(out)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()
