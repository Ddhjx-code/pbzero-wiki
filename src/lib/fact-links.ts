const TOPIC_LINKS: ReadonlyArray<readonly [RegExp, string]> = [
  [/\bSha-chi\b/i, "/combat"],
  [/\bPhantom Edge/i, "/weapons"],
  [/\bSoul\b/, "/protagonist"],
  [/\bS-GAME\b/i, "/s-game"],
  [/\bPS5\b|\bPlayStation 5\b/i, "/release-date"],
  [/\bPC\b|\bSteam\b|\bEpic\b/i, "/release-date"],
];

export function linkFactValue(label: string, value: string): string | null {
  const l = label.trim().toLowerCase();

  if (l === "release date" || l === "platforms" || l === "developer" || l === "publisher") {
    return "/release-date";
  }
  if (l === "location" || l === "areas" || l === "region") {
    return "/guide";
  }
  if (l.includes("drop") || l === "reward" || l === "rewards") {
    return "/boss-guide";
  }
  if (l === "weak to" || l === "resists" || l === "absorbs" || l === "immune") {
    return "/combat";
  }
  if (l === "type" || l === "weapon type" || l === "class") {
    return "/weapons";
  }

  for (const [pattern, href] of TOPIC_LINKS) {
    if (pattern.test(value)) return href;
  }

  return null;
}
