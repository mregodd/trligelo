import meta from "@/data/meta.json"; // bundled: the model numbers of the run that built the site

import { num } from "./format";
import type { AdjustmentKind, LeagueCode } from "./types";

const P = meta.params;

export const LEAGUES: { code: LeagueCode; name: string; slug: string; tier: number }[] = [
  { code: "SL", name: "Süper Lig", slug: "super-lig", tier: 1 },
  { code: "1L", name: "1. Lig", slug: "1-lig", tier: 2 },
  { code: "2L", name: "2. Lig", slug: "2-lig", tier: 3 },
  { code: "3L", name: "3. Lig", slug: "3-lig", tier: 4 },
];

export const leagueName = (code: string) => LEAGUES.find((l) => l.code === code)?.name ?? code;
export const leagueSlug = (code: string) => LEAGUES.find((l) => l.code === code)?.slug ?? code;

export const COMPETITIONS: Record<string, { name: string; short: string }> = {
  SL: { name: "Süper Lig", short: "Lig" },
  "1L": { name: "1. Lig", short: "Lig" },
  "2L": { name: "2. Lig", short: "Lig" },
  "3L": { name: "3. Lig", short: "Lig" },
  TK: { name: "Ziraat Türkiye Kupası", short: "Kupa" },
  SK: { name: "Süper Kupa", short: "Süper Kupa" },
  UCL: { name: "Şampiyonlar Ligi", short: "ŞL" },
  UEL: { name: "Avrupa Ligi", short: "AL" },
  UECL: { name: "Konferans Ligi", short: "KL" },
};

const EUROPE_ROUNDS: Record<string, string> = {
  PR: "ön eleme",
  Q1: "1. eleme turu",
  Q2: "2. eleme turu",
  Q3: "3. eleme turu",
  PO: "play-off turu",
  GS: "grup aşaması",
  LP: "lig aşaması",
  KPO: "eleme play-off'u",
  R32: "son 32",
  R16: "son 16",
  QF: "çeyrek final",
  SF: "yarı final",
  F: "final",
};

const IS_LEAGUE = new Set(["SL", "1L", "2L", "3L"]);
const IS_EUROPE = new Set(["UCL", "UEL", "UECL"]);

/** "Avrupa Ligi, son 16" / "Ziraat Türkiye Kupası, Yarı Final" / "1. Lig play-off, Final" */
export function competitionLabel(comp: string, round: string | null): string {
  const name = COMPETITIONS[comp]?.name ?? comp;
  if (!round) return name;
  if (IS_EUROPE.has(comp)) return `${name}, ${EUROPE_ROUNDS[round] ?? round}`;
  if (IS_LEAGUE.has(comp)) return `${name} play-off, ${round}`; // league rounds are play-offs
  return `${name}, ${round}`;
}

export const isEurope = (comp: string) => IS_EUROPE.has(comp);

export const ADJUSTMENTS: Record<AdjustmentKind, { name: string; why: string }> = {
  promotion: {
    name: "Yükselme düzeltmesi",
    why: "Üst lige çıkan takım, yeni ligine uyum için puan alır.",
  },
  relegation: {
    name: "Düşme düzeltmesi",
    why: "Alt lige düşen takım puan kaybeder.",
  },
  regression: {
    name: "Ortalamaya çekme",
    why: `Yaz aylarında kadrolar değiştiği için puan, ligin ortalamasına doğru %${num(P.regression * 100)} çekilir.`,
  },
  anchor: {
    name: "Ölçek ayarı",
    why: `Bütün puanlar aynı miktarda kaydırılır, 3. Lig ortalaması ${num(P.anchor)} olur. Sıralamayı değiştirmez.`,
  },
  cup: { name: "Türkiye Kupası şampiyonluğu", why: "Kupa şampiyonuna bonus." },
  supercup: { name: "Süper Kupa şampiyonluğu", why: "Süper Kupa şampiyonuna bonus." },
  champion: { name: "Şampiyonluk bonusu", why: "" },
  newcomer: {
    name: "Profesyonel lige katıldı",
    why: `Amatör ligden gelen takım, 3. Lig ortalamasının ${num(Math.abs(P.newcomer))} puan ${P.newcomer < 0 ? "altından" : "üstünden"} başlar.`,
  },
  return: {
    name: "Profesyonel lige döndü",
    why: "Amatöre düşüp dönen takım yeni gelen gibi başlar.",
  },
};

/** "01" -> "1. Grup", "Beyaz" -> "Beyaz Grup" */
export function groupName(group: string): string {
  return /^\d+$/.test(group) ? `${Number(group)}. Grup` : `${group} Grup`;
}
