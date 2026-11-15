import type { Metadata } from "next";
import { Marked, type Tokens } from "marked";

import { TextPage } from "@/components/TextPage";
import { readMethodology } from "@/lib/data";
import { REPO } from "@/lib/site";

export const metadata: Metadata = {
  title: "Puanlar nasıl hesaplanıyor?",
  description: "Türk Ligleri Elo'nun yöntemi: formül, parametreler, test sonuçları ve sınırlamalar.",
};

/** GitHub-style heading id, so links like #10-kendin-hesapla keep working. */
function slug(text: string) {
  return text
    .toLocaleLowerCase("tr-TR")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim()
    .replace(/\s+/g, "-");
}

function render(markdown: string): string {
  const md = new Marked({ gfm: true });
  md.use({
    renderer: {
      heading(this: { parser: { parseInline: (t: Tokens.Generic[]) => string } }, token: Tokens.Heading) {
        const html = this.parser.parseInline(token.tokens);
        return `<h${token.depth} id="${slug(token.text)}">${html}</h${token.depth}>\n`;
      },
      link(this: { parser: { parseInline: (t: Tokens.Generic[]) => string } }, token: Tokens.Link) {
        let href = token.href;
        // Relative links point into the repository on GitHub.
        if (!/^(https?:|#|mailto:)/.test(href)) {
          href = `${REPO}/blob/main/${href.startsWith("../") ? href.slice(3) : `docs/${href}`}`;
        }
        const text = this.parser.parseInline(token.tokens);
        return `<a href="${href}">${text}</a>`;
      },
    },
  });
  // The document's first heading and model line are replaced by the page's own header.
  const body = markdown.replace(/^# .*\n+(> .*\n+)?/, "");
  return md.parse(body) as string;
}

export default function MethodologyPage() {
  const html = render(readMethodology());
  return (
    <TextPage
      title="Puanlar nasıl hesaplanıyor?"
      lead={
        <>
          Formül, parametreler ve bunların nasıl seçildiği. Bu sayfa repodaki{" "}
          <a href={`${REPO}/blob/main/docs/METODOLOJI.md`}>METODOLOJI.md</a> dosyasından üretilir.
        </>
      }
    >
      {/* Repository content, written by the project: rendered as trusted HTML. */}
      <article dangerouslySetInnerHTML={{ __html: html }} />
    </TextPage>
  );
}
