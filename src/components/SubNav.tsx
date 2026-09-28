import Link from "next/link";
import { getSectionLinks } from "@/lib/taxonomy";

interface SubNavProps {
  slug: string;
}

export default function SubNav({ slug }: SubNavProps) {
  const links = getSectionLinks(slug);
  if (links.length === 0) return null;

  return (
    <nav
      aria-label="Section"
      className="mb-6 flex flex-wrap items-center gap-2 border-b border-border pb-4"
    >
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="rounded-md border border-border bg-card px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-accent hover:text-accent"
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
