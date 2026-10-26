#!/usr/bin/env python3
"""Link and structure audit for the pbzero-wiki content pages.

Why this exists: earlier audits ran regexes over the raw JSON text, where every
quote inside a content string is escaped (\\"), so `href="/x"` never matched and
the report was vacuously clean. This module parses the JSON properly and checks
the decoded strings.

Usage
  python3 scripts/audit-links.py            # audit everything, exit 1 on failure
  python3 scripts/audit-links.py --fix      # report only; links are never rewritten
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "src", "data", "pages")
CODE_GLOBS = [
    os.path.join(ROOT, "src", "lib", "taxonomy.ts"),
    os.path.join(ROOT, "src", "lib", "nav-topics.ts"),
    os.path.join(ROOT, "src", "components", "RelatedPages.tsx"),
    os.path.join(ROOT, "src", "data", "news.json"),
]
EXTERNAL = re.compile(r"^(https?:|mailto:|#|/)")
HREF = re.compile(r'href="([^"]+)"')
TAGS = ["p", "ul", "ol", "li", "strong", "em", "a", "code", "h3", "table", "tr", "td", "th", "tbody", "thead"]


def page_slugs():
    return sorted(f[:-5] for f in os.listdir(PAGES_DIR) if f.endswith(".json"))


def load(slug):
    with open(os.path.join(PAGES_DIR, slug + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def page_bodies(doc):
    """Every text blob on a page that may hold markup."""
    for s in doc.get("sections", []):
        yield s.get("id", "?"), s.get("content", "")
    for x in doc.get("facts", []):
        yield "fact:" + x.get("label", "?"), x.get("value", "")
    yield "meta:description", doc.get("description", "")
    yield "meta:keyword", doc.get("keyword", "")


def audit():
    slugs = page_slugs()
    pages = set(slugs)
    errors = []
    warnings = []

    # 1. internal links inside page content
    inbound = {s: 0 for s in slugs}
    for slug in slugs:
        doc = load(slug)
        if doc.get("slug") not in (None, slug):
            errors.append(f"{slug}: slug field says {doc.get('slug')!r}, filename says {slug!r}")
        for sid, body in page_bodies(doc):
            for href in HREF.findall(body):
                if href.startswith(("http://", "https://", "mailto:")):
                    continue
                if href.startswith("#"):
                    target = href[1:]
                    ids = {s.get("id") for s in doc.get("sections", [])}
                    if target and target not in ids:
                        errors.append(f"{slug} [{sid}]: anchor #{target} does not exist on this page")
                    continue
                target = href.lstrip("/").split("?")[0].split("#")[0]
                if not target:
                    continue
                if target not in pages:
                    errors.append(f"{slug} [{sid}]: dead internal link /{target}")
                else:
                    inbound[target] += 1
        # tag balance, per section
        for sid, body in page_bodies(doc):
            for t in TAGS:
                o = len(re.findall(r"<%s[ >]" % t, body))
                c = len(re.findall(r"</%s>" % t, body))
                if o != c:
                    errors.append(f"{slug} [{sid}]: <{t}> open {o} close {c}")

    # 2. links from navigation/registration code (decoded, not escaped)
    code_text = []
    for path in CODE_GLOBS:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        if path.endswith(".json"):
            data = json.load(open(path, encoding="utf-8"))
            entries = data.get("entries", data if isinstance(data, list) else [])
            for e in entries:
                for a in e.get("affects", []):
                    if a == "autolink":   # sentinel handled by gen-news-page.py
                        continue
                    if a not in pages:
                        errors.append(f"news {e.get('date')}: affects '{a}' has no page")
                for _, body in [(k, v) for k, v in e.items() if isinstance(v, str)]:
                    for href in HREF.findall(body):
                        t = href.lstrip("/")
                        if t and not href.startswith("http") and t not in pages:
                            errors.append(f"news {e.get('date')}: dead link {href}")
            code_text.append(json.dumps(data, ensure_ascii=False))
        else:
            for m in re.finditer(r'(?:slug|href)\s*:\s*"(/[a-z0-9-]*)"', raw):
                t = m.group(1).lstrip("/")
                if t and t not in pages:
                    errors.append(f"{os.path.basename(path)}: nav points at missing page /{t}")
            for m in re.finditer(r'(?:slug|href)\s*:\s*"([a-z0-9-]+)"', raw):
                t = m.group(1)
                if t in pages:
                    inbound[t] += 1
            code_text.append(raw)

    # 3. orphans: pages with no inbound link from anywhere
    joined = "\n".join(code_text)
    for path in [os.path.join(ROOT, "src", "app", "[slug]", "page.tsx")]:
        if os.path.exists(path):
            joined += open(path, encoding="utf-8").read()
    for slug in slugs:
        if inbound[slug] == 0 and slug not in ("about", "contact", "privacy-policy", "site-about", "faq"):
            hit = f"/{slug}" in joined
            if not hit:
                errors.append(f"orphan: /{slug} has no inbound link from pages or navigation")

    # 4. stale-looking lastUpdated (pages not touched in a long time while siblings were)
    dates = {s: load(s).get("lastUpdated", "") for s in slugs}
    newest = max(dates.values()) if dates else ""
    for s, d in sorted(dates.items()):
        if d and d < "2026-10-20" and newest > "2026-10-24":
            warnings.append(f"{s}: lastUpdated {d} while the site was updated {newest}")

    return slugs, errors, warnings


def main():
    slugs, errors, warnings = audit()
    print(f"pages: {len(slugs)}")
    for w in warnings:
        print(f"  warn  {w}")
    if errors:
        for e in errors:
            print(f"  ERROR {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nclean ✓  ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
