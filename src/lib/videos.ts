import fs from "fs";
import path from "path";

export interface VideoTimestamp {
  at: string;
  label: string;
}

export interface VideoEntry {
  title: string;
  channel: string;
  url: string;
  duration?: string;
  covers?: string;
  bestFor?: string;
  caveat?: string;
  timestamps?: VideoTimestamp[];
}

export type VideoMap = Record<string, VideoEntry[]>;

const DATA_FILE = path.join(process.cwd(), "src/data/videos.json");

export function loadVideos(): VideoMap {
  if (!fs.existsSync(DATA_FILE)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8")) as VideoMap;
  } catch {
    return {};
  }
}

export function videosFor(slug: string): VideoEntry[] {
  return loadVideos()[slug] ?? [];
}
