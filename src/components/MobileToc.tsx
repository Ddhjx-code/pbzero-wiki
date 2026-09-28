import Link from "next/link";
import { PageSection } from "@/lib/content";

interface MobileTocProps {
  sections: PageSection[];
}

export default function MobileToc({ sections }: MobileTocProps) {
  if (sections.length === 0) return null;

  return (
    <details className="fold mb-8 lg:hidden">
      <summary>
        On this page
        <span className="ml-auto text-xs font-normal text-muted-foreground">
          {sections.length} sections
        </span>
      </summary>
      <ol className="list-none space-y-1.5 py-3 text-sm">
        {sections.map((section, i) => (
          <li key={section.id} className="flex gap-2">
            <span className="text-muted-foreground/60 tabular-nums">
              {i + 1}.
            </span>
            <a
              href={`#${section.id}`}
              className="text-muted-foreground transition-colors hover:text-accent"
            >
              {section.title}
            </a>
          </li>
        ))}
      </ol>
      <div className="border-t border-border px-4 py-3">
        <Link
          href="/boss-guide"
          className="text-sm text-muted-foreground transition-colors hover:text-accent"
        >
          All bosses in order &rarr;
        </Link>
      </div>
    </details>
  );
}
