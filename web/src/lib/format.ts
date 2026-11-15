// Number and date formatting per language (locale and month names from messages/): Turkish
// with a decimal comma, English with a decimal point; both with a true minus sign and no
// digit grouping (ratings read "1657").
import { msg } from "@/messages";

import type { Lang } from "./i18n";

const MINUS = "−";

function parts(iso: string) {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return { y, m, d };
}

export function fmt(lang: Lang) {
  const { locale, months } = msg(lang);
  const num = (x: number, digits = 0) =>
    x
      .toLocaleString(locale, { minimumFractionDigits: digits, maximumFractionDigits: digits, useGrouping: false })
      .replace("-", MINUS);
  return {
    num,
    /** Up to `max` decimals, no trailing zeros: 1.875 -> "1,875" / "1.875", 1 -> "1". */
    factor: (x: number, max = 3) =>
      x.toLocaleString(locale, { maximumFractionDigits: max, useGrouping: false }).replace("-", MINUS),
    rating: (x: number) => num(Math.round(x)),
    /** Signed change: "+9,9", "−2,1", "0,0". */
    delta: (x: number, digits = 1) => {
      const rounded = Number(x.toFixed(digits));
      if (rounded === 0) return num(0, digits);
      return (rounded > 0 ? "+" : MINUS) + num(Math.abs(rounded), digits);
    },
    /** "26 Ekim 2026" / "26 October 2026" */
    dateLong: (iso: string) => {
      const { y, m, d } = parts(iso);
      return `${d} ${months[m - 1]} ${y}`;
    },
    /** "26 Eki" / "26 Oct" */
    dateShort: (iso: string) => {
      const { m, d } = parts(iso);
      return `${d} ${months[m - 1].slice(0, 3)}`;
    },
  };
}

export type Result = "G" | "B" | "M"; // the data's own letters: win, draw, loss

export function result(s: number): Result {
  return s === 1 ? "G" : s === 0 ? "M" : "B";
}
