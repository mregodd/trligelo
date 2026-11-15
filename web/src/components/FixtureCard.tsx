import { dateLong, delta, rating } from "@/lib/format";
import { COMPETITIONS, leagueName } from "@/lib/labels";
import type { Fixture, FixtureSide } from "@/lib/types";

import { ClubLogo } from "./ClubLogo";
import styles from "./FixtureCard.module.css";

const RESULT = ["G", "B", "M"] as const;
const RESULT_WORD = ["galibiyet", "beraberlik", "mağlubiyet"];

/** "4.Tur" -> "4. Tur" (TFF writes cup rounds without the space). */
const roundName = (r: string) => r.replace(/(\d)\.(\S)/, "$1. $2");

function when(f: Fixture, withCompetition: boolean): string {
  const day = f.date ? `${dateLong(f.date)}${f.time ? `, ${f.time}` : ""}` : "Tarih henüz açıklanmadı";
  if (!withCompetition) return day;
  const comp = f.week
    ? `${leagueName(f.comp)}, ${f.week}. hafta`
    : `${COMPETITIONS[f.comp]?.name ?? f.comp}${f.round ? `, ${roundName(f.round)}` : ""}`;
  return `${comp}. ${day}`;
}

function Side({ side, stakes, align }: { side: FixtureSide; stakes: number[]; align: "start" | "end" }) {
  return (
    <div className={styles.side} data-align={align}>
      <a href={`/takim/${side.slug}/`} className={styles.club}>
        <ClubLogo src={side.logo} size={24} />
        <span>{side.name}</span>
      </a>
      <span className={styles.rating}>{rating(side.r)}</span>
      <span className={styles.stakes} aria-label={`${side.name} için puan değişimi`}>
        {RESULT.map((r, i) => (
          <span key={r} title={RESULT_WORD[i]}>
            <span className={styles.chip} data-r={r} aria-hidden="true">
              {r}
            </span>
            <span className="visually-hidden">{RESULT_WORD[i]} </span>
            {delta(stakes[i])}
          </span>
        ))}
      </span>
    </div>
  );
}

/**
 * One upcoming match: both clubs with today's ratings, win/draw/loss chances as one bar, and
 * what each result would do to each club's rating (one-goal margin).
 */
export function FixtureCard({ f, withCompetition = false }: { f: Fixture; withCompetition?: boolean }) {
  const [home, draw, away] = f.p;
  return (
    <li className={styles.fixture}>
      {(f.date || withCompetition) && <p className={styles.when}>{when(f, withCompetition)}</p>}
      <div className={styles.match}>
        <Side side={f.home} stakes={f.stakes.home} align="start" />
        <div className={styles.odds}>
          <div className={styles.bar} aria-hidden="true">
            <span style={{ width: `${home}%` }} />
            <span style={{ width: `${draw}%` }} />
            <span style={{ width: `${away}%` }} />
          </div>
          <p className={styles.pct}>
            <span>%{home}</span>
            <span>beraberlik %{draw}</span>
            <span>%{away}</span>
          </p>
          <p className="visually-hidden">
            Şanslar: {f.home.name} kazanır %{home}, beraberlik %{draw}, {f.away.name} kazanır %{away}.
          </p>
        </div>
        <Side side={f.away} stakes={f.stakes.away} align="end" />
      </div>
    </li>
  );
}

export function FixtureList({ fixtures, withCompetition = false }: { fixtures: Fixture[]; withCompetition?: boolean }) {
  return (
    <ul className={styles.list}>
      {fixtures.map((f) => (
        <FixtureCard key={`${f.comp}-${f.home.slug}-${f.away.slug}`} f={f} withCompetition={withCompetition} />
      ))}
    </ul>
  );
}
