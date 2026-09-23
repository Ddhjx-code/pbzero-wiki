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
    {
      "@type": "FAQPage",
      mainEntity: [
        {
          "@type": "Question",
          name: "What is Phantom Blade Zero?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Phantom Blade Zero is a martial arts action RPG developed by S-Game. It combines fast-paced combat with a dark fantasy world inspired by Chinese wuxia culture.",
          },
        },
        {
          "@type": "Question",
          name: "What are the best weapons in Phantom Blade Zero?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "The Sha-chi system allows you to equip multiple weapons. Best picks depend on your playstyle - check our Weapons Guide for detailed rankings and upgrade paths.",
          },
        },
        {
          "@type": "Question",
          name: "How many endings does Phantom Blade Zero have?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Phantom Blade Zero has multiple endings based on your choices throughout the story. Our Endings page explains how to reach each one.",
          },
        },
      ],
    },
  ],
};

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
