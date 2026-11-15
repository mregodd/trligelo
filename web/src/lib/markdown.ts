// Markdown written by the project (docs/ and content/), rendered at build time. It is trusted:
// the HTML goes into the page as it is.
import { Marked, type Tokens } from "marked";

import { msg } from "@/messages";

import type { Lang } from "./i18n";
import { REPO } from "./site";

type Parser = { parser: { parseInline: (t: Tokens.Generic[]) => string } };

/** GitHub-style heading id, so links like #10-kendin-hesapla keep working. */
function slug(text: string, lang: Lang) {
  return text
    .toLocaleLowerCase(msg(lang).locale)
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim()
    .replace(/\s+/g, "-");
}

/**
 * Markdown to HTML: headings get ids; links to site pages ("/...") and full URLs stay, other
 * relative links point into the repository on GitHub (a file in docs/ by default).
 */
export function renderMarkdown(markdown: string, lang: Lang): string {
  const md = new Marked({ gfm: true });
  md.use({
    renderer: {
      heading(this: Parser, token: Tokens.Heading) {
        const html = this.parser.parseInline(token.tokens);
        return `<h${token.depth} id="${slug(token.text, lang)}">${html}</h${token.depth}>\n`;
      },
      link(this: Parser, token: Tokens.Link) {
        let href = token.href;
        if (!/^(https?:|#|mailto:|\/)/.test(href)) {
          href = `${REPO}/blob/main/${href.startsWith("../") ? href.slice(3) : `docs/${href}`}`;
        }
        const rel = /^https?:/.test(href) ? ' rel="noopener"' : "";
        return `<a href="${href}"${rel}>${this.parser.parseInline(token.tokens)}</a>`;
      },
    },
  });
  return md.parse(markdown) as string;
}

/** Fill {name} placeholders (site name, dates, addresses) before rendering. */
export const fill = (markdown: string, values: Record<string, string>) =>
  markdown.replace(/\{(\w+)\}/g, (all, key: string) => values[key] ?? all);
