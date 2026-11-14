# pipeline

Data pipeline (and, from Faz 2, the Elo engine) for turkish-leagues-elo.

```bash
uv sync                       # install dependencies (Python 3.13)
uv run tlelo --help
uv run pytest                 # tests
uv run ruff check . && uv run ruff format --check .
```

## Layout

| Module | Role |
|---|---|
| `tlelo/http.py` | Polite caching client: one request every 2 s, gzip page cache in `data/raw/tff/`, retries with backoff |
| `tlelo/tff/parse.py` | Pure parsers for tff.org pages (fixture list, week views, cup rounds, standings, match detail) |
| `tlelo/tff/crawl.py` | Which pages to download for a competition-season |
| `tlelo/tff/collect.py` | Cached pages → `Match` records; forfeit detection; detail-page pass |
| `tlelo/tff/supercup.py` | Süper Kupa (history table + hand-entered extras) |
| `tlelo/build.py` | Writes `data/matches/*.csv` and the team tables |
| `tlelo/validate.py` | Recomputes league tables and compares them with TFF's standings |

Column definitions and data sources: [`../data/README.md`](../data/README.md).

Set `TLELO_USER_AGENT` to change the HTTP User-Agent (default is a generic, non-identifying name).
