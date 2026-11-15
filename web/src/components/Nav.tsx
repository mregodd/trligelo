"use client";

import { usePathname } from "next/navigation";

import { href, type Lang, langOf, otherLangPath } from "@/lib/i18n";
import { type Messages, msg } from "@/messages";

import styles from "./Nav.module.css";

// Link texts are in messages/ (nav); league names are the same in every language.
const LINKS: { href: string; label: (m: Messages) => string }[] = [
  { href: "/", label: (m) => m.nav.rankings },
  { href: "/maclar/", label: (m) => m.nav.fixtures },
  { href: "/lig/super-lig/", label: () => "Süper Lig" },
  { href: "/lig/1-lig/", label: () => "1. Lig" },
  { href: "/lig/2-lig/", label: () => "2. Lig" },
  { href: "/lig/3-lig/", label: () => "3. Lig" },
  { href: "/metodoloji/", label: (m) => m.nav.methodology },
];

export function Nav({ lang }: { lang: Lang }) {
  const path = usePathname() ?? "/";
  const here = lang === "en" ? path.slice(3) || "/" : path; // the path after /en
  const norm = here.endsWith("/") ? here : `${here}/`;
  return (
    <nav aria-label={msg(lang).nav.label} className={styles.nav}>
      <ul>
        {LINKS.map((l) => {
          const current = l.href === "/" ? norm === "/" : norm.startsWith(l.href);
          return (
            <li key={l.href}>
              <a href={href(lang, l.href)} aria-current={current ? "page" : undefined}>
                {l.label(msg(lang))}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

/** The same page in the other language, named in that language. */
export function LangSwitch() {
  const path = usePathname() ?? "/";
  const here = langOf(path);
  const target = here === "en" ? "tr" : "en";
  return (
    <a href={otherLangPath(path.endsWith("/") ? path : `${path}/`)} lang={target} hrefLang={target}>
      {msg(here).nav.switchTo}
    </a>
  );
}
