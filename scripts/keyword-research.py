#!/usr/bin/env python3
"""
SEO keyword research — harvest real search suggestions, no paid API needed.

Sources (all free, no key):
  google_chrome   Google suggest, client=chrome  -> 15 suggestions + google:suggestrelevance score
  google_firefox  Google suggest, client=firefox -> 10 suggestions
  google_yt       Google suggest, ds=yt (YouTube) -> video intent layer
  bing            Bing OpenSearch suggest
  ddg             DuckDuckGo autocomplete

Why suggestions are a valid demand signal:
  every engine returns them ordered by real query popularity, and Google's
  `google:suggestrelevance` is an explicit relevance/popularity score. A word
  that several engines independently suggest under several different prefixes
  is a word people actually type. That gives a relative demand ranking without
  any keyword-volume subscription.

Usage:
  python3 scripts/keyword-research.py --seeds "phantom blade zero" --depth 3
  python3 scripts/keyword-research.py --seeds-file seeds.txt --site-root . --depth 2
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

PROXY = os.environ.get("KW_PROXY", "http://127.0.0.1:7897")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

ENDPOINTS = {
    "google_chrome":  "https://suggestqueries.google.com/complete/search?client=chrome&hl={hl}&gl={gl}&q={q}",
    "google_firefox": "https://suggestqueries.google.com/complete/search?client=firefox&hl={hl}&gl={gl}&q={q}",
    "google_yt":      "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl={hl}&gl={gl}&q={q}",
    "bing":           "https://api.bing.com/osjson.aspx?query={q}&market={mkt}",
    "ddg":            "https://duckduckgo.com/ac/?q={q}&type=list",
}

# intent modifiers. Each is appended to the seed as "<seed><mod>".
QUESTION_PREFIX = ["how to ", "what is ", "where is ", "why ", "can you ", "is ", "does ", "when "]
INTENT_SUFFIX = [
    " guide", " wiki", " tips", " reddit", " steam", " ps5", " xbox", " pc",
    " release date", " dlc", " update", " map", " trophy guide", " achievements",
    " walkthrough", " review", " metacritic", " new game plus", " difficulty",
    " how long", " best", " tier list", " vs", " or", " explained", " bug",
    " crash", " price", " cd key", " system requirements", " demo",
    " boss", " bosses", " weapons", " weapon tier list", " armor", " build",
    " ending", " endings", " secret", " collectibles", " missables",
]
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

# ---------------------------------------------------------------- transport
_cache = {}


def fetch(url, tries=3):
    if url in _cache:
        return _cache[url]
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept-Language": "en-US,en;q=0.9",
                # without identity the suggest endpoint answers gzip and urllib
                # hangs on read until timeout -> silent empty results
                "Accept-Encoding": "identity",
            })
            op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
            with op.open(req, timeout=12) as r:
                raw = r.read()
                if raw[:2] == b"\x1f\x8b":
                    import gzip
                    raw = gzip.decompress(raw)
                body = raw.decode("utf-8", "replace")
            _cache[url] = body
            return body
        except Exception:
            if i == tries - 1:
                _cache[url] = None
                return None
            time.sleep(0.6 * (i + 1))
    return None


def parse_google(body):
    """-> (suggestions, relevance_list)"""
    if not body:
        return [], []
    try:
        data = json.loads(body)
    except Exception:
        # firefox client sometimes returns bare array already; nothing else to try
        return [], []
    if not isinstance(data, list) or len(data) < 2:
        return [], []
    sugg = [s for s in data[1] if isinstance(s, str)]
    rel = []
    for item in data[2:]:
        if isinstance(item, dict) and "google:suggestrelevance" in item:
            rel = item["google:suggestrelevance"]
            break
    return sugg, rel


def parse_osjson(body):
    if not body:
        return []
    try:
        data = json.loads(body)
    except Exception:
        return []
    if not isinstance(data, list) or len(data) < 2:
        return []
    second = data[1]
    if isinstance(second, list):
        out = []
        for s in second:
            if isinstance(s, str):
                out.append(s)
            elif isinstance(s, dict) and "phrase" in s:
                out.append(s["phrase"])
        return out
    return []


def query(engine, q, hl="en", gl="us", mkt="en-US"):
    url = ENDPOINTS[engine].format(q=urllib.parse.quote(q), hl=hl, gl=gl, mkt=mkt)
    body = fetch(url)
    if engine.startswith("google"):
        return parse_google(body)
    return parse_osjson(body), []


# ---------------------------------------------------------------- harvest
class Harvest:
    def __init__(self, hl, gl, workers):
        self.hl, self.gl = hl, gl
        self.workers = workers
        self.words = {}          # word -> record
        self.requests = 0

    def rec(self, w):
        w = re.sub(r"\s+", " ", w.strip().lower())
        if not w:
            return None
        if w not in self.words:
            self.words[w] = {
                "word": w,
                "engines": set(),
                "relevance": 0,
                "hits": 0,
                "via": set(),          # which seed/modifier surfaced it
                "position": [],        # rank in suggestion list
            }
        return self.words[w]

    def run_batch(self, tasks, label):
        """tasks: list of (engine, query_string). label explains provenance."""
        results = []
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = {ex.submit(query, e, q, self.hl, self.gl): (e, q) for e, q in tasks}
            for f in futs:
                e, q = futs[f]
                try:
                    sugg, rel = f.result()
                except Exception:
                    sugg, rel = [], []
                self.requests += 1
                results.append((e, q, sugg, rel))
                if self.requests % 80 == 0:
                    print(f"  ... {self.requests} requests, {len(self.words)} words", file=sys.stderr)
        for e, q, sugg, rel in results:
            for i, s in enumerate(sugg):
                r = self.rec(s)
                if not r:
                    continue
                r["engines"].add(e)
                r["hits"] += 1
                r["via"].add(label)
                r["position"].append(i + 1)
                if i < len(rel):
                    try:
                        r["relevance"] = max(r["relevance"], int(rel[i]))
                    except Exception:
                        pass
        print(f"  [{label}] {len(tasks)} req -> {len(self.words)} words total", file=sys.stderr)
        return results


def build_tasks(seeds, depth, engines):
    """Return (tasks, provenance_label) grouped so we can label provenance."""
    batches = []

    # level 1: bare seed, all engines
    t = [(e, s) for s in seeds for e in engines]
    batches.append((t, "seed"))

    if depth >= 2:
        # level 2: alphabet expansion on google_chrome + bing  (classic harvesting)
        t = []
        for s in seeds:
            for ch in ALPHABET:
                t.append(("google_chrome", f"{s} {ch}"))
                t.append(("bing", f"{s} {ch}"))
        batches.append((t, "alpha"))

    if depth >= 3:
        # level 3: intent suffix matrix on google_chrome + bing + ddg + yt
        t = []
        for s in seeds:
            for mod in INTENT_SUFFIX:
                for e in ("google_chrome", "bing", "ddg", "google_yt"):
                    t.append((e, s + mod))
        batches.append((t, "intent"))

    if depth >= 4:
        # level 4: question prefixes
        t = []
        for s in seeds:
            for pre in QUESTION_PREFIX:
                for e in ("google_chrome", "bing"):
                    t.append((e, pre + s))
        batches.append((t, "question"))

    return batches


# ---------------------------------------------------------------- analysis
INTENT_CLUSTERS = [
    ("weapons",     r"\bweapon|blade|sword|saber|phantom edge|armor|tier list|best (weapon|build)"),
    ("bosses",      r"\bboss|bosses|fight|parry|phase\b"),
    ("endings",     r"\bending|endings|true ending|final boss"),
    ("locations",   r"\bmanor|courtyard|region|area|temple|village|fortress|palace|forest|city|\bmap\b"),
    ("progression", r"\bnew game plus|ng\+|level cap|skill tree|respec|difficulty|walkthrough|chapter"),
    ("collect",     r"\bcollectible|missable|trophy|achievement|chest|key\b|location|where to|where is|where can"),
    ("platform",    r"\bps5|xbox|pc\b|steam|switch|requirements|demo|price|cd key|game pass"),
    ("release",     r"\brelease|out now|launch|pre ?order|deluxe|edition|dlc\b"),
    ("mechanic",    r"\bparry|combat|stamina|sha-chi|block|dodge|combos?\b|how to"),
    ("help",        r"\bbug|crash|fix|error|not working|black screen|lag|fps"),
    ("review",      r"\breview|metacritic|worth it|good\?|opinion|reddit"),
]

# How much a wiki site can actually win -- not how hot the query is.
# review/metacritic/steam/price are navigational or commercial intent: IGN and
# Steam own those SERPs, a fan wiki cannot rank there. guide/location/boss/
# trophy is informational deep intent, exactly where an entity wiki wins.
HIGH_VALUE = (r"\bguide|location|where|how to|boss|bosses|weapon|tier list|build|trophy|"
              r"achievement|ending|collectible|missable|map|walkthrough|new game plus|parry|"
              r"recipe|material|drop|secret|puzzle|\w+ key\b|all \w+")
MID_VALUE  = r"\bwiki|tips|explained|\ball\b|list|best|vs\b|difference|compare"
LOW_VALUE  = (r"\breview|metacritic|reddit|steam|ps5|xbox|pc\b|price|cd key|demo|download|"
              r"requirements|release|trailer|gameplay|cast|donnie yen|physical|disc|collector|"
              r"engine|news|youtube|sale|buy|worth it|^keys?$")

# These change the *page type*, so an existing category page does not cover
# them: /blades is a weapon list, it is not a weapon tier list, a build guide or
# a "where to find" page. Counting them as covered would hide the real gaps.
FORMAT_MODIFIERS = (r"\btier list|\bguide\b|walkthrough|\bhow to|location|\bwhere\b|\bbuild\b|"
                    r"\bbest\b|\ball\b|\bmap\b|\bexplained|\bvs\b|comparison")

# ---------------------------------------------------------------- profiles
# A morse-code site is not a game wiki: "key" there is a telegraph key, not a
# CD key; "map" is a code table, not a level map. Reusing the game rules would
# cluster every query wrong and misprice the intent, so each vertical gets its
# own cluster set and its own value ladder.
MORSE_CLUSTERS = [
    ("chart",     r"\bchart|alphabet|numbers?|punctuation|table|\blist\b|printable|pdf|reference"),
    ("letter",    r"\bin morse|^[a-z0-9]$|letter [a-z]|what is .* in morse"),
    ("learn",     r"\blearn|practice|beginner|how to|memor|stud|tutorial|course"),
    ("audio",     r"\baudio|sound|beep|tone|listen|mp3|wav|signal|frequency"),
    ("equipment", r"\bkey\b|keys\b|bug\b|paddle|oscillator|straight key|telegraph|radio"),
    ("decode",    r"\bdecode|decoder|transl|convert|encrypt|cipher|read"),
    ("in-games",  r"\bgame|puzzle|easter egg|titanfall|hoi4|minecraft|escape room|"
                  r"call of duty|battlefield|zelda|fallout|skyrim|among us|roblox"),
    ("history",   r"\bhistory|invented|samuel|origin|1844|timeline|who created"),
    ("exam",      r"\btest|exam|quiz|licen[cs]e|amateur radio|ham\b"),
]

MORSE_HIGH = (r"\bchart|alphabet|learn|how to|decode|decoder|transl|convert|\bkey\b|audio|"
              r"sound|beep|practice|beginner|number|punctuation|printable|in morse")
MORSE_MID  = r"\bguide|meaning|example|\ball\b|what is|explain"
MORSE_LOW  = r"\bhistory|invented|samuel|origin|who created|buy|price|amazon|for sale"
MORSE_FORMAT = r"\bchart|printable|pdf|sheet|table|alphabet|guide\b"

RULES = {}


def use_profile(name):
    global INTENT_CLUSTERS, HIGH_VALUE, MID_VALUE, LOW_VALUE, FORMAT_MODIFIERS
    if name == "morse":
        INTENT_CLUSTERS = MORSE_CLUSTERS
        HIGH_VALUE, MID_VALUE, LOW_VALUE = MORSE_HIGH, MORSE_MID, MORSE_LOW
        FORMAT_MODIFIERS = MORSE_FORMAT


def intent_value(core):
    if re.search(LOW_VALUE, core):
        return 1
    if re.search(HIGH_VALUE, core):
        return 3
    if re.search(MID_VALUE, core):
        return 2
    return 2


def strip_brand(word, brand_tokens):
    core = word
    for b in brand_tokens:
        core = core.replace(b, " ")
    return re.sub(r"\s+", " ", core).strip()


def is_off_brand(word, brand_tokens):
    """A query that shares the brand's first word but not its full phrase is a
    different product: 'phantom forces', 'phantom x', 'phantom armor' are not
    Phantom Blade Zero. Alphabet expansion drags these in constantly."""
    if not brand_tokens:
        return False
    full = max(brand_tokens, key=len)
    first = full.split()[0]
    return first in word and full not in word


def cluster_of(core):
    """Classify on the query MINUS the brand phrase. Otherwise 'blade' inside
    the game's own name labels every keyword a weapons query."""
    for name, pat in INTENT_CLUSTERS:
        if re.search(pat, core):
            return name
    return "other"


def load_slugs(site_root):
    """Page inventory, for gap matching. Supports both a JSON page store
    (src/data/pages/*.json) and Next.js app-router route folders (src/app/<slug>)."""
    slugs = set()
    d = os.path.join(site_root, "src", "data", "pages")
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".json"):
                slugs.add(f[:-5].lower())
    app = os.path.join(site_root, "src", "app")
    if os.path.isdir(app):
        for name in os.listdir(app):
            if os.path.isdir(os.path.join(app, name)) and not name.startswith(("(", "_", "[")):
                slugs.add(name.lower())
    return slugs


# query concepts that a differently-named page already owns
CONCEPT_ALIASES = {
    "weapon":     ["blades", "weapons"],
    "boss":       ["boss-list", "boss-guide", "bosses"],
    "trophy":     ["trophy-list", "trophy-guide"],
    "achievement": ["trophy-list", "trophy-guide", "achievements"],
    "build":      ["best-build", "best-builds"],
    "ending":     ["endings", "endings-explained"],
    "new game plus": ["new-game-plus"],
    # the homepage is the wiki; "phantom blade zero wiki" is not a content gap
    "wiki":       ["__home__"],
    "fandom":     ["__home__"],
}

HOME_SLUGS = {"__home__", "index", "home"}

# Queries whose concept is close enough to an existing page that the page can
# be extended rather than written from scratch. Keeping this separate from
# `covered` matters: "bosses ranked" is not a new page, it is a second view of
# an existing boss-order page, and it should not be quoted as greenfield work.
NEAR_BY_TOKEN = {
    "boss":    ["boss-order", "boss-list", "bosses", "boss-guide", "bosses-by-class"],
    "bosses":  ["boss-order", "boss-list", "bosses", "boss-guide", "bosses-by-class"],
    "ranked":  ["boss-order", "bosses-by-class", "tier-list", "weapons-tier-list"],
    "order":   ["boss-order"],
    "tier":    ["tier-list", "weapons-tier-list", "best-build", "best-builds"],
    "map":     ["interactive-map", "map"],
    "secret":  ["secrets", "endings"],
    "secrets": ["secrets", "endings"],
    "ending":  ["endings", "endings-explained"],
    "achievement": ["trophy-list", "trophy-guide"],
    "trophy":  ["trophy-list", "trophy-guide"],
    "decoder": ["morse-code-translator-to-english", "decode"],
    "translator": ["morse-code-translator-to-english", "decode"],
    "chart":   ["morse-code-chart-pdf", "american-morse-code-chart",
                "international-morse-code-chart", "chart"],
    "learn":   ["learn"],
    "audio":   ["audio"],
}


def near_page(core, slugs):
    """An existing page that covers part of the intent -- extend, don't rebuild."""
    for tok in [_norm(t) for t in core.split()]:
        for cand in NEAR_BY_TOKEN.get(tok, []):
            if cand in slugs:
                return cand
    return ""


def _norm(t):
    """crude singular form so 'endings' matches 'ending', 'builds' matches 'build'."""
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 3 and t.endswith("es") and not t.endswith("ses"):
        return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t


def covered(core, slugs, word=None):
    """Does an existing page already target this query's core concept?"""
    # match the page slug against the RAW query first: stripping the brand can
    # destroy the very phrase we need ("a in morse code" -> "a in")
    if word:
        for s in slugs:
            if len(s) > 4 and s.replace("-", " ") in word:
                return True
    if not core:
        return True  # pure brand query -> homepage
    toks = [_norm(t) for t in core.split()]
    sig = [t for t in toks if len(t) > 2]
    for s in slugs:
        if s.replace("-", " ") in core:
            return True
        parts = [_norm(p) for p in s.split("-")]
        # page name fully contained in the query
        if len(parts) >= 2 and all(p in toks for p in parts if len(p) > 2):
            return True
        # query fully covered by the page name ("endings" -> "endings-explained").
        # guard on sig: all() is True for an empty list, which would mark every
        # 1-2 letter query as covered.
        if sig and all(t in parts for t in sig):
            return True
    # a format modifier asks for a page type we don't have, even if the bare
    # category page exists
    if re.search(FORMAT_MODIFIERS, core):
        return False
    # concept aliases only rescue short queries. Otherwise 'builds act 2'
    # would be counted as covered just because a 'best-builds' page exists.
    if len([t for t in toks if len(t) > 2]) <= 1:
        for tok in toks:
            for alias in CONCEPT_ALIASES.get(tok, []):
                if alias in HOME_SLUGS or alias in slugs:
                    return True
    return False


def score(r):
    eng = len(r["engines"])
    # engine agreement dominates: independent sources proposing the same phrase
    s = eng * 12.0
    s += min(r["hits"], 30) * 1.8
    if min(r["position"] or [9]) <= 3:
        s += 4
    # weight by how winnable the intent is for a wiki, not just by heat
    s *= (0.55, 1.0, 1.15)[r["intent"] - 1]
    return round(s, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="")
    ap.add_argument("--seeds-file", default="")
    ap.add_argument("--brand", default="", help="brand tokens, comma separated, stripped before gap check")
    ap.add_argument("--site-root", default=".", help="repo root holding src/data/pages")
    ap.add_argument("--depth", type=int, default=2, choices=[1, 2, 3, 4])
    ap.add_argument("--hl", default="en")
    ap.add_argument("--gl", default="us")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-prefix", default="reports/kw")
    ap.add_argument("--min-engines", type=int, default=1)
    ap.add_argument("--max-seeds", type=int, default=40, help="cap seeds fed to deep levels")
    ap.add_argument("--allow-off-brand", action="store_true",
                    help="keep queries that share only the brand's first word "
                         "(use when the brand word alone is still your topic, e.g. 'morse')")
    ap.add_argument("--profile", default="game", choices=["game", "morse"],
                    help="which cluster set and intent ladder to use")
    args = ap.parse_args()

    seeds = []
    if args.seeds:
        seeds += [s.strip() for s in args.seeds.split("|") if s.strip()]
    if args.seeds_file:
        with open(args.seeds_file) as f:
            seeds += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not seeds:
        print("no seeds given", file=sys.stderr)
        return 2

    brand_tokens = [b.strip().lower() for b in args.brand.split(",") if b.strip()]
    use_profile(args.profile)
    slugs = load_slugs(args.site_root)

    print(f"seeds={len(seeds)} depth={args.depth} proxy={PROXY}", file=sys.stderr)
    h = Harvest(args.hl, args.gl, args.workers)

    # deep levels only on the first N seeds (they are the money terms);
    # the rest just get the bare query across all engines.
    primary = seeds[:args.max_seeds]
    rest = seeds[args.max_seeds:]

    batches = build_tasks(primary, args.depth, list(ENDPOINTS))
    if rest:
        batches.append(([(e, s) for s in rest for e in ENDPOINTS], "seed"))

    for tasks, label in batches:
        h.run_batch(tasks, label)

    # ---- score & write
    rows = []
    off_brand = 0
    for w, r in h.words.items():
        if len(r["engines"]) < args.min_engines:
            continue
        if not args.allow_off_brand and is_off_brand(w, brand_tokens):
            off_brand += 1
            continue
        core = strip_brand(w, brand_tokens)
        r["core"] = core
        r["intent"] = intent_value(core)
        r["score"] = score(r)
        r["cluster"] = cluster_of(core)
        r["is_brand"] = not core
        r["covered"] = covered(core, slugs, w)
        r["near"] = "" if r["covered"] else near_page(core, slugs)
        rows.append(r)
    rows.sort(key=lambda r: -r["score"])

    os.makedirs("reports", exist_ok=True)
    csv_path = f"{args.out_prefix}-raw.csv"
    with open(csv_path, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["word", "core_query", "score", "intent", "n_engines", "engines",
                     "hits", "best_pos", "cluster", "branded_only", "has_page", "near_page",
                     "found_via", "n_words"])
        for r in rows:
            wr.writerow([
                r["word"], r["core"], r["score"], r["intent"], len(r["engines"]),
                "|".join(sorted(r["engines"])), r["hits"], min(r["position"] or [0]),
                r["cluster"], int(r["is_brand"]), int(r["covered"]), r["near"],
                "|".join(sorted(r["via"])), len(r["word"].split()),
            ])
    print(f"\nwrote {csv_path} ({len(rows)} keywords)", file=sys.stderr)

    # ---- markdown digest
    md_path = f"{args.out_prefix}-digest.md"
    by_cluster = defaultdict(list)
    for r in rows:
        by_cluster[r["cluster"]].append(r)

    high_gaps = [r for r in rows if r["intent"] == 3 and not r["covered"] and len(r["engines"]) >= 2]
    all_gaps = [r for r in rows if not r["covered"] and len(r["engines"]) >= 2]

    def table(f, items, n=40):
        f.write("| # | query | score | eng | intent | cluster |\n|---|---|---|---|---|---|\n")
        for i, r in enumerate(items[:n], 1):
            f.write(f"| {i} | {r['word']} | {r['score']} | {len(r['engines'])} | "
                    f"{r['intent']} | {r['cluster']} |\n")

    with open(md_path, "w") as f:
        f.write(f"# Keyword research — {', '.join(primary[:3])}\n\n")
        f.write(f"- seeds: {len(seeds)} · depth: {args.depth} · locale: {args.hl}-{args.gl}\n")
        f.write(f"- requests: {h.requests} · unique suggestions: {len(h.words)} · "
                f"kept (>= {args.min_engines} engine): {len(rows)} · "
                f"off-brand dropped: {off_brand}\n\n")
        f.write("**Score** = (12 × engine agreement + 1.8 × times suggested + top-3 bonus) × intent weight.\n\n"
                "Engine agreement is weighted hardest: when Bing, Google, DuckDuckGo and YouTube "
                "independently propose the same phrase under different prefixes, people really type it. "
                "Intent weight multiplies 0.55 / 1.0 / 1.15 for low / mid / high wiki value, so a hot "
                "'metacritic' query does not outrank a cold 'boss location' one on a wiki site.\n\n")

        f.write(f"## 1. Highest-value demand with no page ({len(high_gaps)})\n\n"
                "High-value intent (guide / location / boss / weapon / trophy / build), at least two "
                "engines agree, and no existing page matches the core concept. This is the build list.\n\n")
        table(f, high_gaps, 50)

        f.write("\n## 2. Top 40 overall by score\n\n")
        table(f, rows, 40)

        f.write(f"\n## 3. All demand without a page ({len(all_gaps)})\n\n")
        table(f, all_gaps, 60)

        f.write("\n## 4. By cluster\n\n")
        for c, items in sorted(by_cluster.items(), key=lambda kv: -len(kv[1])):
            top = ", ".join(r["core"] or "(brand only)" for r in items[:8])
            f.write(f"- **{c}** ({len(items)}): {top}\n")

        f.write("\n## 5. Intent value distribution\n\n")
        for lvl, name in ((3, "high (winnable)"), (2, "mid"), (1, "low (IGN/Steam own it)")):
            sub = [r for r in rows if r["intent"] == lvl]
            f.write(f"- **{name}**: {len(sub)} queries, {sum(1 for r in sub if not r['covered'])} without a page\n")
    print(f"wrote {md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
