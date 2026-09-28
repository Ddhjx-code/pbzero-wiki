import Link from "next/link";
import { getTopicForSlug } from "@/lib/nav-topics";

export default function TopicNav({ currentSlug }: { currentSlug: string }) {
  const topic = getTopicForSlug(currentSlug);

  if (!topic) return null;

  return (
    <details className="fold mt-12" open aria-label={`${topic.label} navigation`}>
      <summary>
        {topic.label}
        <span className="ml-auto text-xs font-normal text-muted-foreground">
          {topic.pages.length} pages
        </span>
      </summary>
      <ul className="flex flex-wrap gap-x-3 gap-y-2 py-4">
        {topic.pages.map((page) => {
          const current = page.slug === currentSlug;
          return (
            <li key={page.slug}>
              <Link
                href={`/${page.slug}`}
                aria-current={current ? "page" : undefined}
                className={
                  current
                    ? "rounded border border-accent px-2 py-1 text-xs font-medium text-accent"
                    : "rounded border border-transparent px-2 py-1 text-xs text-muted-foreground transition-colors hover:border-border hover:text-accent"
                }
              >
                {page.title}
              </Link>
            </li>
          );
        })}
      </ul>
    </details>
  );
}
