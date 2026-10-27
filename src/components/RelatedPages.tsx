import Link from "next/link";

const ALL_PAGES = [
  { slug: "guide", title: "Beginner Guide", description: "Combat & 66-day system" },
  { slug: "characters", title: "Characters", description: "All playable characters" },
  { slug: "boss-list", title: "Boss List", description: "Every boss named so far" },
  { slug: "boss-guide", title: "Boss Guide", description: "Every boss strategy" },
  { slug: "weapons", title: "Weapons", description: "Weapons & Sha-chi upgrade paths" },
  { slug: "combat", title: "Combat", description: "Parry, dodge & Sha-chi stances" },
  { slug: "news", title: "News & Updates", description: "Dated official announcements" },
  { slug: "release-date", title: "Release Date", description: "Launch info & platforms" },
  { slug: "reviews", title: "Reviews", description: "Metacritic 88, OpenCritic 91" },
  { slug: "collectors-edition", title: "Collector's Edition", description: "The ¥1,199 box has no disc" },
  { slug: "locations", title: "Locations", description: "Every named region" },
  { slug: "missable", title: "Missable Content", description: "What you can permanently skip" },
  { slug: "collectibles", title: "Collectibles", description: "Every type and what each does" },
  { slug: "platforms", title: "Platforms", description: "PS5, PC, Xbox, Switch" },
  { slug: "demo", title: "Playable Demo", description: "Does a demo exist?" },
  { slug: "physical-edition", title: "Physical Edition", description: "Disc at launch: no. 2027: yes" },
  { slug: "s-game", title: "S-Game", description: "Studio behind the game" },
  { slug: "protagonist", title: "Protagonist", description: "Soul, the 66-day assassin" },
  { slug: "endings", title: "Endings", description: "Eight claimed, none confirmed" },
];

function rotateFrom(slug: string) {
  const start = ALL_PAGES.findIndex((p) => p.slug === slug) + 1;
  return [...ALL_PAGES.slice(start), ...ALL_PAGES.slice(0, start)];
}

export default function RelatedPages({ currentSlug }: { currentSlug: string }) {
  const related = rotateFrom(currentSlug)
    .filter((p) => p.slug !== currentSlug)
    .slice(0, 4);
  return (
    <nav className="mt-12 border-t border-border pt-8" aria-label="Related guides">
      <h2 className="text-lg font-semibold text-foreground mb-4">Related Guides</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {related.map((page) => (
          <Link
            key={page.slug}
            href={`/${page.slug}`}
            className="group rounded-lg border border-border bg-card p-4 transition-all hover:border-accent hover:shadow-sm"
          >
            <h3 className="font-medium text-card-foreground group-hover:text-accent transition-colors">
              {page.title}
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">{page.description}</p>
          </Link>
        ))}
      </div>
    </nav>
  );
}
