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
    label: "Getting Started",
    pages: [
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
