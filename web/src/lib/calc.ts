// A match's rating change told in plain words (the sentences are in messages/). The formula
// itself is on the methodology page (docs/METODOLOJI.md §2).
import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site
import { msg } from "@/messages";

import { fmt, result } from "./format";
import type { Lang } from "./i18n";
import { competitionName } from "./labels";
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

/** The club's chances before the match, in whole percent adding up to 100. */
export function chances(m: MatchEvent): { win: number; draw: number; loss: number } {
  const lead = m.r + m.h - m.ro; // the club's lead, its side of the home advantage included
  const asHome = homeChances(lead);
  const asAway = homeChances(-lead).reverse();
  const [w, , l] =
    m.venue === "h" ? asHome : m.venue === "a" ? asAway : asHome.map((p, i) => (p + asAway[i]) / 2);
  const win = Math.round(w * 100);
  const loss = Math.round(l * 100);
  return { win, draw: 100 - win - loss, loss };
}

export function explain(team: string, m: MatchEvent, lang: Lang): string[] {
  const t = msg(lang).explain;
  const f = fmt(lang);
  const opp = m.opp.name;
  const out: string[] = [];

  let before = t.before(team, f.num(m.r, 0), opp, f.num(m.ro, 0));
  if (m.opp.kind === "foreign") before += t.foreign;
  if (m.opp.kind === "amateur") before += t.amateur;
  const h = Math.round(Math.abs(m.h));
  if (m.venue === "n") {
    before += t.neutral;
  } else {
    const host = m.venue === "h" ? team : opp;
    before += h === Math.round(P.homeClosed) ? t.closed(host, h) : t.home(host, h);
  }
  out.push(before);

  const c = chances(m);
  out.push(t.chances(team, c.win, c.draw, c.loss));

  const r = result(m.s);
  const fav = m.e >= 0.55 ? 1 : m.e <= 0.45 ? -1 : 0; // favourite, underdog, or even
  let score = `${m.gf}-${m.ga}`;
  if (m.g90) score += t.extraTime(m.g90[0], m.g90[1]);
  if (m.pens) score += t.shootout(m.pens[0], m.pens[1]);
  let res = t.result(score, msg(lang).result.word[r], t.why[r][fav + 1], f.delta(m.d));
  if (m.pens) res += t.pens;
  out.push(res);

  if (m.g > 1) out.push(t.margin(Math.abs(m.gf - m.ga), f.factor(m.g)));
  if (m.w !== 1) {
    out.push(
      m.opp.kind === "amateur"
        ? t.amateurWeight(f.factor(m.w))
        : t.weight(competitionName(m.comp, lang), f.factor(m.w)),
    );
  }
  if (m.k !== P.k) out.push(t.provisional(P.provisionalGames, f.factor(P.provisionalFactor)));
  return out;
}

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
