"use client";

import { usePathname } from "next/navigation";

import styles from "./Nav.module.css";

const LINKS = [
  { href: "/", label: "Sıralama" },
  { href: "/maclar/", label: "Maçlar" },
  { href: "/lig/super-lig/", label: "Süper Lig" },
  { href: "/lig/1-lig/", label: "1. Lig" },
  { href: "/lig/2-lig/", label: "2. Lig" },
  { href: "/lig/3-lig/", label: "3. Lig" },
  { href: "/metodoloji/", label: "Metodoloji" },
];

export function Nav() {
  const path = usePathname() ?? "/";
  const norm = path.endsWith("/") ? path : `${path}/`;
  return (
    <nav aria-label="Ana menü" className={styles.nav}>
      <ul>
        {LINKS.map((l) => {
          const current = l.href === "/" ? norm === "/" : norm.startsWith(l.href);
          return (
            <li key={l.href}>
              <a href={l.href} aria-current={current ? "page" : undefined}>
                {l.label}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
