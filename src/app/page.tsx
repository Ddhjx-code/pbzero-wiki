import Link from "next/link";

const QUICK_LINKS = [
  { href: "/guide", emoji: "📖", title: "Beginner Guide", desc: "Combat mechanics & 66-day system" },
  { href: "/characters", emoji: "⚔️", title: "Characters", desc: "Soul, Mu Xiaokui, Zuo Shang & more" },
  { href: "/boss-guide", emoji: "💀", title: "Boss Guide", desc: "All known boss strategies" },
  { href: "/weapons", emoji: "🗡️", title: "Weapons", desc: "30+ weapons & Shachi system" },
];

const STATS = [
  { value: "30+", label: "Weapons" },
  { value: "4", label: "Playable Characters" },
  { value: "66", label: "Days to Live" },
  { value: "8+", label: "Endings" },
];

export default function HomePage() {
  return (
    <>
      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            name: "PBZero Wiki",
            url: "https://pbzero.wiki",
            description:
              "Complete Phantom Blade Zero wiki — guides, boss strategies, weapons, characters, and endings.",
            potentialAction: {
              "@type": "SearchAction",
              target: "https://pbzero.wiki/?q={search_term_string}",
              "query-input": "required name=search_term_string",
            },
          }),
        }}
      />

      {/* Hero */}
      <section className="relative overflow-hidden py-20 sm:py-28">
        {/* Background image */}
        <img
          src="/images/hero-bg.jpg"
          alt=""
          className="absolute inset-0 w-full h-full object-cover -z-30"
        />
        <div className="absolute inset-0 -z-20 bg-black/70" />
        {/* Layered atmospheric overlay */}
        <div className="absolute inset-0 -z-10 opacity-40 bg-[radial-gradient(ellipse_at_top,_var(--accent)_0%,_transparent_50%)]" />
        <div className="absolute inset-0 -z-10 opacity-15 bg-[radial-gradient(ellipse_at_bottom_right,_var(--accent-gold)_0%,_transparent_40%)]" />
        {/* Decorative slash lines */}
        <div className="absolute inset-0 -z-5 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-accent/30 to-transparent" />
          <div className="absolute top-2/3 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-accent-gold/20 to-transparent" />
        </div>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <p className="inline-block rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-accent">
            Releases October 29, 2026
          </p>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl text-balance">
            Phantom Blade Zero Wiki
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Your complete guide to combat, bosses, weapons, characters, and endings in S-Game&apos;s wuxia-punk action RPG.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            {STATS.map((stat) => (
              <span key={stat.label} className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                {stat.value} {stat.label}
              </span>
            ))}
          </div>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/guide"
              className="rounded-lg bg-accent px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-accent-hover"
            >
              Beginner Guide
            </Link>
            <Link
              href="/characters"
              className="rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-card-foreground transition-colors hover:border-accent"
            >
              Characters
            </Link>
            <Link
              href="/boss-guide"
              className="rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-card-foreground transition-colors hover:border-accent"
            >
              Boss Guide
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-foreground sm:text-3xl">
            Where to Start
          </h2>
          <p className="mt-2 text-muted-foreground">
            Pick a guide to jump right in.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {QUICK_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="group relative rounded-xl border border-border bg-card p-6 transition-all hover:border-accent hover:shadow-md"
              >
                <span className="text-2xl">{link.emoji}</span>
                <h3 className="mt-3 text-lg font-semibold text-card-foreground group-hover:text-accent transition-colors">
                  {link.title}
                </h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {link.desc}
                </p>
                <span className="mt-4 inline-flex items-center text-sm font-medium text-accent opacity-0 transition-opacity group-hover:opacity-100">
                  Read more →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Game visual banner */}
      <section className="py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="overflow-hidden rounded-xl border border-border bg-gradient-to-r from-[#1a0a0a] via-[#0f0f1a] to-[#0a0a15] p-8 sm:p-12 relative">
            <div className="absolute inset-0 opacity-5 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMSIgZmlsbD0id2hpdGUiLz48L3N2Zz4=')]" />
            <div className="relative flex flex-col sm:flex-row items-center gap-8">
              <div className="flex-shrink-0 w-32 h-32 rounded-lg border border-accent/20 overflow-hidden">
                <img src="/images/poster.webp" alt="Phantom Blade Zero" className="w-full h-full object-cover" />
              </div>
              <div>
                <p className="text-accent-gold text-sm font-semibold uppercase tracking-wider">Wuxia-Punk Action RPG</p>
                <h2 className="mt-2 text-2xl font-bold text-foreground">影之刃零</h2>
                <p className="mt-2 text-muted-foreground">By S-Game • Unreal Engine 5 • Donnie Yen Motion Capture</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <span className="px-3 py-1 text-xs rounded-full border border-accent/30 text-accent bg-accent/5">Action RPG</span>
                  <span className="px-3 py-1 text-xs rounded-full border border-accent-gold/30 text-accent-gold bg-accent-gold/5">Wuxia</span>
                  <span className="px-3 py-1 text-xs rounded-full border border-border text-muted-foreground">Single Player</span>
                  <span className="px-3 py-1 text-xs rounded-full border border-border text-muted-foreground">PS5 / PC</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About */}
      <section className="py-16 border-t border-border">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-12 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <h2 className="text-2xl font-bold text-foreground sm:text-3xl">
                About the Game
              </h2>
              <div className="mt-4 space-y-4">
                <p className="text-muted-foreground leading-relaxed">
                  Phantom Blade Zero is a third-person action RPG set in a wuxia-punk world called the Shadow Realm. Developed by S-Game with Unreal Engine 5 and martial arts choreography by Donnie Yen.
                </p>
                <p className="text-muted-foreground leading-relaxed">
                  You play as Soul, an elite assassin framed for murder and left with only 66 days to live. Master fast-paced combat combining 30+ weapons, 20+ Phantom Edges, and fluid martial arts combos to uncover the truth before time runs out.
                </p>
              </div>
            </div>
            <div className="flex flex-col justify-center">
              <div className="grid grid-cols-2 gap-4">
                {[
                  { value: "UE5", label: "Engine" },
                  { value: "PS5/PC", label: "Platforms" },
                  { value: "S-Game", label: "Developer" },
                  { value: "Oct 2026", label: "Release" },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="rounded-lg border border-border bg-card p-4 text-center"
                  >
                    <p className="text-2xl font-bold text-accent">{item.value}</p>
                    <p className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">
                      {item.label}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
