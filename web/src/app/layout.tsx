import type { Metadata, Viewport } from "next";
import { Barlow, Barlow_Semi_Condensed } from "next/font/google";

import { Nav } from "@/components/Nav";
import { ThemeToggle } from "@/components/ThemeToggle";
import { getMeta } from "@/lib/data";
import { dateLong } from "@/lib/format";
import { THEME_SCRIPT } from "@/lib/theme";
import { REPO, SITE } from "@/lib/site";

import styles from "./layout.module.css";
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
  title: { default: SITE, template: `%s | ${SITE}` },
  description:
    "Süper Lig, 1. Lig, 2. Lig ve 3. Lig'deki bütün profesyonel kulüpler tek bir Elo cetvelinde. Her maçın puan hesabı açık.",
};

export const viewport: Viewport = {
  themeColor: "#13235e", // the night band
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const meta = getMeta();
  return (
    // data-theme is set by THEME_SCRIPT before React hydrates, hence the warning suppression.
    <html lang="tr" className={`${text.variable} ${display.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body>
        <a href="#icerik" className={styles.skip}>
          İçeriğe geç
        </a>
        <header className={styles.header}>
          <div className={`wrap ${styles.bar}`}>
            <a href="/" className={styles.wordmark}>
              {SITE}
            </a>
            <ThemeToggle />
            <Nav />
          </div>
        </header>
        <main id="icerik" className={styles.main}>{children}</main>
        <footer className={styles.footer}>
          <div className={`wrap ${styles.footerGrid}`}>
            <p>
              Puanlar son olarak {dateLong(meta.lastMatch)} tarihli maçlara göre hesaplandı. Model{" "}
              {meta.model}.
            </p>
            <nav aria-label="Site bilgileri">
              <ul className={styles.footerLinks}>
                <li>
                  <a href="/metodoloji/">Puanlar nasıl hesaplanıyor?</a>
                </li>
                <li>
                  <a href="/hakkinda/">Hakkında</a>
                </li>
                <li>
                  <a href="/kaynaklar/">Kaynaklar</a>
                </li>
                <li>
                  <a href="/gizlilik/">Gizlilik</a>
                </li>
                <li>
                  <a href={REPO}>GitHub</a>
                </li>
              </ul>
            </nav>
          </div>
        </footer>
      </body>
    </html>
  );
}
