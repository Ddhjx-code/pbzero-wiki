"use client";
import { useState } from "react";
import Link from "next/link";
import SearchDialog from "./SearchDialog";

// Order follows measured demand, not the site's original structure: the October
// 2026 US volumes were trophy guide 4,400, walkthrough 1,600, wiki 1,300, bosses
// 1,300, map 1,000. Trophy pages and the walkthrough were both missing from this
// bar entirely, which left the two biggest non-brand queries pointing at pages
// with no sitewide inbound link.
//
// Bosses and Weapons still point at the tier-2 databases rather than the strategy
// hubs: the database pages are what link out to all 60 boss pages and all 42
// blade/edge pages, so keeping them here gives every entity page at least one
// inbound link from every other page on the site.
const NAV_LINKS = [
  { href: "/walkthrough", label: "Walkthrough" },
  { href: "/boss-list", label: "Bosses" },
  { href: "/map", label: "Map" },
  { href: "/trophy-guide", label: "Trophies" },
  { href: "/blades", label: "Weapons" },
  { href: "/news", label: "News" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-sm">
      <nav className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-bold text-accent hover:text-accent-hover transition-colors"
        >
          <img src="/images/favicon.png" alt="" className="w-6 h-6" />
          <span>PBZero Wiki</span>
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-muted-foreground hover:text-accent transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        

        <SearchDialog />
<button
          type="button"
          className="md:hidden flex flex-col items-center justify-center w-8 h-8 gap-1.5"
          aria-label="Toggle navigation menu"
          onClick={() => setOpen(!open)}
        >
          <span className={`block h-0.5 w-5 bg-foreground transition-transform duration-200 ${open ? "rotate-45 translate-y-2" : ""}`} />
          <span className={`block h-0.5 w-5 bg-foreground transition-opacity duration-200 ${open ? "opacity-0" : ""}`} />
          <span className={`block h-0.5 w-5 bg-foreground transition-transform duration-200 ${open ? "-rotate-45 -translate-y-2" : ""}`} />
        </button>
      </nav>

      {open && (
        <div className="md:hidden border-t border-border bg-background px-4 py-4 space-y-3">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="block text-muted-foreground hover:text-accent transition-colors"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
