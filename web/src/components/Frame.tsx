import { getMeta } from "@/lib/data";
import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { REPO, SITE } from "@/lib/site";
import { msg } from "@/messages";

import styles from "./Frame.module.css";
import { LangSwitch, Nav } from "./Nav";
import { ThemeToggle } from "./ThemeToggle";

/** Header, menu and footer around a page, in one language (lang set on the whole frame). */
export function Frame({ lang, children }: { lang: Lang; children: React.ReactNode }) {
  const meta = getMeta();
  const t = msg(lang).frame;
  return (
    <div lang={lang} className={styles.frame}>
      <a href="#icerik" className={styles.skip}>
        {t.skip}
      </a>
      <header className={styles.header}>
        <div className={`wrap ${styles.bar}`}>
          <a href={href(lang, "/")} className={styles.wordmark}>
            {/* The favicon (app/icon.svg) without its tile: the band is the tile here. */}
            <svg className={styles.mark} viewBox="2 3 12 10" aria-hidden="true">
              <path
                d="M2 12h12v1H2zM2 9h1v3H2zM4 10h1v2H4zM6 9h1v3H6zM8 10h1v2H8zM12 10h1v2h-1z"
                fill="var(--band-ink)"
              />
              <path d="M10 3h1v9h-1zM11 3h3l-1 2 1 2h-3z" fill="var(--flare)" />
            </svg>
            {SITE}
          </a>
          <div className={styles.tools}>
            <LangSwitch />
            <ThemeToggle lang={lang} />
          </div>
          <Nav lang={lang} />
        </div>
      </header>
      <main id="icerik" className={styles.main}>
        {children}
      </main>
      <footer className={styles.footer}>
        <div className={`wrap ${styles.footerGrid}`}>
          <p>{t.updated(fmt(lang).dateLong(meta.lastMatch), meta.model)}</p>
          <nav aria-label={t.footerNav}>
            <ul className={styles.footerLinks}>
              <li>
                <a href={href(lang, "/metodoloji/")}>{t.how}</a>
              </li>
              <li>
                <a href={href(lang, "/hakkinda/")}>{t.about}</a>
              </li>
              <li>
                <a href={href(lang, "/kaynaklar/")}>{t.sources}</a>
              </li>
              <li>
                <a href={href(lang, "/gizlilik/")}>{t.privacy}</a>
              </li>
              <li>
                <a href={REPO}>GitHub</a>
              </li>
            </ul>
          </nav>
        </div>
      </footer>
    </div>
  );
}
