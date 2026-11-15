// A match's rating change told in plain words. The formula itself is on the methodology page
// (docs/METODOLOJI.md §2); these sentences say what moved the number and why.
import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site

import { delta, factor, num, RESULT_WORD, result } from "./format";
import { COMPETITIONS } from "./labels";
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

function scoreLine(m: MatchEvent): string {
  let s = `${m.gf}-${m.ga}`;
  if (m.g90) s += ` (uzatmalarda; 90 dakika ${m.g90[0]}-${m.g90[1]})`;
  if (m.pens) s += `, penaltılar ${m.pens[0]}-${m.pens[1]}`;
  return s;
}

// Names never take a suffix here (Turkish suffixes follow the word's sounds): sentences are
// built so the club names stand alone.
export function explain(team: string, m: MatchEvent): string[] {
  const opp = m.opp.name;
  const out: string[] = [];

  let before = `Maç öncesi ${team} ${num(m.r, 0)}, ${opp} ${num(m.ro, 0)} puandaydı.`;
  if (m.opp.kind === "foreign") before += " Yabancı rakibin puanı UEFA kulüp katsayısından hesaplanır.";
  if (m.opp.kind === "amateur") before += " Amatör rakiplerin puanı her maçta aynıdır.";
  const h = Math.round(Math.abs(m.h));
  if (m.venue === "n") {
    before += " Maç tarafsız sahada oynandı, ev avantajı yok.";
  } else {
    const host = m.venue === "h" ? team : opp;
    before +=
      h === Math.round(P.homeClosed)
        ? ` ${host} ev sahibiydi; maç seyircisiz oynandığı için ev avantajı ${h} puan sayıldı.`
        : ` ${host} ev sahibi olduğu için ${h} puanlık avantajla başladı.`;
  }
  out.push(before);

  const c = chances(m);
  out.push(
    `Bu puanlarla ${team} için şanslar: galibiyet %${c.win}, beraberlik %${c.draw}, yenilgi %${c.loss}.`,
  );

  const r = result(m.s);
  const fav = m.e >= 0.55 ? 1 : m.e <= 0.45 ? -1 : 0; // favourite, underdog, or even
  const why = {
    G: ["Sürpriz bir galibiyet olduğu için puanı çok artırdı", "Denk bir maçı kazandı",
        "Favori olduğu için galibiyet puanı az artırdı"],
    B: ["Zayıf görülen taraf olduğu için beraberlik puan kazandırdı",
        "Denk bir maçta beraberlik puanı pek değiştirmedi",
        "Favori olduğu için beraberlik puan kaybettirdi"],
    M: ["Beklenen bir yenilgi olduğu için puanı az düşürdü", "Denk bir maçı kaybetti",
        "Beklenmeyen bir yenilgi olduğu için puanı çok düşürdü"],
  }[r][fav + 1];
  let res = `Sonuç ${scoreLine(m)}, ${RESULT_WORD[r]}. ${why}: ${delta(m.d)}.`;
  if (m.pens) res += " Penaltı atışları Elo'da beraberlik sayılır.";
  out.push(res);

  const margin = Math.abs(m.gf - m.ga);
  if (m.g > 1) out.push(`Fark ${margin} gol olduğu için değişim ${factor(m.g)} katına çıktı.`);
  if (m.w !== 1) {
    const comp = COMPETITIONS[m.comp]?.name ?? m.comp;
    out.push(
      m.opp.kind === "amateur"
        ? `Amatör bir rakiple oynanan kupa maçı ${factor(m.w)} ağırlıkla sayılır.`
        : `${comp} maçları ${factor(m.w)} ağırlıkla sayılır.`,
    );
  }
  if (m.k !== P.k) {
    out.push(
      `Kulübün profesyonel liglerdeki ilk ${P.provisionalGames} maçından biri olduğu için ` +
        `değişim ${factor(P.provisionalFactor)} katına çıktı.`,
    );
  }
  return out;
}

/** A summer regression with its numbers: how far from the league mean, how much was closed. */
export function regressionText(d: number): string {
  const gap = num(Math.abs(d) / P.regression);
  const side = d < 0 ? "üstündeydi" : "altındaydı";
  return (
    `Ligin ortalamasının ${gap} puan ${side}. Yaz aylarında kadrolar değiştiği için bu fark ` +
    `%${num(P.regression * 100)} oranında kapatıldı: ${delta(d)}.`
  );
}
