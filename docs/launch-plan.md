# pbzero.wiki launch plan

Game: Phantom Blade Zero (S-GAME / Kepler Interactive)
Launch: **2026-10-29** for PS5 and PC (Steam, Epic). PS5 console exclusive for 12 months.
Pre-orders opened 2026-08-11. Delayed once, from 2026-09-09.
Pre-order bonus: Treasure Basin accessory + Legacy outfit, both also obtainable in-game.
Plan written 2026-09-28, 31 days before launch.

## Baseline

| Metric | Value |
| --- | --- |
| Pages | 15 |
| Words | 8,017 |
| Internal links | 14 |
| Links per 1,000 words | **1.7** |
| GSC impressions (18 days) | 2 |
| GSC clicks | 0 |
| Average position | 67 |

Reference point: expedition33.wiki sits at 44 links per 1,000 words after the
same work, and still only 22 impressions. A new domain needs weeks before
Google trusts it, so the skeleton has to be in place now, not on launch day.

## Why the window is one-shot

Search demand for a game wiki spikes on release day and stays elevated for
roughly a week. Indexing latency is measured in weeks for a young domain.
Content published on launch day cannot rank during the launch week. Everything
that can be written before launch must be live before launch.

## Phases

### P0 - Port the verified skeleton (09-28 to 09-30)

Copy the components and tooling already proven on expedition33.wiki rather than
redesigning them:

- `FactsCard` with linked field values
- `Breadcrumb`, `CategoryTags`, `PageSources` (the fixed page tail)
- `MobileToc`, `SubNav`, `TopicNav` (collapsible navbox)
- `SearchDialog` plus a generated search index
- `src/lib/autolink.ts`, `taxonomy.ts`, `fact-links.ts`, `nav-topics.ts`
- `scripts/gen-entity-pages.py` and `scripts/wire-entities.py`
- `src/data/entities/` data layer

Target: links per 1,000 words from 1.7 to 40 or better.

### P1 - Pre-launch content (09-30 to 10-08)

Queries with real volume today, answerable from official material:

- PC system requirements (DLSS 4.5, ray-traced reflections confirmed)
- Editions and whether pre-order is worth it; bonus items are farmable
- Release time and unlock schedule by region
- Single-player or co-op
- Playtime and difficulty
- Story premise, the Phantom World, Xuan paper art direction
- Character deep dives, combat systems, full weapon breakdown

### P2 - Launch-day ammunition (10-08 to 10-28)

Build templates and data schemas for bosses, weapons, quests, collectibles and
trophies, populated only where a source exists. Empty slots stay empty rather
than being filled with guesses.

### P3 - Launch week sprint (10-29 to 11-05)

Day-one guides driven by whatever is verifiable as the game opens: first-hours
walkthrough, first boss, starter builds, trophy list. Batch-generated through
the P0 pipeline.

## Rule carried over from expedition33.wiki

Where a value cannot be verified against a source, the page says so instead of
guessing. This is not relaxed for launch-week volume; unpublished game data
stays unpublished until it is real.
