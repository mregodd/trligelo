import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { competitionName, leagueName, roundName } from "@/lib/labels";
import type { Fixture, FixtureSide } from "@/lib/types";
import { msg } from "@/messages";

import { ClubLogo } from "./ClubLogo";
import styles from "./FixtureCard.module.css";

const RESULTS = ["G", "B", "M"] as const;

function when(f: Fixture, withCompetition: boolean, lang: Lang): string {
  const t = msg(lang).fixture;
  const day = f.date ? `${fmt(lang).dateLong(f.date)}${f.time ? `, ${f.time}` : ""}` : t.noDate;
  if (!withCompetition) return day;
  const comp = f.week
    ? `${leagueName(f.comp)}, ${t.week(f.week)}`
    : `${competitionName(f.comp, lang)}${f.round ? `, ${roundName(f.round, lang)}` : ""}`;
  return `${comp}. ${day}`;
}

function Side({ lang, side, stakes, align }: { lang: Lang; side: FixtureSide; stakes: number[]; align: "start" | "end" }) {
  const f = fmt(lang);
  return (
    <div className={styles.side} data-align={align}>
      <a href={href(lang, `/takim/${side.slug}/`)} className={styles.club}>
        <ClubLogo src={side.logo} size={24} />
        <span>{side.name}</span>
      </a>
      <span className={styles.rating}>{f.rating(side.r)}</span>
      <span className={styles.stakes} aria-label={msg(lang).fixture.stakes(side.name)}>
        {RESULTS.map((r, i) => (
          <span key={r} title={msg(lang).result.word[r]}>
            <span className={styles.chip} data-r={r} aria-hidden="true">
              {msg(lang).result.letter[r]}
            </span>
            <span className="visually-hidden">{msg(lang).result.word[r]} </span>
            {f.delta(stakes[i])}
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
export function FixtureCard({ f, lang, withCompetition = false }: { f: Fixture; lang: Lang; withCompetition?: boolean }) {
  const t = msg(lang).fixture;
  const [home, draw, away] = f.p;
  return (
    <li className={styles.fixture}>
      {(f.date || withCompetition) && <p className={styles.when}>{when(f, withCompetition, lang)}</p>}
      <div className={styles.match}>
        <Side lang={lang} side={f.home} stakes={f.stakes.home} align="start" />
        <div className={styles.odds}>
          <div className={styles.bar} aria-hidden="true">
            <span style={{ width: `${home}%` }} />
            <span style={{ width: `${draw}%` }} />
            <span style={{ width: `${away}%` }} />
          </div>
          <p className={styles.pct} aria-hidden="true">
            <span>{t.pct(home)}</span>
            <span>
              {t.draw} {t.pct(draw)}
            </span>
            <span>{t.pct(away)}</span>
          </p>
          <p className="visually-hidden">{t.odds(f.home.name, home, draw, f.away.name, away)}</p>
        </div>
        <Side lang={lang} side={f.away} stakes={f.stakes.away} align="end" />
      </div>
    </li>
  );
}

export function FixtureList({ fixtures, lang, withCompetition = false }: { fixtures: Fixture[]; lang: Lang; withCompetition?: boolean }) {
  return (
    <ul className={styles.list}>
      {fixtures.map((f) => (
        <FixtureCard key={`${f.comp}-${f.home.slug}-${f.away.slug}`} f={f} lang={lang} withCompetition={withCompetition} />
      ))}
    </ul>
  );
}
