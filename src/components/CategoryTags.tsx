import Link from "next/link";
import { getCategories } from "@/lib/taxonomy";

interface CategoryTagsProps {
  slug: string;
  title: string;
}

export default function CategoryTags({ slug, title }: CategoryTagsProps) {
  const categories = getCategories(slug, title);
  if (categories.length === 0) return null;

  return (
    <nav aria-label="Categories" className="mt-12 border-t border-border pt-6">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Categories
      </h2>
      <ul className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <li key={category.href}>
            <Link
              href={category.href}
              className="inline-flex items-center rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-accent hover:text-accent"
            >
              {category.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
