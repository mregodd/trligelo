# pipeline

Data pipeline and Elo engine for turkish-leagues-elo. How the ratings work: [`../docs/METODOLOJI.md`](../docs/METODOLOJI.md).

```bash
uv sync                       # install dependencies (Python 3.13)
uv run tlelo --help
uv run pytest                 # tests
uv run ruff check . && uv run ruff format --check .
```

## Layout

| Module | Role |
|---|---|
| `tlelo/http.py` | Polite caching client: one request every 2 s, gzip page cache under `data/raw/`, retries with backoff |
| `tlelo/tff/parse.py` | Pure parsers for tff.org pages (fixture list, week views, cup rounds, standings, match detail) |
| `tlelo/tff/crawl.py` | Which pages to download for a competition-season |
| `tlelo/tff/collect.py` | Cached pages → `Match` records; forfeit detection; detail-page pass |
| `tlelo/tff/supercup.py` | Süper Kupa (history table + hand-entered extras) |
| `tlelo/europe/wiki.py` | Finds a UEFA competition-season's Wikipedia articles (article pages only, as robots.txt allows) |
| `tlelo/europe/parse.py` | Pure parsers for Wikipedia's Parsoid HTML: match boxes, coefficient tables |
| `tlelo/europe/collect.py` | Turkish clubs' matches, name resolution, opponents' coefficients, legs |
| `tlelo/europe/validate.py` | Group / league phase sizes, two-legged ties, missing results |
| `tlelo/elo/data.py` | Match CSVs → one chronological game list (pro / amateur / foreign sides, neutral ground, closed doors) |
| `tlelo/elo/engine.py` | The Elo engine: season transitions, match updates, cup bonuses |
| `tlelo/elo/fit.py` | Europe opponent model (fitted with the run's own ratings) and the ordered-logit win/draw/loss model |
| `tlelo/elo/params.py` | `Params` (plan starting values) and `V1` (model v1.0) |
| `tlelo/elo/backtest.py`, `report.py` | Scoring, baselines, parameter search, `docs/backtest.md` |
| `tlelo/elo/output.py` | `data/ratings/current.csv` and `history.csv` |
| `tlelo/site/names.py` | Readable club names (legal form dropped, Turkish title case, hand-kept overrides) and URL slugs |
| `tlelo/site/export.py` | The website's JSON (`web/src/data/`): summaries, leagues, every club's events in the display window; withdrawals; logo copies |
| `tlelo/site/logos.py` | Club logos from the clubs' TFF pages, cached in `data/raw/tff/` |
| `tlelo/build.py` | Writes `data/matches/*.csv`, the team tables and `data/europe/*.csv` |
| `tlelo/validate.py` | Recomputes league tables and compares them with TFF's standings |

Column definitions and data sources: [`../data/README.md`](../data/README.md).

Set `TLELO_USER_AGENT` to change the HTTP User-Agent (default is a generic, non-identifying name).
