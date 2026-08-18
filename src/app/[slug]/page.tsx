import { Metadata } from "next";
import { getAllSlugs, getPageContent } from "@/lib/content";
import RelatedPages from "@/components/RelatedPages";

const BASE_URL = "https://pbzero.wiki";

interface PageProps {
  params: { slug: string };
}

export function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }));
}

export function generateMetadata({ params }: PageProps): Metadata {
  const content = getPageContent(params.slug);
  const title = content?.title || params.slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  const description = content?.description || `${title} - Phantom Blade Zero Wiki guide.`;

  return {
    title,
    description,
    keywords: [content?.keyword || params.slug, "Phantom Blade Zero", "PBZ"],
    alternates: { canonical: `${BASE_URL}/${params.slug}` },
    openGraph: {
      title,
      description,
      url: `${BASE_URL}/${params.slug}`,
      siteName: "PBZero Wiki",
      type: "article",
    },
  };
}

export default function SlugPage({ params }: PageProps) {
  const content = getPageContent(params.slug);

  if (!content) {
    const title = params.slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-foreground mb-4">{title}</h1>
        <div className="rounded-lg border border-border bg-card p-6">
          <p className="text-muted-foreground">
            This guide is being prepared. Full content will be available at launch (October 29, 2026).
          </p>
        </div>
        <RelatedPages currentSlug={params.slug} />
      </div>
    );
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: content.title,
            description: content.description,
            dateModified: content.lastUpdated,
            url: `${BASE_URL}/${params.slug}`,
            publisher: { "@type": "Organization", name: "PBZero Wiki" },
          }),
        }}
      />
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Page header with visual */}
        <header className="mb-8 relative overflow-hidden rounded-xl border border-border bg-gradient-to-r from-card via-[#1a0a10] to-card p-6 sm:p-8">
          <div className="absolute top-0 right-0 w-32 h-32 opacity-10 bg-[radial-gradient(circle,_var(--accent)_0%,_transparent_70%)]" />
          <h1 className="text-3xl font-bold text-foreground mb-2 relative">
            {content.title}
          </h1>
          <p className="text-sm text-muted-foreground relative">
            Last updated: {content.lastUpdated}
          </p>
        </header>

        <div className="space-y-8">
          {content.sections.map((section) => (
            <section key={section.id} id={section.id}>
              <h2 className="text-xl font-semibold text-foreground mb-3 scroll-mt-20">
                {section.title}
              </h2>
              <div
                className="prose prose-sm prose-invert max-w-none text-muted-foreground leading-relaxed [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-border [&_th]:bg-card [&_th]:px-3 [&_th]:py-2 [&_th]:text-left [&_th]:text-foreground [&_td]:border [&_td]:border-border [&_td]:px-3 [&_td]:py-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:mb-1 [&_h3]:text-foreground [&_h3]:font-semibold [&_h3]:mt-4 [&_h3]:mb-2 [&_strong]:text-foreground [&_a]:text-accent [&_a]:underline [&_p]:mb-3"
                dangerouslySetInnerHTML={{ __html: section.content }}
              />
            </section>
          ))}
        </div>

        <RelatedPages currentSlug={params.slug} />
      </div>
    </>
  );
}
