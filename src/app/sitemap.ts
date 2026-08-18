import { MetadataRoute } from "next";
import { getAllSlugs } from "@/lib/content";

const BASE_URL = "https://pbzero.wiki";

export default function sitemap(): MetadataRoute.Sitemap {
  const slugPages = getAllSlugs().map((slug) => ({
    url: `${BASE_URL}/${slug}`,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

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
