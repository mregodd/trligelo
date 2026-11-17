export const SITE = "trligelo";
export const SITE_URL = "https://trligelo.com";
export const REPO = "https://github.com/mregodd/trligelo";
export const CONTACT = "derbedekegemen@gmail.com";

/** The link-preview card of every page in a language; the images come from notes/og/build.mjs. */
export const openGraph = (lang: "tr" | "en") => ({
  siteName: SITE,
  type: "website" as const,
  locale: lang === "tr" ? "tr_TR" : "en_US",
  images: [{ url: lang === "tr" ? "/og.png" : "/en/og.png", width: 1200, height: 630 }],
});
