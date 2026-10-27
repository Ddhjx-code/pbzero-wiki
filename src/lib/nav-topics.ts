export interface NavPage {
  slug: string;
  title: string;
}

export interface NavTopic {
  label: string;
  pages: NavPage[];
}

export const TOPICS: NavTopic[] = [
  {
    label: "World & Exploration",
    pages: [
      { slug: "locations", title: "Locations & Regions" },
      { slug: "collectibles", title: "Collectibles" },
      { slug: "missable", title: "Missable Content" },
    ],
  },
  {
    label: "Weapons",
    pages: [
      { slug: "weapons", title: "Weapons Overview" },
      { slug: "phantom-edges", title: "Phantom Edges (Secondary)" },
    ],
  },
  {
    label: "Bosses",
    pages: [
      { slug: "boss-list", title: "Boss List" },
      { slug: "xiaokui-guarded-fight", title: "Mu Xiaokui + Escorts" },
      { slug: "changhong-boss", title: "Changhong" },
      { slug: "leidang-boss", title: "Lei Dang" },
      { slug: "the-hunt", title: "The Hunt" },
      { slug: "puppet-boss", title: "Puppet Boss" },
      { slug: "huangxing-boss", title: "Huangxing" },
      { slug: "seven-stars-boss", title: "Seven Stars" },
      { slug: "lion-dance-boss", title: "Lion Dance" },
      { slug: "drunken-sword-boss", title: "Drunken Sword" },
      { slug: "double-boss-fight", title: "Double Boss Fight" },
      { slug: "commander-cleave", title: "Commander Cleave" },
    ],
  },
  {
    label: "Getting Started",
    pages: [
      { slug: "reviews", title: "Reviews & Embargo" },
      { slug: "collectors-edition", title: "Collector's Edition" },
      { slug: "physical-edition", title: "Physical Edition" },
      { slug: "demo", title: "Is There a Demo?" },
      { slug: "platforms", title: "Platforms & Exclusivity" },
      { slug: "guide", title: "Beginner Guide" },
      { slug: "release-date", title: "Release Date" },
      { slug: "faq", title: "FAQ" },
      { slug: "is-phantom-blade-zero-a-soulslike", title: "Is It a Soulslike?" },
      { slug: "is-phantom-blade-zero-single-player", title: "Is It Single-Player?" },
      { slug: "pre-order-guide", title: "Pre-Order Guide" },
      { slug: "pc-requirements", title: "PC Requirements" },
      { slug: "how-long-to-beat", title: "How Long Is It?" },
      { slug: "about", title: "About the Game" },
    ],
  },
  {
    label: "Combat & Bosses",
    pages: [
      { slug: "best-build", title: "Best Build" },
      { slug: "combat", title: "Combat System" },
      { slug: "weapons", title: "Weapons & Phantom Edges" },
      { slug: "difficulty-modes", title: "Difficulty Modes" },
      { slug: "boss-guide", title: "Boss Guide" },
      { slug: "boss-video-guides", title: "Boss Video Guides" },
    ],
  },
  {
    label: "Story & Characters",
    pages: [
      { slug: "protagonist", title: "Soul (Protagonist)" },
      { slug: "characters", title: "All Characters" },
      { slug: "npcs", title: "NPCs" },
      { slug: "endings", title: "Endings" },
    ],
  },
  {
    label: "Studio",
    pages: [
      { slug: "s-game", title: "S-GAME" },
      { slug: "site-about", title: "About This Site" },
    ],
  },
];

export function getTopicForSlug(slug: string): NavTopic | undefined {
  return TOPICS.find((topic) => topic.pages.some((p) => p.slug === slug));
}
