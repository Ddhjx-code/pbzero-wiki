export interface Crumb {
  label: string;
  href?: string;
}

export interface Category {
  label: string;
  href: string;
}

interface SectionDef {
  label: string;
  href: string;
  slugs: Set<string>;
  category: string;
}

const SECTIONS: SectionDef[] = [
  {
    label: "Getting Started",
    href: "/guide",
    slugs: new Set(["guide", "faq", "release-date", "is-phantom-blade-zero-a-soulslike", "about"]),
    category: "Beginner guides",
  },
  {
    label: "Combat & Bosses",
    href: "/combat",
    slugs: new Set(["combat", "weapons", "boss-guide", "boss-video-guides"]),
    category: "Combat & Bosses",
  },
  {
    label: "Story & Characters",
    href: "/characters",
    slugs: new Set(["characters", "protagonist", "endings"]),
    category: "Characters & Story",
  },
  {
    label: "Studio",
    href: "/s-game",
    slugs: new Set(["s-game"]),
    category: "Studio",
  },
];

const SECTION_LINKS: Record<string, { label: string; href: string }[]> = {
  "Getting Started": [
    { label: "Beginner Guide", href: "/guide" },
    { label: "Release Date", href: "/release-date" },
    { label: "FAQ", href: "/faq" },
    { label: "Is It a Soulslike?", href: "/is-phantom-blade-zero-a-soulslike" },
  ],
  "Combat & Bosses": [
    { label: "Combat System", href: "/combat" },
    { label: "Weapons", href: "/weapons" },
    { label: "Boss Guide", href: "/boss-guide" },
    { label: "Boss Video Guides", href: "/boss-video-guides" },
  ],
  "Story & Characters": [
    { label: "All Characters", href: "/characters" },
    { label: "Soul", href: "/protagonist" },
    { label: "Endings", href: "/endings" },
  ],
  Studio: [
    { label: "S-GAME", href: "/s-game" },
    { label: "About This Site", href: "/site-about" },
  ],
};

const LEGAL_SLUGS = new Set(["about", "contact", "privacy-policy", "site-about"]);

function sectionFor(slug: string): SectionDef | undefined {
  return SECTIONS.find((s) => s.slugs.has(slug));
}

function shortTitle(title: string): string {
  return title.split(/\s+[-—|]\s+/)[0].trim() || title;
}

export function getBreadcrumbs(slug: string, title: string): Crumb[] {
  const section = sectionFor(slug);
  const trail: Crumb[] = [{ label: "Home", href: "/" }];
  if (section) trail.push({ label: section.label, href: section.href });
  trail.push({ label: shortTitle(title) });
  return trail;
}

export function getCategories(slug: string, title: string): Category[] {
  if (LEGAL_SLUGS.has(slug)) return [];

  const cats: Category[] = [];
  const section = sectionFor(slug);
  if (section) cats.push({ label: section.category, href: section.href });

  if (slug === "boss-guide" || slug === "combat" || slug === "weapons") {
    cats.push({ label: "Pre-launch coverage", href: "/release-date" });
  }
  if (slug === "endings") {
    cats.push({ label: "Spoiler territory", href: "/endings" });
  }

  cats.push({ label: shortTitle(title), href: `/${slug}` });

  return cats.filter((c, i, a) => a.findIndex((x) => x.href === c.href) === i);
}

export function getSectionLinks(slug: string): { label: string; href: string }[] {
  for (const [, links] of Object.entries(SECTION_LINKS)) {
    if (links.some((l) => l.href.slice(1) === slug)) return [];
  }
  const section = sectionFor(slug);
  if (!section) return [];
  return SECTION_LINKS[section.label] ?? [];
}
