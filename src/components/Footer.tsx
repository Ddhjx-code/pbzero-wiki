import Link from "next/link";

// Sitewide internal links to the tier-2 hub pages. Before this block the footer
// carried only social links and legal pages, which meant the 130-odd entity pages
// (60 bosses, 42 weapons, 36 trophies) had no path from a crawled page except
// through the hub that happened to list them. Google had discovered them and never
// crawled them; a footer that links every hub from every page is the cheapest fix
// for that, and it also gives the new /map page a sitewide inbound link.
const FOOTER_GROUPS: { heading: string; links: { href: string; label: string }[] }[] = [
  {
    heading: "Start here",
    links: [
      { href: "/guide", label: "Beginner Guide" },
      { href: "/walkthrough", label: "Walkthrough" },
      { href: "/faq", label: "FAQ" },
      { href: "/difficulty-modes", label: "Difficulty Modes" },
      { href: "/how-long-to-beat", label: "How Long to Beat" },
      { href: "/patch-notes", label: "Patch Notes" },
    ],
  },
  {
    heading: "Bosses & combat",
    links: [
      { href: "/boss-list", label: "All Bosses" },
      { href: "/boss-order", label: "Boss Order" },
      { href: "/boss-guide", label: "Boss Strategies" },
      { href: "/combat", label: "Combat System" },
      { href: "/blades", label: "Blades" },
      { href: "/phantom-edges", label: "Phantom Edges" },
      { href: "/best-build", label: "Best Build" },
    ],
  },
  {
    heading: "World & map",
    links: [
      { href: "/map", label: "Map & Regions" },
      { href: "/locations", label: "Locations" },
      { href: "/collectibles", label: "Collectibles" },
      { href: "/missable", label: "Missable Content" },
      { href: "/side-quests", label: "Side Quests" },
      { href: "/characters", label: "Characters" },
    ],
  },
  {
    heading: "Completion",
    links: [
      { href: "/trophy-guide", label: "Trophy Guide" },
      { href: "/trophy-list", label: "Trophy List" },
      { href: "/endings", label: "Endings" },
      { href: "/true-ending", label: "True Ending" },
      { href: "/weapons", label: "Weapons" },
      { href: "/news", label: "News" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-border bg-card py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <nav
          aria-label="Site sections"
          className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4"
        >
          {FOOTER_GROUPS.map((group) => (
            <div key={group.heading}>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                {group.heading}
              </h3>
              <ul className="mt-2 space-y-2 text-sm">
                {group.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-muted-foreground hover:text-accent transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className="mt-10 grid gap-8 border-t border-border pt-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
              PBZero Wiki
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Community-driven Phantom Blade Zero guide &amp; wiki.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
              Community
            </h3>
            <ul className="mt-2 space-y-2 text-sm">
              <li>
                <a
                  href="https://store.steampowered.com/app/4115450/Phantom_Blade_Zero/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  Steam Store Page
                </a>
              </li>
              <li>
                <a
                  href="https://www.reddit.com/r/PhantomBladeZero/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  r/PhantomBladeZero
                </a>
              </li>
              <li>
                <a
                  href="https://x.com/pbzero_official"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  @pbzero_official
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
              Site
            </h3>
            <ul className="mt-2 space-y-2 text-sm">
              <li>
                <Link
                  href="/site-about"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  About Us
                </Link>
              </li>
              <li>
                <Link
                  href="/privacy-policy"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-muted-foreground hover:text-accent transition-colors"
                >
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
              Disclaimer
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Fan-made wiki. Not affiliated with S-Game or any official entity.
            </p>
          </div>
        </div>
        <div className="mt-8 border-t border-border pt-6 text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} PBZero Wiki. Game content belongs to S-Game.
        </div>
      </div>
    </footer>
  );
}
