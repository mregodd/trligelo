// Build-time data access: server components only (it reads files during `next build`).
import { readFileSync } from "node:fs";
import path from "node:path";

import type { Lang } from "./i18n";
import type { Fixtures, League, Meta, TeamDetail, TeamSummary } from "./types";

const DATA = path.join(process.cwd(), "src", "data");

function read<T>(file: string): T {
  try {
    return JSON.parse(readFileSync(path.join(DATA, file), "utf-8")) as T;
  } catch (err) {
    throw new Error(
      `Site data missing (${file}). Generate it first: cd pipeline && uv run tlelo site`,
      { cause: err },
    );
  }
}

let cache: { meta: Meta; teams: TeamSummary[]; leagues: League[] } | null = null;

function load() {
  cache ??= {
    meta: read<Meta>("meta.json"),
    teams: read<TeamSummary[]>("teams.json"),
    leagues: read<League[]>("leagues.json"),
  };
  return cache;
}

export const getMeta = () => load().meta;
export const getTeams = () => load().teams;
export const getLeagues = () => load().leagues;
export const getFixtures = () => read<Fixtures>("fixtures.json");

export function getTeamMap(): Map<string, TeamSummary> {
  return new Map(getTeams().map((t) => [t.slug, t]));
}

export function getTeam(slug: string): TeamDetail {
  return read<TeamDetail>(path.join("teams", `${slug}.json`));
}

/** The methodology page's single source: docs/METODOLOJI.md, or its translation METHODOLOGY.md. */
export const methodologyFile = (lang: Lang) => (lang === "en" ? "METHODOLOGY.md" : "METODOLOJI.md");

export function readMethodology(lang: Lang): string {
  return readFileSync(path.join(process.cwd(), "..", "docs", methodologyFile(lang)), "utf-8");
}

/** A long page of the site in one language: web/content/<lang>/<name>.md. */
export function readContent(lang: Lang, name: string): string {
  return readFileSync(path.join(process.cwd(), "content", lang, `${name}.md`), "utf-8");
}
