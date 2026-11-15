// Turkish number and date formatting. Decimal comma, a true minus sign for negatives.

const MINUS = "−";

/** Ratings stay below 10 000 and read like "1657" (as on the ruler), so no digit grouping. */
export function num(x: number, digits = 0): string {
  return x
    .toLocaleString("tr-TR", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
      useGrouping: false,
    })
    .replace("-", MINUS);
}

/** Up to `max` decimals, no trailing zeros: 1.875 -> "1,875", 1.5 -> "1,5", 1 -> "1". */
export function factor(x: number, max = 3): string {
  return x
    .toLocaleString("tr-TR", { maximumFractionDigits: max, useGrouping: false })
    .replace("-", MINUS);
}

export function rating(x: number): string {
  return num(Math.round(x));
}

/** Signed change: "+9,9", "−2,1", "0,0". */
export function delta(x: number, digits = 1): string {
  const rounded = Number(x.toFixed(digits));
  if (rounded === 0) return num(0, digits);
  return (rounded > 0 ? "+" : MINUS) + num(Math.abs(rounded), digits);
}

const MONTHS = [
  "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
];
const MONTHS_SHORT = MONTHS.map((m) => m.slice(0, 3));

function parts(iso: string) {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return { y, m, d };
}

/** "26 Ekim 2026" */
export function dateLong(iso: string): string {
  const { y, m, d } = parts(iso);
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

/** "26 Eki" (same season context) */
export function dateShort(iso: string): string {
  const { m, d } = parts(iso);
  return `${d} ${MONTHS_SHORT[m - 1]}`;
}

export function result(s: number): "G" | "B" | "M" {
  return s === 1 ? "G" : s === 0 ? "M" : "B";
}

export const RESULT_WORD = { G: "galibiyet", B: "beraberlik", M: "mağlubiyet" } as const;
