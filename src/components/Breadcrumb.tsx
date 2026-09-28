import Link from "next/link";
import { getBreadcrumbs } from "@/lib/taxonomy";

interface BreadcrumbProps {
  slug: string;
  title: string;
}

export default function Breadcrumb({ slug, title }: BreadcrumbProps) {
  const trail = getBreadcrumbs(slug, title);
  if (trail.length < 2) return null;

  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
        {trail.map((crumb, i) => {
          const last = i === trail.length - 1;
          return (
            <li key={`${crumb.label}-${i}`} className="flex items-center gap-2">
              {crumb.href && !last ? (
                <Link href={crumb.href} className="hover:text-accent transition-colors">
                  {crumb.label}
                </Link>
              ) : (
                <span className={last ? "text-foreground" : undefined} aria-current={last ? "page" : undefined}>
                  {crumb.label}
                </span>
              )}
              {!last && <span aria-hidden="true">/</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
