// Shapes of the JSON written by `uv run tlelo site` (pipeline/src/tlelo/site/export.py).

export type LeagueCode = "SL" | "1L" | "2L" | "3L";

export interface Meta {
  model: string;
  generatedAt: string;
  lastMatch: string;
  weekFrom: string;
  season: string;
  displayFrom: string;
  activeTeams: number;
  teams: number;
  europe: { a: number; b: number; home: number };
}

export interface FormEntry {
  s: number; // 1 win, 0.5 draw, 0 loss
  d: number; // rating change
}

export interface TeamSummary {
  id: number;
  slug: string;
  name: string;
  official: string; // "" when the club is shown by its display name only
  active: boolean;
  withdrawn: string | null; // date it left the league this season (forfeits from then on)
  league: LeagueCode;
  group: string | null;
  lastSeason: string;
  rating: number;
  rank: number | null;
  leagueRank: number | null;
  week: number;
  games: number;
  peak: { r: number; date: string } | null;
  low: { r: number; date: string } | null;
  form: FormEntry[];
}

export interface Opponent {
  kind: "pro" | "amateur" | "foreign";
  name: string;
  slug?: string | null;
  coef?: number | null;
}

export interface MatchEvent {
  t: "match";
  seq: number;
  date: string;
  season: string;
  comp: string;
  round: string | null;
  venue: "h" | "a" | "n";
  opp: Opponent;
  gf: number;
  ga: number;
  g90: [number, number] | null;
  pens: [number, number] | null;
  r: number;
  ro: number;
  h: number;
  e: number;
  s: number;
  k: number;
  w: number;
  g: number;
  d: number;
  ra: number;
}

export type AdjustmentKind =
  | "promotion"
  | "relegation"
  | "regression"
  | "anchor"
  | "cup"
  | "supercup"
  | "champion"
  | "newcomer"
  | "return";

export interface AdjustmentEvent {
  t: AdjustmentKind;
  seq: number;
  date: string | null;
  season: string;
  d: number;
  ra: number;
}

export type TeamEvent = MatchEvent | AdjustmentEvent;

export interface TeamSeason {
  season: string;
  league: LeagueCode;
  group: string | null;
}

export interface TeamDetail extends TeamSummary {
  seasons: TeamSeason[];
  events: TeamEvent[];
}

export interface LeagueGroup {
  name: string | null;
  teams: string[]; // slugs, best first
}

export interface League {
  code: LeagueCode;
  groups: LeagueGroup[];
}
