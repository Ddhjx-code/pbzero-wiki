import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import "./globals.css";

const GA_MEASUREMENT_ID = "G-MZ867GJT24";

export const metadata: Metadata = {
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
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
