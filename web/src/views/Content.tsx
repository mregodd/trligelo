import type { Metadata } from "next";

import { TextPage } from "@/components/TextPage";
import { getMeta, readContent } from "@/lib/data";
import { fmt } from "@/lib/format";
import type { Lang } from "@/lib/i18n";
import { fill, renderMarkdown } from "@/lib/markdown";
import { CONTACT, REPO, SITE } from "@/lib/site";
import { msg } from "@/messages";

/** The long pages: title and lead in messages/, the body in content/<lang>/<file>.md. */
const PAGES = { about: "hakkinda", sources: "kaynaklar", privacy: "gizlilik" } as const;
export type ContentPage = keyof typeof PAGES;

export function contentMetadata(lang: Lang, page: ContentPage): Metadata {
  const t = msg(lang).pages[page];
  return { title: t.title, description: t.description(SITE) };
}

// shortcut: the privacy page describes the launch setup (Cloudflare Pages + Cloudflare Web
// Analytics, decided for Faz 4); update content/*/gizlilik.md if hosting or statistics change.
export function ContentView({ lang, page }: { lang: Lang; page: ContentPage }) {
  const t = msg(lang).pages[page];
  const meta = getMeta();
  const markdown = fill(readContent(lang, PAGES[page]), {
    site: SITE,
    date: fmt(lang).dateLong(meta.lastMatch),
    model: meta.model,
    contact: CONTACT,
    repo: REPO,
  });
  return (
    <TextPage title={t.title} lead={t.lead(SITE)}>
      {/* Project content: rendered as trusted HTML. */}
      <article dangerouslySetInnerHTML={{ __html: renderMarkdown(markdown, lang) }} />
    </TextPage>
  );
}
