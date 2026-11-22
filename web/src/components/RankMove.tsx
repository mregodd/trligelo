import type { Lang } from "@/lib/i18n";
import { msg } from "@/messages";

import styles from "./Standings.module.css";

/** Places gained or lost over the week, as a small arrow after a rank; nothing when none. */
export function RankMove({ n, lang }: { n: number | null; lang: Lang }) {
  if (!n) return null;
  const t = msg(lang).standings;
  return (
    <span className={`${styles.move} ${n > 0 ? "gain" : "loss"}`} title={n > 0 ? t.up(n) : t.down(-n)}>
      <span aria-hidden="true">
        {n > 0 ? "▲" : "▼"}
        {Math.abs(n)}
      </span>
      <span className="visually-hidden"> ({n > 0 ? t.up(n) : t.down(-n)})</span>
    </span>
  );
}
