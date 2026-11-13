import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import "./globals.css";

const GA_MEASUREMENT_ID = "G-W9Y62B3DBM";

const BASE_URL = "https://pbzero.wiki";

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: {
    default: "Phantom Blade Zero Wiki - Guides, Builds & Boss Strategies",
    template: "%s | PBZero Wiki",
  },
  description:
    "Complete Phantom Blade Zero wiki. Boss guides, weapon list, character builds, skill tree, endings walkthrough, and combat tips for the action RPG by S-Game.",
  keywords: [
    "Phantom Blade Zero",
    "PBZ",
    "wiki",
    "boss guide",
    "weapons",
    "characters",
    "skill tree",
    "endings",
    "builds",
    "S-Game",
  ],
  alternates: {
    canonical: BASE_URL,
  },
  openGraph: {
    title: "Phantom Blade Zero Wiki - Guides, Builds & Boss Strategies",
    description: "Complete Phantom Blade Zero wiki. Boss guides, weapon list, character builds, skill tree, endings walkthrough, and combat tips.",
    type: "website",
    locale: "en_US",
    siteName: "PBZero Wiki",
    url: BASE_URL,
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Phantom Blade Zero Wiki",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Phantom Blade Zero Wiki - Guides, Builds & Boss Strategies",
    description: "Complete Phantom Blade Zero wiki. Boss guides, weapon list, character builds, skill tree, endings walkthrough, and combat tips.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      name: "PBZero Wiki",
      url: BASE_URL,
      description: "Complete guide for Phantom Blade Zero - bosses, weapons, builds, endings, and combat tips.",
    },
    {
      "@type": "VideoGame",
      name: "Phantom Blade Zero",
      genre: "Action RPG",
      gamePlatform: ["PC", "PlayStation 5"],
      publisher: { "@type": "Organization", name: "S-Game" },
      description: "A martial arts action RPG set in a dark fantasy world inspired by Chinese wuxia.",
    },
  ],
};

// The FAQPage block used to live here, which meant all 185 pages claimed to be
// an FAQ about the same three questions - structured data that does not match
// the visible page is what gets rich results dropped. It is now emitted on /faq
// only, from that page's own question headings.

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <script
          async
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${GA_MEASUREMENT_ID}');
            `,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
