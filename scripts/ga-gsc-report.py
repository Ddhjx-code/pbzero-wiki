#!/usr/bin/env python3
"""Pull Search Console and GA4 numbers for pbzero.wiki with a service account.

Usage:
  python3 scripts/ga-gsc-report.py                      # last 28 days vs previous 28
  python3 scripts/ga-gsc-report.py 2026-10-01 2026-11-10

Needs a GCP service-account JSON key at .secrets/gcp-sa.json (override with
GOOGLE_SA=...). The key must be added as a GA4 property viewer and as a Search
Console user, otherwise the APIs answer 403 and nothing here can help.

No third-party packages: the RS256 assertion is signed with the `openssl` CLI,
so this runs on a bare python3.
"""
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

SA_PATH = os.environ.get("GOOGLE_SA", ".secrets/gcp-sa.json")
MEASUREMENT_ID = "G-W9Y62B3DBM"
# GA4 property 549933418 hosts several web streams (pbzero.wiki and
# expedition33.wiki), so reports must be filtered down to this host.
SITE_HOST = "pbzero.wiki"
SCOPES = (
    "https://www.googleapis.com/auth/analytics.readonly "
    "https://www.googleapis.com/auth/webmasters.readonly"
)
TOKEN_URI = "https://oauth2.googleapis.com/token"
GSC_SITES = ("sc-domain:pbzero.wiki", "https://pbzero.wiki/")
OUT_DIR = "reports"


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def http_json(url, token=None, payload=None, method=None, retries=3):
    """JSON request with retries. The link to Google gets reset often enough
    that a single URLError should not abort a 184-URL audit."""
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=data, headers=headers, method=method or ("POST" if data else "GET")
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:600]
            if exc.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(2 + 2 * attempt)
                continue
            raise RuntimeError(f"HTTP {exc.code} {url}\n{body}") from None
        except Exception as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 + 2 * attempt)
                continue
    raise RuntimeError(f"network error on {url}: {type(last).__name__} {last}") from None


def access_token(sa):
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    claim = {
        "iss": sa["client_email"],
        "scope": SCOPES,
        "aud": sa.get("token_uri", TOKEN_URI),
        "iat": now,
        "exp": now + 3600,
    }
    unsigned = (
        b64u(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        + "."
        + b64u(json.dumps(claim).encode())
    )
    with tempfile.TemporaryDirectory() as tmp:
        key = os.path.join(tmp, "key.pem")
        with open(key, "w", encoding="utf-8") as fh:
            fh.write(sa["private_key"])
        os.chmod(key, 0o600)
        src = os.path.join(tmp, "unsigned.txt")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(unsigned)
        sig_path = os.path.join(tmp, "sig.bin")
        subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key, "-out", sig_path, src],
            check=True,
            capture_output=True,
        )
        with open(sig_path, "rb") as fh:
            signature = fh.read()

    body = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": f"{unsigned}.{b64u(signature)}",
        }
    ).encode()
    last = None
    for attempt in range(4):
        req = urllib.request.Request(
            sa.get("token_uri", TOKEN_URI),
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())["access_token"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:600]
            raise RuntimeError(f"token exchange failed (HTTP {exc.code}): {detail}") from None
        except Exception as exc:
            last = exc
            if attempt + 1 < 4:
                time.sleep(2 + 2 * attempt)
    raise RuntimeError(f"token exchange failed on network: {type(last).__name__} {last}") from None


def find_property(token):
    """Map G-W9Y62B3DBM to the numeric GA4 property id."""
    try:
        data = http_json("https://analyticsadmin.googleapis.com/v1beta/accountSummaries?pageSize=200", token)
    except RuntimeError as exc:
        return None, f"Admin API unavailable: {str(exc)[:120]}"
    for account in data.get("accountSummaries", []):
        for prop in account.get("propertySummaries", []):
            pid = prop.get("property", "").split("/")[-1]
            if not pid:
                continue
            try:
                streams = http_json(
                    f"https://analyticsadmin.googleapis.com/v1beta/properties/{pid}/dataStreams", token
                )
            except RuntimeError:
                continue
            for stream in streams.get("dataStreams", []):
                if stream.get("webStreamData", {}).get("measurementId") == MEASUREMENT_ID:
                    return pid, prop.get("displayName", "")
    return None, "no property matched the measurement id"


def ga4(token, prop, start, end, dims, mets, limit=15):
    payload = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "metrics": [{"name": m} for m in mets],
        "limit": limit,
        # The property also carries other sites (expedition33.wiki shares it),
        # so every report has to be pinned to our own host or the totals are
        # a blend of two unrelated wikis.
        "dimensionFilter": {
            "filter": {
                "fieldName": "hostName",
                "stringFilter": {"matchType": "EXACT", "value": SITE_HOST},
            }
        },
    }
    if dims:
        payload["dimensions"] = [{"name": d} for d in dims]
    return http_json(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport", token, payload
    )


def ga4_rows(resp):
    dims = [h["name"] for h in resp.get("dimensionHeaders", [])]
    mets = [h["name"] for h in resp.get("metricHeaders", [])]
    rows = []
    for row in resp.get("rows", []):
        vals = [d.get("value", "") for d in row.get("dimensionValues", [])]
        nums = [m.get("value", "") for m in row.get("metricValues", [])]
        rows.append((dims, mets, vals, nums))
    return rows


def gsc(token, site, start, end, dims, limit=25):
    payload = {"startDate": start, "endDate": end, "rowLimit": limit}
    if dims:
        payload["dimensions"] = dims
    quoted = urllib.parse.quote(site, safe="")
    return http_json(
        f"https://www.googleapis.com/webmasters/v3/sites/{quoted}/searchAnalytics/query", token, payload
    )


def table(headers, rows, numeric_from=1):
    if not rows:
        return "_(no rows)_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            cells.append(f"{cell:,}" if i >= numeric_from and isinstance(cell, (int, float)) else str(cell))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def index_audit(token, site, urls):
    """Ask Search Console about every URL in the sitemap.

    Coverage state is the only honest answer to "is this page in Google" -
    the sitemap submitted/indexed counters are legacy and go stale.
    """
    out = []
    for url in urls:
        try:
            resp = http_json(
                "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                token,
                {"inspectionUrl": url, "siteUrl": site, "languageCode": "en"},
            )
            res = resp.get("inspectionResult", {}).get("indexStatusResult", {})
            out.append((url, res.get("coverageState", "-"), (res.get("lastCrawlTime") or "")[:10]))
        except RuntimeError as exc:
            out.append((url, f"inspect failed: {str(exc)[:60]}", ""))
    return out


def sitemap_urls(site_hint):
    host = site_hint.replace("sc-domain:", "https://").rstrip("/")
    try:
        # Cloudflare answers 403 to the bare python-urllib user agent.
        req = urllib.request.Request(
            f"{host}/sitemap.xml",
            headers={"User-Agent": "Mozilla/5.0 (compatible; pbzero-wiki-report/1.0)"},
        )
        raw = urllib.request.urlopen(req, timeout=60).read().decode()
    except Exception:
        raw = ""
    if not raw:
        # Direct HTTPS to the site is flaky from some networks (Cloudflare
        # resets the TLS handshake), so fall back to the repo's page list.
        if os.path.isdir(PAGES):
            slugs = sorted(f[:-5] for f in os.listdir(PAGES) if f.endswith(".json"))
            return [f"https://pbzero.wiki/{s}" for s in slugs]
        return []
    return re.findall(r"<loc>([^<]+)</loc>", raw)


def main():
    if not os.path.exists(SA_PATH):
        raise SystemExit(f"missing service-account key: {SA_PATH}")

    audit = "--index-audit" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    today = dt.date.today()
    if len(args) >= 2:
        start = dt.date.fromisoformat(args[0])
        end = dt.date.fromisoformat(args[1])
    else:
        end = today - dt.timedelta(days=1)
        start = end - dt.timedelta(days=27)
    span = (end - start).days + 1
    prev_end = start - dt.timedelta(days=1)
    prev_start = prev_end - dt.timedelta(days=span - 1)

    with open(SA_PATH, encoding="utf-8") as fh:
        sa = json.load(fh)
    print(f"service account: {sa['client_email']}")
    token = access_token(sa)
    print("access token: ok")

    lines = [
        f"# pbzero.wiki - GA4 & Search Console",
        "",
        f"- window: **{start} to {end}** ({span} days)",
        f"- compared with: {prev_start} to {prev_end}",
        f"- pulled: {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
    ]

    prop, note = find_property(token)
    if prop:
        lines.append(f"## GA4 (property {prop}{', ' + note if note else ''})")
        lines.append("")
        cur = ga4(token, prop, start.isoformat(), end.isoformat(), [], ["activeUsers", "sessions", "screenPageViews", "engagementRate"])
        prev = ga4(token, prop, prev_start.isoformat(), prev_end.isoformat(), [], ["activeUsers", "sessions", "screenPageViews"])
        cvals = [float(m["value"]) for m in cur.get("rows", [{}])[0].get("metricValues", [])] if cur.get("rows") else [0, 0, 0, 0]
        pvals = [float(m["value"]) for m in prev.get("rows", [{}])[0].get("metricValues", [])] if prev.get("rows") else [0, 0, 0, 0]

        def delta(a, b):
            a, b = int(a), int(b)
            return f"{a} ({(a - b):+d})" if b else str(a)

        lines.append(table(
            ["metric", "current", "previous"],
            [
                ["active users", delta(cvals[0], pvals[0]), int(pvals[0])],
                ["sessions", delta(cvals[1], pvals[1]), int(pvals[1])],
                ["page views", delta(cvals[2], pvals[2]), int(pvals[2])],
                ["engagement rate", f"{cvals[3] * 100:.1f}%" if len(cvals) > 3 else "-", "-"],
            ],
            1,
        ))

        try:
            resp = ga4(
                token, prop, start.isoformat(), end.isoformat(),
                ["date"], ["activeUsers", "sessions"], limit=span + 5,
            )
            drows = []
            for _, _, vals, nums in ga4_rows(resp):
                d = vals[0]
                drows.append([f"{d[:4]}-{d[4:6]}-{d[6:]}", *[f"{float(n):,.0f}" for n in nums]])
            drows.sort(key=lambda r: r[0])
            lines.append("### Daily")
            lines.append("")
            lines.append(table(["date", "activeUsers", "sessions"], drows))
        except RuntimeError as exc:
            lines.append(f"_(daily failed: {str(exc)[:160]})_")
            lines.append("")

        for title, dim, mets in [
            ("Channels", "sessionDefaultChannelGroup", ["sessions", "activeUsers"]),
            ("Sources", "sessionSourceMedium", ["sessions"]),
            ("Landing pages", "landingPagePlusQueryString", ["sessions", "screenPageViews"]),
            ("Top pages", "pagePath", ["screenPageViews", "activeUsers"]),
            ("Countries", "country", ["activeUsers"]),
        ]:
            try:
                resp = ga4(token, prop, start.isoformat(), end.isoformat(), [dim], mets, limit=15)
                rows = [
                    [vals[0], *[f"{float(n):,.0f}" if float(n) == int(float(n)) else f"{float(n):,.2f}" for n in nums]]
                    for _, _, vals, nums in ga4_rows(resp)
                ]
                lines.append(f"### {title}")
                lines.append("")
                lines.append(table([dim, *mets], rows))
            except RuntimeError as exc:
                lines.append(f"### {title}")
                lines.append("")
                lines.append(f"_(failed: {str(exc)[:200]})_")
                lines.append("")
    else:
        lines.append(f"## GA4")
        lines.append("")
        lines.append(f"_(skipped: {note})_")
        lines.append("")

    try:
        sites = http_json("https://www.googleapis.com/webmasters/v3/sites", token)
        available = [s.get("siteUrl") for s in sites.get("siteEntry", [])]
    except RuntimeError as exc:
        available = []
        lines.append(f"## Search Console")
        lines.append("")
        lines.append(f"_(site list failed: {str(exc)[:200]})_")
        lines.append("")

    if available:
        site = next((s for s in GSC_SITES if s in available), available[0])
        lines.append(f"## Search Console ({site})")
        lines.append("")
        lines.append(f"properties visible to this account: {', '.join(available)}")
        lines.append("")
        try:
            totals = gsc(token, site, start.isoformat(), end.isoformat(), None, 1)
            rows = totals.get("rows", [])
            if rows:
                r = rows[0]
                lines.append(table(
                    ["clicks", "impressions", "ctr", "avg position"],
                    [[r.get("clicks", 0), r.get("impressions", 0), f"{r.get('ctr', 0) * 100:.2f}%", f"{r.get('position', 0):.1f}"]],
                    0,
                ))
            else:
                lines.append("_(no impressions in this window)_\n")

            for title, dim in [("Top queries", "query"), ("Top pages", "page"), ("Countries", "country"), ("Devices", "device")]:
                resp = gsc(token, site, start.isoformat(), end.isoformat(), [dim], 25)
                rows = [
                    [
                        r["keys"][0],
                        int(r.get("clicks", 0)),
                        int(r.get("impressions", 0)),
                        f"{r.get('ctr', 0) * 100:.1f}%",
                        f"{r.get('position', 0):.1f}",
                    ]
                    for r in resp.get("rows", [])
                ]
                lines.append(f"### {title}")
                lines.append("")
                lines.append(table([dim, "clicks", "impressions", "ctr", "position"], rows))
        except RuntimeError as exc:
            lines.append(f"_(query failed: {str(exc)[:200]})_")
            lines.append("")

    if audit:
        urls = sitemap_urls(GSC_SITES[0])
        lines.append("## Index coverage (sitemap URLs)")
        lines.append("")
        if not urls:
            lines.append("_(could not read sitemap.xml)_")
            lines.append("")
        else:
            print(f"inspecting {len(urls)} URLs...")
            results = index_audit(token, GSC_SITES[0], urls)
            tally = {}
            for _, state, _ in results:
                tally[state] = tally.get(state, 0) + 1
            lines.append(table(
                ["coverage state", "urls"],
                [[k, v] for k, v in sorted(tally.items(), key=lambda kv: -kv[1])],
                1,
            ))
            unknown = [u.replace("https://pbzero.wiki", "") for u, s, _ in results if "unknown" in s.lower()]
            if unknown:
                lines.append(f"\nNot yet known to Google ({len(unknown)}): {', '.join(unknown[:40])}")
                if len(unknown) > 40:
                    lines.append(f"... and {len(unknown) - 40} more")
                lines.append("")

    report = "\n".join(lines)
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{today.isoformat()}-gsc-ga4.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()
