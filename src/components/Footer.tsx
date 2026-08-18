export default function Footer() {
  return (
    <footer className="border-t border-border bg-card py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
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
