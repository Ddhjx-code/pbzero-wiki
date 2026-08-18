import fs from "fs";
import path from "path";

export interface PageSection {
  id: string;
  title: string;
  content: string;
}

export interface PageContent {
  slug: string;
  title: string;
  description: string;
  keyword: string;
  lastUpdated: string;
  sections: PageSection[];
}

const PAGES_DIR = path.join(process.cwd(), "src/data/pages");

const ALL_SLUGS = [
  "guide",
  "characters",
  "boss-guide",
  "weapons",
  "best-build",
  "skill-tree",
  "endings",
  "lore",
  "character-creation",
  "map",
];

export function getAllSlugs(): string[] {
  return ALL_SLUGS;
}

export function getPageContent(slug: string): PageContent | null {
  const filePath = path.join(PAGES_DIR, `${slug}.json`);
  if (!fs.existsSync(filePath)) {
    return null;
  }
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    const data = JSON.parse(raw) as Omit<PageContent, "slug">;
    return { slug, ...data };
  } catch {
    return null;
  }
}
