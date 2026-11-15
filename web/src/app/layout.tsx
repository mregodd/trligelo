import type { Metadata, Viewport } from "next";
import { Barlow, Barlow_Semi_Condensed } from "next/font/google";

import { Nav } from "@/components/Nav";
import { getMeta } from "@/lib/data";
import { dateLong } from "@/lib/format";
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
  themeColor: "#0d3a40",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const meta = getMeta();
  return (
    <html lang="tr" className={`${text.variable} ${display.variable}`}>
      <body>
        <a href="#icerik" className={styles.skip}>
          İçeriğe geç
        </a>
        <header className={styles.header}>
          <div className={`wrap ${styles.bar}`}>
            <a href="/" className={styles.wordmark}>
              {SITE}
            </a>
            <Nav />
          </div>
        </header>
        <main id="icerik" className={styles.main}>{children}</main>
        <footer className={styles.footer}>
          <div className={`wrap ${styles.footerGrid}`}>
            <p>
              Puanlar son olarak {dateLong(meta.lastMatch)} tarihli maçlara göre hesaplandı. Model{" "}
              {meta.model}. <a href="/metodoloji/">Puanlar nasıl hesaplanıyor?</a>
            </p>
            <p>
              Yurt içi maç sonuçları{" "}
              <a href="https://www.tff.org" rel="noopener">
                Türkiye Futbol Federasyonu
              </a>
              , Avrupa maçları ve UEFA katsayıları{" "}
              <a href="https://en.wikipedia.org" rel="noopener">
                Wikipedia
              </a>{" "}
              (CC BY-SA 4.0) kaynaklıdır. Ticari olmayan bir projedir: reklam ve üyelik yok.
            </p>
            <p>
              Kod ve veri açık: <a href={REPO}>GitHub</a>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
