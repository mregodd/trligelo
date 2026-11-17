// Two languages: Turkish at the site root, English under /en/ with the same paths after it
// (/club/galatasaray/ and /en/club/galatasaray/), so switching is a prefix change.

export type Lang = "tr" | "en";

/** A site path in the given language. */
export const href = (lang: Lang, path: string) => (lang === "en" ? `/en${path}` : path);

export const langOf = (pathname: string): Lang =>
  pathname === "/en" || pathname.startsWith("/en/") ? "en" : "tr";

/** The same page in the other language. */
export const otherLangPath = (pathname: string) =>
  langOf(pathname) === "en" ? pathname.slice(3) || "/" : `/en${pathname}`;

/** Canonical and hreflang links of a page, from its Turkish path ("/club/galatasaray/"). */
export const alternates = (lang: Lang, path: string) => ({
  canonical: href(lang, path),
  languages: { tr: path, en: href("en", path), "x-default": path },
});
