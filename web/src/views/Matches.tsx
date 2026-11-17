import type { Metadata } from "next";

import { FixtureList } from "@/components/FixtureCard";
import { getFixtures, getMeta } from "@/lib/data";
import { fmt } from "@/lib/format";
import { alternates, type Lang } from "@/lib/i18n";
import { competitionName, groupName, leagueName, leagueSlug } from "@/lib/labels";
import { msg } from "@/messages";

import styles from "./Matches.module.css";

export function matchesMetadata(lang: Lang): Metadata {
  return {
    title: msg(lang).matches.title,
    description: msg(lang).matches.description,
    alternates: alternates(lang, "/fixtures/"),
  };
}

export function MatchesView({ lang }: { lang: Lang }) {
  const t = msg(lang).matches;
  const { rounds, cup } = getFixtures();
  const meta = getMeta();
  const sections = rounds.map((r) => ({
    id: `${leagueSlug(r.league)}${r.group ? `-${r.group.toLocaleLowerCase("tr-TR")}` : ""}`,
    title: `${leagueName(r.league)}${r.group ? `, ${groupName(r.group, lang)}` : ""}`,
    ...r,
  }));
  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <h1>{t.title}</h1>
          <p className={styles.lead}>{t.lead(fmt(lang).dateLong(meta.lastMatch))}</p>
          <ul className={styles.jump} aria-label={t.sections}>
            {sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`}>{s.title}</a>
              </li>
            ))}
            {cup.length > 0 && (
              <li>
                <a href="#kupa">{t.cup}</a>
              </li>
            )}
          </ul>
        </div>
      </section>

      <div className="wrap">
        {sections.map((s) => (
          <section key={s.id} id={s.id} className={styles.round}>
            <h2>
              {s.title}, {t.week(s.week)}
            </h2>
            {s.matches.every((m) => !m.date) && <p className={styles.note}>{t.noDates}</p>}
            <FixtureList fixtures={s.matches} lang={lang} />
          </section>
        ))}
        {cup.length > 0 && (
          <section id="kupa" className={styles.round}>
            <h2>{competitionName("TK", lang)}</h2>
            <FixtureList fixtures={cup} lang={lang} withCompetition />
          </section>
        )}
      </div>
    </>
  );
}
