// A match's numbers in plain terms: the chances before it and what each result was worth.
// The sentences are in messages/ and are put together in components/History.tsx; the
// formula itself is on the methodology page (docs/METODOLOJI.md §2).
import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site
import { msg } from "@/messages";

import { fmt } from "./format";
import type { Lang } from "./i18n";
import type { MatchEvent } from "./types";

const { params: P, outcome } = meta;

const expit = (x: number) => 1 / (1 + Math.exp(-x));

/** Home win, draw, away win from the home side's lead (home advantage included). */
function homeChances(lead: number): number[] {
  const z = (outcome.beta * lead) / 100;
  const away = expit(outcome.c1 - z);
  const home = 1 - expit(outcome.c2 - z);
  return [home, 1 - home - away, away];
}

/** A club's win, draw and loss chances in whole percent adding up to 100. */
function percent(lead: number, venue: MatchEvent["venue"]) {
  const asHome = homeChances(lead);
  const asAway = homeChances(-lead).reverse();
  const [w, , l] =
    venue === "h" ? asHome : venue === "a" ? asAway : asHome.map((p, i) => (p + asAway[i]) / 2);
  const win = Math.round(w * 100);
  const loss = Math.round(l * 100);
  return { win, draw: 100 - win - loss, loss };
}

/** The club's chances before the match, and its chance of winning on neutral ground. */
export function chances(m: MatchEvent) {
  const lead = m.r + m.h - m.ro; // the club's lead, its side of the home advantage included
  return { ...percent(lead, m.venue), neutralWin: percent(m.r - m.ro, "n").win };
}

/** What a win, a draw and a defeat by one goal were worth to the club, as on the fixtures. */
export function stakes(m: MatchEvent): number[] {
  return [1, 0.5, 0].map((s) => Math.round(m.k * m.w * (s - m.e) * 10) / 10 + 0); // + 0: no -0
}

/** Played behind closed doors (a smaller home advantage). */
export function closedDoors(m: MatchEvent): boolean {
  return m.venue !== "n" && Math.round(Math.abs(m.h)) === Math.round(P.homeClosed);
}

/** The model numbers the match box needs: K and the provisional rule. */
export const model = { k: P.k, provisionalGames: P.provisionalGames, provisionalFactor: P.provisionalFactor };

/** A summer regression with its numbers: how far from the league mean, how much was closed. */
export function regressionText(d: number, lang: Lang): string {
  const f = fmt(lang);
  return msg(lang).explain.regression(
    f.num(Math.abs(d) / P.regression),
    d < 0,
    f.num(P.regression * 100),
    f.delta(d),
  );
}
