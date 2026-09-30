const ENTITY_LINKS: ReadonlyArray<readonly [RegExp, string]> = [
  // Systems
  [/\bSha-chi\b/, "/combat"],
  [/\bPhantom Edges?\b/i, "/weapons"],
  // Characters
  [/\bSoul\b/, "/protagonist"],
  [/\bMu Xiaokui\b/, "/characters"],
  [/\bMu Tianmiao\b/, "/characters"],
  [/\bZuo Shang\b/, "/characters"],
  [/\bHellwalkers?\b/, "/characters"],
  [/\bMystic Healer\b/, "/characters"],
  [/\bWayfarers?\b/, "/characters"],
  [/\bThe Order\b/, "/characters"],
  // Weapon types
  [/\bRegular Sword\b/, "/weapons"],
  [/\bLong Sword\b/, "/weapons"],
  [/\bDual Swords\b/, "/weapons"],
  // World & framing
  [/\bPhantom World\b/, "/guide"],
  [/\bKungfu\s?Punk\b/i, "/guide"],
  [/\bSixty-Six Days\b/, "/release-date"],
  [/\bsoulslike\b/i, "/is-phantom-blade-zero-a-soulslike"],
  // Pre-launch info pages
  [/\bWayfarer\b/, "/difficulty-modes"],
  [/\bHellwalker\b/, "/difficulty-modes"],
  [/\bsingle-player\b/i, "/is-phantom-blade-zero-single-player"],
  [/\bpre-order(?:ing)?\b/i, "/pre-order-guide"],
  [/\bDLSS\b/, "/pc-requirements"],
  [/\bUnreal Engine 5\b/, "/pc-requirements"],
  [/\bEpic Games Store\b/, "/pre-order-guide"],
  [/\bsystem requirements\b/i, "/pc-requirements"],
  // Studio
  [/\bS-GAME\b/, "/s-game"],
];

const SKIP_TAGS = new Set([
  "a",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "code",
  "pre",
  "button",
  "script",
  "style",
]);

const TAG_NAME = /^<\s*(\/?)\s*([a-zA-Z][a-zA-Z0-9]*)/;

function linkifyRun(run: string, currentSlug: string, used: Set<number>): string {
  const out: string[] = [];
  let cursor = 0;

  while (cursor < run.length) {
    let bestIndex = -1;
    let bestRule = -1;
    let bestText = "";

    for (let i = 0; i < ENTITY_LINKS.length; i++) {
      if (used.has(i)) continue;
      const [pattern, href] = ENTITY_LINKS[i];
      if (href.slice(1) === currentSlug) continue;

      const match = pattern.exec(run.slice(cursor));
      if (!match || match.index === undefined) continue;

      const at = cursor + match.index;
      if (bestIndex === -1 || at < bestIndex) {
        bestIndex = at;
        bestRule = i;
        bestText = match[0];
      }
    }

    if (bestRule === -1) break;

    const href = ENTITY_LINKS[bestRule][1];
    out.push(run.slice(cursor, bestIndex));
    out.push(
      `<a href="${href}" style="color:var(--accent);text-decoration:underline;text-underline-offset:2px">${bestText}</a>`
    );
    cursor = bestIndex + bestText.length;
    used.add(bestRule);
  }

  out.push(run.slice(cursor));
  return out.join("");
}

/**
 * Turn the first mention of each known entity in a page's body copy into an
 * internal link. Headings, existing anchors and code blocks are left alone so
 * links never nest and the outline stays clean.
 */
export function autoLink(html: string, currentSlug: string): string {
  const used = new Set<number>();
  const skipStack: string[] = [];
  const tokens = html.split(/(<[^>]+>)/);
  const out: string[] = [];

  for (const token of tokens) {
    if (token.startsWith("<")) {
      const match = TAG_NAME.exec(token);
      if (match) {
        const isClosing = match[1] === "/";
        const tag = match[2].toLowerCase();
        if (SKIP_TAGS.has(tag)) {
          if (isClosing) {
            const at = skipStack.lastIndexOf(tag);
            if (at >= 0) skipStack.splice(at, 1);
          } else if (!token.endsWith("/>")) {
            skipStack.push(tag);
          }
        }
      }
      out.push(token);
      continue;
    }

    if (skipStack.length > 0 || token.trim() === "") {
      out.push(token);
      continue;
    }

    out.push(linkifyRun(token, currentSlug, used));
  }

  return out.join("");
}
