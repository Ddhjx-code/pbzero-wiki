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

export function getAllSlugs(): string[] {
  if (!fs.existsSync(PAGES_DIR)) {
    return [];
  }
  return fs
    .readdirSync(PAGES_DIR)
    .filter((file) => file.endsWith(".json"))
    .map((file) => file.replace(/\.json$/, ""));
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
