import { MetadataRoute } from "next";
import { getAllSlugs, getPageContent } from "@/lib/content";

const BASE_URL = "https://pbzero.wiki";

// lastModified has to be the date the page actually changed. Emitting the build
// time on every URL tells Google that all 185 pages changed at once every time
// anything ships, which is the fastest way to get lastmod ignored entirely.
export default function sitemap(): MetadataRoute.Sitemap {
  const slugPages = getAllSlugs().map((slug) => {
    const page = getPageContent(slug);
    const updated = page?.lastUpdated ? new Date(`${page.lastUpdated}T12:00:00Z`) : undefined;
    return {
      url: `${BASE_URL}/${slug}`,
      lastModified: updated && !Number.isNaN(updated.getTime()) ? updated : undefined,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    };
  });

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    ...slugPages,
  ];
}
