// The arithmetic behind one rating change, as plain sentences (same steps as METODOLOJI §3).
import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site

import { delta, factor, num, RESULT_WORD, result } from "./format";
import { COMPETITIONS } from "./labels";
import type { MatchEvent } from "./types";

export interface CalcStep {
  label: string;
  text: string;
}

const { europe, params: P } = meta;

function scoreLine(m: MatchEvent): string {
  let s = `${m.gf}-${m.ga}`;
  if (m.g90) s += ` (uzatmalarda; 90 dakika ${m.g90[0]}-${m.g90[1]})`;
  if (m.pens) s += `, penaltılar ${m.pens[0]}-${m.pens[1]}`;
  return s;
}

export function steps(team: string, m: MatchEvent): CalcStep[] {
  const out: CalcStep[] = [];
  const opp = m.opp.name;

  let oppSource = `${opp} ${num(m.ro, 1)}`;
  if (m.opp.kind === "foreign" && m.opp.coef != null) {
    oppSource =
      `${opp} ${num(m.ro, 1)}: UEFA kulüp katsayısı ${num(m.opp.coef, 3)}, ` +
      `puanı ${num(europe.a, 0)} + ${num(europe.b, 1)} × ln(1 + ${num(m.opp.coef, 3)})`;
  } else if (m.opp.kind === "amateur") {
    oppSource = `${opp} ${num(m.ro, 1)}: amatör takım, sabit puan (3. Lig ortalaması)`;
  }
  out.push({ label: "Maç öncesi puanlar", text: `${team} ${num(m.r, 1)}; ${oppSource}.` });

  const h = Math.abs(m.h);
  const closed = Math.round(h) === Math.round(P.homeClosed) ? " (seyircisiz maç)" : "";
  const where =
    m.venue === "n"
      ? "Tarafsız saha, ev avantajı yok."
      : m.venue === "h"
        ? `${team} ev sahibi: +${num(h, 0)} puan${closed}.`
        : `${opp} ev sahibi: ${team} için −${num(h, 0)} puan${closed}.`;
  out.push({ label: "Saha", text: where });

  const diff = m.r + m.h - m.ro;
  const hTerm = m.h === 0 ? "" : m.h > 0 ? ` + ${num(h, 0)}` : ` − ${num(h, 0)}`;
  out.push({
    label: "Fark",
    text: `${num(m.r, 1)}${hTerm} − ${num(m.ro, 1)} = ${num(diff, 1)}`,
  });
  out.push({
    label: "Beklenen skor",
    text: `E = 1 / (1 + 10^(${num(-diff, 1)} / 400)) = ${num(m.e, 3)}`,
  });

  const r = result(m.s);
  let res = `${scoreLine(m)}, ${RESULT_WORD[r]}: S = ${factor(m.s)}.`;
  if (m.pens) res += " Penaltı atışları Elo'da beraberlik sayılır.";
  out.push({ label: "Sonuç", text: res });

  const factors: string[] = [];
  factors.push(
    m.k === P.k
      ? `K = ${num(m.k, 0)}`
      : `K = ${num(m.k, 0)} (yeni takımın ilk ${P.provisionalGames} maçı: ${num(P.k, 0)} × ${factor(P.provisionalFactor)})`,
  );
  const comp = COMPETITIONS[m.comp]?.name ?? m.comp;
  const wWhy = m.opp.kind === "amateur" ? `${comp}, amatör rakip` : comp;
  factors.push(`W = ${factor(m.w)} (${wWhy})`);
  const margin = Math.abs(m.gf - m.ga);
  factors.push(
    margin <= 1
      ? `G = 1`
      : `G = ${factor(m.g)} (${margin} farklı)`,
  );
  out.push({ label: "Çarpanlar", text: factors.join(", ") + "." });

  out.push({
    label: "Değişim",
    text:
      `${factor(m.k)} × ${factor(m.w)} × ${factor(m.g)} × ` +
      `(${factor(m.s)} − ${num(m.e, 3)}) = ${delta(m.d, 1)}. ` +
      `Yeni puan ${num(m.ra, 1)}.`,
  });
  return out;
}
