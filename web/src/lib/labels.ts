import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site
import { msg } from "@/messages";

import { fmt } from "./format";
import type { Lang } from "./i18n";
import type { AdjustmentKind, LeagueCode } from "./types";

const P = meta.params;

// League names are proper names: the same in every language.
export const LEAGUES: { code: LeagueCode; name: string; slug: string; tier: number }[] = [
  { code: "SL", name: "Süper Lig", slug: "super-lig", tier: 1 },
  { code: "1L", name: "1. Lig", slug: "1-lig", tier: 2 },
  { code: "2L", name: "2. Lig", slug: "2-lig", tier: 3 },
  { code: "3L", name: "3. Lig", slug: "3-lig", tier: 4 },
];

export const leagueName = (code: string) => LEAGUES.find((l) => l.code === code)?.name ?? code;
export const leagueSlug = (code: string) => LEAGUES.find((l) => l.code === code)?.slug ?? code;

export const competitionName = (comp: string, lang: Lang) =>
  msg(lang).competitions[comp]?.name ?? leagueName(comp);
export const competitionShort = (comp: string, lang: Lang) =>
  msg(lang).competitions[comp]?.short ?? msg(lang).leagueShort;

/** A TFF round name: "4.Tur" -> "4. Tur" / "Round 4", "Yarı Final" -> "Semi-final". */
export function roundName(round: string, lang: Lang): string {
  const m = msg(lang).rounds;
  const tur = /^(\d+)\.\s?Tur$/i.exec(round);
  if (tur) return m.tur(tur[1]);
  return m.known[round.toLocaleLowerCase("tr-TR")] ?? round;
}

const IS_LEAGUE = new Set(["SL", "1L", "2L", "3L"]);
const IS_EUROPE = new Set(["UCL", "UEL", "UECL"]);

/** "Avrupa Ligi, son 16" / "Ziraat Türkiye Kupası, Yarı Final" / "1. Lig play-off, Final" */
export function competitionLabel(comp: string, round: string | null, lang: Lang): string {
  const name = competitionName(comp, lang);
  if (!round) return name;
  if (IS_EUROPE.has(comp)) return `${name}, ${msg(lang).europeRounds[round] ?? round}`;
  if (IS_LEAGUE.has(comp)) return `${name} play-off, ${roundName(round, lang)}`; // league rounds are play-offs
  return `${name}, ${roundName(round, lang)}`;
}

export const isEurope = (comp: string) => IS_EUROPE.has(comp);

/** Where in its competition a match was: "12. hafta" in a league, the round in a cup or Europe. */
export function stageName(comp: string, round: string | null, week: number | null, lang: Lang): string | null {
  if (round) return IS_EUROPE.has(comp) ? (msg(lang).europeRounds[round] ?? round) : roundName(round, lang);
  return week ? msg(lang).fixture.week(week) : null;
}

/** Names and reasons of the rating adjustments, with the model's numbers filled in. */
export function adjustments(lang: Lang): Record<AdjustmentKind, { name: string; why: string }> {
  const { num } = fmt(lang);
  return msg(lang).adjustments({
    pct: num(P.regression * 100),
    gap: num(Math.abs(P.newcomer)),
    anchor: num(P.anchor),
    below: P.newcomer < 0,
  });
}

/** "01" -> "1. Grup" / "Group 1", "Beyaz" -> "Beyaz Grup" / "White Group" */
export function groupName(group: string, lang: Lang): string {
  const m = msg(lang).groups;
  return /^\d+$/.test(group) ? m.numbered(Number(group)) : m.named(m.colours[group] ?? group);
}
