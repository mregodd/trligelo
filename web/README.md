# web

The website: a static Next.js export (`out/`), deployed to Cloudflare Pages.

```bash
cd ../pipeline && uv run tlelo site   # write the site's data to src/data/ (generated, not committed)
cd ../web
npm install
npm run dev                          # http://localhost:3000
npm run build                        # static site in out/
```

Pages: overall ranking (`/`), league tables (`/lig/<lig>/`), club pages (`/takim/<kulüp>/`), methodology (`/metodoloji/`, rendered from `../docs/METODOLOJI.md`).

| Path | Role |
|---|---|
| `src/lib/data.ts` | Reads the generated JSON at build time (server components only) |
| `src/lib/format.ts`, `labels.ts`, `calc.ts` | Turkish number/date formatting, names of leagues and rounds, the text of a match's calculation |
| `src/components/Ruler.tsx` | The rating ruler: every club on one scale, one lane per league |
| `src/components/Standings.tsx` | Ranking table with league filter and search, linked to the ruler |
| `src/components/TeamTimeline.tsx` | A club's rating chart and match list from one copy of its events |
| `src/app/globals.css` | Colour, type and spacing tokens (light and dark) |

Club names come from TFF without the legal form; sponsored names use the common name from `../data/sources/team_display_names.csv`.
