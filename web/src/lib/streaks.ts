// The runs a club's matches belong to (wins in a row, unbeaten, ...), told in the match box.
// Only type imports here, so `npm test` can run streaks.test.mjs on this file as it is.
import type { TeamEvent } from "./types";

export type StreakKind =
  | "wins"
  | "losses"
  | "unbeaten"
  | "winless"
  | "endedWins"
  | "endedLosses"
  | "endedUnbeaten"
  | "endedWinless";

export interface Streak {
  kind: StreakKind;
  n: number;
}

/**
 * For each match worth a sentence (by seq): the run it extended or ended. Runs of wins or
 * of defeats count from the third match, runs with draws in them (unbeaten, without a win)
 * from the fifth. Events must be in order; adjustments are skipped.
 */
export function streaks(events: TeamEvent[]): Map<number, Streak> {
  const out = new Map<number, Streak>();
  let [wins, losses, unbeaten, winless] = [0, 0, 0, 0]; // runs before the match
  for (const e of events) {
    if (e.t !== "match") continue;
    let note: Streak | null = null;
    if (e.s === 1) {
      if (losses >= 3) note = { kind: "endedLosses", n: losses };
      else if (winless >= 5) note = { kind: "endedWinless", n: winless };
      else if (wins >= 2) note = { kind: "wins", n: wins + 1 };
      [wins, losses, unbeaten, winless] = [wins + 1, 0, unbeaten + 1, 0];
    } else if (e.s === 0) {
      if (wins >= 3) note = { kind: "endedWins", n: wins };
      else if (unbeaten >= 5) note = { kind: "endedUnbeaten", n: unbeaten };
      else if (losses >= 2) note = { kind: "losses", n: losses + 1 };
      [wins, losses, unbeaten, winless] = [0, losses + 1, 0, winless + 1];
    } else {
      if (wins >= 3) note = { kind: "endedWins", n: wins };
      else if (losses >= 3) note = { kind: "endedLosses", n: losses };
      else if (unbeaten >= 4) note = { kind: "unbeaten", n: unbeaten + 1 };
      else if (winless >= 4) note = { kind: "winless", n: winless + 1 };
      [wins, losses, unbeaten, winless] = [0, 0, unbeaten + 1, winless + 1];
    }
    if (note) out.set(e.seq, note);
  }
  return out;
}
