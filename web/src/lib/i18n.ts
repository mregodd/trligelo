// Two languages: Turkish at the site root, English under /en/ with the same paths after it
// (/takim/galatasaray/ and /en/takim/galatasaray/), so switching is a prefix change.

export type Lang = "tr" | "en";

/** A site path in the given language. */
export const href = (lang: Lang, path: string) => (lang === "en" ? `/en${path}` : path);

export const langOf = (pathname: string): Lang =>
  pathname === "/en" || pathname.startsWith("/en/") ? "en" : "tr";

/** The same page in the other language. */
export const otherLangPath = (pathname: string) =>
  langOf(pathname) === "en" ? pathname.slice(3) || "/" : `/en${pathname}`;
