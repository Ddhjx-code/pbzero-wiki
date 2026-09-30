interface PageSourcesProps {
  lastUpdated: string;
  game: string;
}

export default function PageSources({ lastUpdated, game }: PageSourcesProps) {
  return (
    <section aria-label="Sources" className="mt-12 border-t border-border pt-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Sources &amp; verification
      </h2>
      <ul className="space-y-2 text-xs leading-relaxed text-muted-foreground">
        <li>
          Compiled from official {game} material and cross-checked against
          independent coverage where it exists.
        </li>
        <li>
          Figures that could not be confirmed against a second source are left
          out of this page rather than estimated. Where a page says
          &ldquo;not confirmed&rdquo;, that is deliberate.
        </li>
        <li>
          Before release, this site describes announced content only. Boss
          strategies, drop tables and playtime are marked unconfirmed rather
          than guessed, and are updated as the shipped game allows them to be
          verified.
        </li>
        <li>Last reviewed: {lastUpdated}</li>
      </ul>
    </section>
  );
}
