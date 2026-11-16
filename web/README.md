# web

The website: a static Next.js export (`out/`), deployed to Cloudflare Pages.

```bash
cd ../pipeline && uv run tlelo site   # write the site's data to src/data/ and the logos to public/logos/ (generated, not committed)
cd ../web
npm install
npm run dev                          # http://localhost:3000
npm run build                        # static site in out/
```

Pages, in Turkish at the root and in English under `/en/` with the same paths: overall ranking (`/`), upcoming matches (`/maclar/`), league tables (`/lig/<lig>/`), club pages (`/takim/<kulüp>/`), methodology (`/metodoloji/`, rendered from `../docs/METODOLOJI.md` or `../docs/METHODOLOGY.md`), about, sources and privacy (`/hakkinda/`, `/kaynaklar/`, `/gizlilik/`, from `content/<lang>/*.md`).

| Path | Role |
|---|---|
| `src/app/(tr)/`, `src/app/en/` | The routes of each language: thin files that render a view with `lang` |
| `src/views/` | One view per page, shared by both languages |
| `src/messages/tr.ts`, `en.ts` | Every short text of the site, one file per language |
| `content/tr/`, `content/en/` | The long pages (about, sources, privacy) as Markdown |
| `src/components/Frame.tsx` | Header, menu, language link and footer around every page |
| `src/lib/i18n.ts` | The two languages and their paths (`href`, the other language's path) |
| `src/lib/data.ts` | Reads the generated JSON at build time (server components only) |
| `src/lib/format.ts`, `labels.ts`, `calc.ts` | Number and date formatting, names of competitions and rounds, the plain-language account of a match (both languages) |
| `src/components/Ruler.tsx` | The rating ruler: every club on one scale, one lane per league |
| `src/components/Standings.tsx` | Ranking table with league filter and search, linked to the ruler |
| `src/components/TeamTimeline.tsx` | A club's rating chart and match list from one copy of its events |
| `src/app/globals.css` | Colour, type and spacing tokens (light and dark) |
| `src/app/icon.svg` | The site's mark (a ruler with a corner flag) on a 16-unit grid. `favicon.ico` (16, 32, 48 px) and `apple-icon.png` (180 px) beside it are rendered from it; the header in `Frame.tsx` repeats it without the tile, so change both together |

Translating: short texts are in `src/messages/`. `en.ts` must have exactly the shape of `tr.ts`, so a missing or extra key fails the build; sentences that take numbers or names are functions there. To add a language, copy `en.ts`, translate it, register it in `src/messages/index.ts` and add its routes like `src/app/en/`. Long pages are Markdown in `content/<lang>/` (placeholders such as `{date}` are filled at build time); the methodology is `../docs/METODOLOJI.md` and its translations. Club and league names are the same in every language. Club names come from TFF without the legal form; sponsored names use the common name from `../data/sources/team_display_names.csv`.
