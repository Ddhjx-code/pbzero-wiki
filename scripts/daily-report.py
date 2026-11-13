#!/usr/bin/env python3
"""Today's numbers, not a rolling month.

Usage:
  python3 scripts/daily-report.py              # today so far + yesterday + 7-day trend
  python3 scripts/daily-report.py 2026-11-12   # treat that date as "today"

The 28-day report answers "how is the site doing overall". This one answers
"what happened since I last looked": GA4 is near real-time, so the current day
is included as a partial day; Search Console lags two to three days, so its
table is labelled with the last date that actually carries data instead of
being padded with zeros.
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

_spec2 = importlib.util.spec_from_file_location(
    "allsites", os.path.join(HERE, "all-sites-report.py")
)
allsites = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(allsites)

SITES = allsites.SITES
TOP_N = 10
TREND_DAYS = 7


def ymd(date):
    return date.isoformat()


def short(raw):
    """GA4 dates arrive as 20261113, GSC as 2026-11-13."""
    raw = str(raw)
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
    return raw


def daily_rows(token, prop, host, start, end):
    resp = rep.ga4(
        token, prop, ymd(start), ymd(end), ["date"],
        ["activeUsers", "sessions", "engagedSessions", "screenPageViews"],
        limit=TREND_DAYS + 7, host=host,
    )
    out = {}
    for _, _, vals, nums in rep.ga4_rows(resp):
        out[short(vals[0])] = [int(float(n)) for n in nums]
    return out


def totals(token, prop, host, start, end):
    resp = rep.ga4(
        token, prop, ymd(start), ymd(end), [],
        ["activeUsers", "sessions", "engagedSessions", "screenPageViews",
         "engagementRate", "averageSessionDuration"],
        host=host,
    )
    if not resp.get("rows"):
        return [0] * 6
    return [float(m["value"]) for m in resp["rows"][0]["metricValues"]]


def main():
    allsites.pick_working_proxy()

    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    day_before = today - dt.timedelta(days=2)
    trend_start = today - dt.timedelta(days=TREND_DAYS - 1)

    with open(rep.SA_PATH, encoding="utf-8") as fh:
        sa = json.load(fh)
    token = rep.access_token(sa)

    available = []
    try:
        sites = rep.http_json("https://www.googleapis.com/webmasters/v3/sites", token)
        available = [s.get("siteUrl") for s in sites.get("siteEntry", [])]
    except RuntimeError as exc:
        print(f"GSC site list failed: {str(exc)[:160]}")

    zones = {s.get("tz") for s in SITES if s.get("tz")}
    tz_note = zones.pop() if len(zones) == 1 else "各站不同"

    out = [
        "# 当日快照",
        "",
        f"- 拉取时间：{dt.datetime.now():%Y-%m-%d %H:%M}",
        f"- 今日（截至现在）：{today}",
        f"- 完整对比日：{yesterday}，前一日 {day_before}",
        f"- 趋势窗口：{trend_start} ~ {today}（{TREND_DAYS} 天）",
        f"- GA4 属性时区：**{tz_note}**",
        "",
        "> GA4 近实时，今天的数字是**不完整的一天**。"
        "Search Console 有 2–3 天延迟，表里标注的是实际有数据的最晚一天，不是今天。",
        "",
    ]

    if tz_note == "Asia/Shanghai" and any(
        s["host"] in ("expedition33.wiki", "pbzero.wiki", "morsecodenow.com") for s in SITES
    ):
        out += [
            f"> 时区提醒：属性按 **北京 00:00** 切日，而读者在美欧。"
            f"因此每个「{today}」实际覆盖的是美东 {today} 前一日 11:00 至 {today} 11:00，"
            "当地晚间高峰会落到次日的格子里。看单日涨跌时要记住这个边界，"
            "连续多日的趋势比单日对比可靠。",
            "",
        ]

    summary = []
    blocks = []

    for site in SITES:
        host = site["host"]
        rep.MEASUREMENT_ID = site["measurement_id"]
        rep.SITE_HOST = host
        prop, note = rep.find_property(token)
        header = [f"## {host}", ""]
        if not prop:
            blocks += header + [f"_(GA4 属性不可见：{note})_", ""]
            continue

        try:
            t_today = totals(token, prop, host, today, today)
            t_yest = totals(token, prop, host, yesterday, yesterday)
            t_prev = totals(token, prop, host, day_before, day_before)
            trend = daily_rows(token, prop, host, trend_start, today)
        except RuntimeError as exc:
            blocks += header + [f"_(GA4 失败：{str(exc)[:200]})_", ""]
            continue

        summary.append((host, t_today, t_yest, t_prev))

        def delta(cur, prev):
            cur, prev = int(cur), int(prev)
            if not prev:
                return f"{cur} (—)"
            return f"{cur} ({(cur - prev) / prev * 100:+.0f}%)"

        rows = [
            ["昨日用户", delta(t_yest[0], t_prev[0])],
            ["昨日会话", delta(t_yest[1], t_prev[1])],
            ["昨日互动会话", delta(t_yest[2], t_prev[2])],
            ["昨日浏览", delta(t_yest[3], t_prev[3])],
            ["昨日互动率", f"{t_yest[4] * 100:.0f}%" if t_yest[4] <= 1 else f"{t_yest[4]:.0f}%"],
            ["昨日平均时长", f"{t_yest[5]:.0f}s"],
            ["今日用户（截至现在）", f"{int(t_today[0])}"],
            ["今日会话（截至现在）", f"{int(t_today[1])}"],
            ["今日互动会话", f"{int(t_today[2])}"],
        ]
        body = header + [
            f"### GA4（property {prop}）",
            "",
            rep.table(["指标", f"{yesterday} 对比 {day_before}"], rows, 1),
            "",
            f"### 近 {TREND_DAYS} 天",
            "",
        ]

        trows = []
        for offset in range(TREND_DAYS):
            day = trend_start + dt.timedelta(days=offset)
            key = ymd(day)
            v = trend.get(key, [0, 0, 0, 0])
            mark = ""
            if day == today:
                mark = " ⏳"
            elif day == yesterday:
                mark = " ←"
            trows.append([f"{key}{mark}", str(v[0]), str(v[1]), str(v[2]), str(v[3])])
        body += [rep.table(["日期", "用户", "会话", "互动会话", "浏览"], trows), ""]

        # Page detail for the last complete day - today is too thin to rank.
        try:
            resp = rep.ga4(
                token, prop, ymd(yesterday), ymd(yesterday), ["pagePath"],
                ["screenPageViews", "activeUsers"], limit=TOP_N, host=host,
            )
            prows = [
                [v[0], str(int(float(nums[0]))), str(int(float(nums[1])))]
                for _, _, v, nums in rep.ga4_rows(resp)
            ]
        except RuntimeError as exc:
            body += [f"#### 昨日页面", "", f"_(失败：{str(exc)[:160]})_", ""]
        else:
            body += [f"#### 昨日页面（{yesterday}）", "",
                     rep.table(["pagePath", "浏览", "用户"], prows), ""]

        # Search Console: find the last day that actually has rows.
        props = [p for p in site["gsc"] if p in available]
        if not props:
            body += ["### Search Console", "", "_（账号下未验证该站点）_", ""]
        else:
            gprop = props[0]
            try:
                d = rep.gsc(token, gprop, ymd(today - dt.timedelta(days=6)), ymd(today), ["date"], limit=20)
                grows = sorted(
                    [[short(r["keys"][0]), str(r["clicks"]), str(r["impressions"]),
                      f"{r['position']:.1f}"] for r in d.get("rows", [])]
                )
            except RuntimeError as exc:
                body += ["### Search Console", "", f"_(失败：{str(exc)[:200]})_", ""]
            else:
                if grows:
                    latest = grows[-1][0]
                    body += [
                        f"### Search Console（{gprop}）",
                        "",
                        f"数据截至 **{latest}**（GSC 延迟 2–3 天；今天与昨天通常为空）",
                        "",
                        rep.table(["日期", "点击", "曝光", "平均排名"], grows),
                        "",
                    ]
                else:
                    body += ["### Search Console", "", "_（近 7 天无曝光）_", ""]

        blocks += body

    if summary:
        out += [
            "## 三站合计",
            "",
            rep.table(
                ["站点", "昨日用户", "昨日会话", "昨日互动", f"今日用户（截至 {dt.datetime.now():%H:%M}）"],
                [
                    [host, str(int(t_yest[0])), str(int(t_yest[1])), str(int(t_yest[2])), str(int(t_today[0]))]
                    for host, t_today, t_yest, _ in summary
                ],
            ),
            "",
            "---",
            "",
        ]
    out += blocks

    os.makedirs(rep.OUT_DIR, exist_ok=True)
    path = os.path.join(rep.OUT_DIR, f"{today:%Y-%m-%d}-daily.md")
    report = "\n".join(out)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()
