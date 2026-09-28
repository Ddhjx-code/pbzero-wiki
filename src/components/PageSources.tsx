interface PageSourcesProps {
  lastUpdated: string;
}

export default function PageSources({ lastUpdated }: PageSourcesProps) {
  return (
    <section aria-label="Sources" className="mt-12 border-t border-border pt-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Sources &amp; verification
      </h2>
      <ul className="space-y-2 text-xs leading-relaxed text-muted-foreground">
        <li>
          Compiled from official Clair Obscur: Expedition 33 material and
          cross-checked against multiple independent community references.
        </li>
        <li>
          Numbers that could not be confirmed against a second source are left
          out of this page rather than estimated. Where a page says &ldquo;not
          documented&rdquo;, that is deliberate.
        </li>
        <li>Last reviewed: {lastUpdated}</li>
      </ul>
    </section>
  );
}
