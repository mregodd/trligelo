import type { Metadata, Viewport } from "next";
import { Barlow, Barlow_Semi_Condensed } from "next/font/google";

import { SITE, SITE_URL } from "@/lib/site";
import { THEME_SCRIPT } from "@/lib/theme";
import { msg } from "@/messages";

import "./globals.css";

const text = Barlow({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--font-text",
  display: "swap",
});
const display = Barlow_Semi_Condensed({
  subsets: ["latin", "latin-ext"],
  weight: ["500", "600"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  twitter: { card: "summary_large_image" },
  title: { default: SITE, template: `%s | ${SITE}` },
  description: msg("tr").home.description,
};

export const viewport: Viewport = {
  themeColor: "#13235e", // the night band
};

/**
 * The document only: header, menu and footer come from each language's layout (Frame), so
 * Turkish pages (app/(tr)/) and English pages (app/en/) each get their own.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // data-theme and, under /en/, lang are set by THEME_SCRIPT before React hydrates.
    <html lang="tr" className={`${text.variable} ${display.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
