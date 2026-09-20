import Link from 'next/link';

const DESTINATIONS = [
  { href: '/release-date', label: 'Release Date', desc: 'October 29, 2026 on PS5 and PC' },
  { href: '/guide', label: 'Beginner Guide', desc: 'Combat and the 66-day premise' },
  { href: '/combat', label: 'Combat System', desc: 'Sha-chi, blades and Phantom Edges' },
  { href: '/s-game', label: 'Developer (S-GAME)', desc: 'Studio, team and history' },
  { href: '/weapons', label: 'Weapons', desc: 'Blades and secondary weapons' },
  { href: '/characters', label: 'Characters', desc: 'Soul and the cast' },
];

export default function NotFound() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="text-center mb-10">
        <p className="text-sm font-semibold text-accent mb-3">Error 404</p>
        <h1 className="text-3xl font-bold text-foreground mb-3">Page Not Found</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          This page does not exist yet. Phantom Blade Zero launches on October 29, 2026, so more of
          the wiki is still being written — start from one of these instead.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {DESTINATIONS.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className="block rounded-lg border border-border bg-card p-5 transition-colors hover:border-accent"
          >
            <div className="font-semibold text-foreground mb-1">{item.label}</div>
            <div className="text-sm text-muted-foreground">{item.desc}</div>
          </Link>
        ))}
      </div>

      <p className="text-center text-muted-foreground mt-10">
        Or start from the{' '}
        <Link href="/" className="text-accent underline">
          Phantom Blade Zero Wiki home page
        </Link>
        .
      </p>
    </div>
  );
}
