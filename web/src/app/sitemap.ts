import type { MetadataRoute } from "next";

import { getTeams } from "@/lib/data";
import { href } from "@/lib/i18n";
import { LEAGUES } from "@/lib/labels";
import { SITE_URL } from "@/lib/site";

export const dynamic = "force-static";

const PAGES = ["/", "/fixtures/", "/methodology/", "/about/", "/sources/", "/privacy/"];

/** Every page in both languages, each listing its other-language twin. */
export default function sitemap(): MetadataRoute.Sitemap {
  const paths = [
    ...PAGES,
    ...LEAGUES.map((l) => `/league/${l.slug}/`),
    ...getTeams().map((c) => `/club/${c.slug}/`),
  ];
  const languages = (path: string) => ({ tr: SITE_URL + path, en: SITE_URL + href("en", path) });
  return paths.flatMap((path) =>
    (["tr", "en"] as const).map((lang) => ({
      url: SITE_URL + href(lang, path),
      alternates: { languages: languages(path) },
    })),
  );
}
