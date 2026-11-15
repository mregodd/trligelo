import type { Metadata } from "next";

import { TextPage } from "@/components/TextPage";
import { methodologyFile, readMethodology } from "@/lib/data";
import type { Lang } from "@/lib/i18n";
import { renderMarkdown } from "@/lib/markdown";
import { REPO } from "@/lib/site";
import { msg } from "@/messages";

export function methodologyMetadata(lang: Lang): Metadata {
  return { title: msg(lang).methodology.title, description: msg(lang).methodology.description };
}

export function MethodologyView({ lang }: { lang: Lang }) {
  const t = msg(lang).methodology;
  const file = methodologyFile(lang);
  // The document's first heading and version line are replaced by the page's own header.
  const html = renderMarkdown(readMethodology(lang).replace(/^# .*\n+(> .*\n+)?/, ""), lang);
  return (
    <TextPage
      title={t.title}
      lead={
        <>
          {t.lead} <a href={`${REPO}/blob/main/docs/${file}`}>{file}</a> {t.leadEnd}
        </>
      }
    >
      {/* Repository content, written by the project: rendered as trusted HTML. */}
      <article dangerouslySetInnerHTML={{ __html: html }} />
    </TextPage>
  );
}
