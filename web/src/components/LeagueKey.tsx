import type { LeagueCode } from "@/lib/types";

import styles from "./LeagueKey.module.css";

/** A small swatch beside a league's name: identity comes from the mark, never from text colour. */
export function LeagueKey({ code }: { code: LeagueCode }) {
  return <span className={styles.key} data-league={code} aria-hidden="true" />;
}
