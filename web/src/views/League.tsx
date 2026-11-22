import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ClubLogo } from "@/components/ClubLogo";
import { Form } from "@/components/Form";
import { RankMove } from "@/components/RankMove";
import { Ruler } from "@/components/Ruler";
import table from "@/components/Standings.module.css";
import { getLeagues, getMeta, getTeamMap, getTeams } from "@/lib/data";
import { fmt } from "@/lib/format";
import { alternates, href, type Lang } from "@/lib/i18n";
import { groupName, LEAGUES } from "@/lib/labels";
import { msg } from "@/messages";

import styles from "./League.module.css";

export const leagueParams = () => LEAGUES.map((l) => ({ slug: l.slug }));

export function leagueMetadata(lang: Lang, slug: string): Metadata {
  const league = LEAGUES.find((l) => l.slug === slug);
  return {
    title: league ? msg(lang).league.title(league.name) : "Lig",
    alternates: alternates(lang, `/league/${slug}/`),
  };
}

export function LeagueView({ lang, slug }: { lang: Lang; slug: string }) {
  const league = LEAGUES.find((l) => l.slug === slug);
  if (!league) notFound();
  const t = msg(lang).league;
  const f = fmt(lang);

  const meta = getMeta();
  const teams = getTeamMap();
  const active = getTeams()
    .filter((c) => c.active)
    .map(({ slug, name, league, rating, leagueRank }) => ({ slug, name, league, rating, leagueRank }));
  const groups = getLeagues().find((l) => l.code === league.code)?.groups ?? [];
  const members = groups.flatMap((g) => g.teams.map((s) => teams.get(s)!));
  const ratings = members.map((c) => c.rating);
  const mean = ratings.reduce((a, b) => a + b, 0) / ratings.length;

  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <h1>{league.name}</h1>
          <p className={styles.lead}>
            {t.lead(
              members.length,
              f.rating(Math.min(...ratings)),
              f.rating(Math.max(...ratings)),
              f.rating(mean),
              f.dateLong(meta.lastMatch),
            )}
          </p>
          <Ruler teams={active} focusLeague={league.code} label={t.ruler(league.name)} lang={lang} />
        </div>
      </section>

      <div className="wrap">
        {groups.map((group) => (
          <section key={group.name ?? "all"} className={styles.group}>
            {group.name && <h2>{groupName(group.name, lang)}</h2>}
            <table className={table.table}>
              <caption className="visually-hidden">
                {league.name}
                {group.name ? `, ${groupName(group.name, lang)}` : ""}: {t.caption}
              </caption>
              <thead>
                <tr>
                  <th scope="col" className="num" title={msg(lang).standings.moveTitle}>
                    {t.head[0]}
                  </th>
                  <th scope="col">{t.head[1]}</th>
                  <th scope="col" className="num">
                    {t.head[2]}
                  </th>
                  <th scope="col" className="num" title={t.weekTitle}>
                    {t.head[3]}
                  </th>
                  <th scope="col" className={table.formCol}>
                    {t.head[4]}
                  </th>
                  <th scope="col" className={`num ${table.wideOnly}`}>
                    {t.head[5]}
                  </th>
                </tr>
              </thead>
              <tbody>
                {group.teams.map((s, i) => {
                  const c = teams.get(s)!;
                  return (
                    <tr key={s}>
                      <td className={`num ${table.rankCell}`}>
                        {i + 1}
                        <RankMove n={c.groupMove} lang={lang} />
                      </td>
                      <th scope="row" className={table.club}>
                        <ClubLogo src={c.logo} keepSpace />
                        <a href={href(lang, `/club/${s}/`)}>{c.name}</a>
                      </th>
                      <td className={`num ${table.rating}`}>{f.rating(c.rating)}</td>
                      <td className={`num ${c.week > 0 ? "gain" : c.week < 0 ? "loss" : "muted"}`}>
                        {f.delta(c.week)}
                      </td>
                      <td className={table.formCol}>
                        <Form form={c.form} lang={lang} />
                      </td>
                      <td className={`num muted ${table.wideOnly}`}>{c.rank}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>
        ))}
        <p className={styles.note}>
          {t.note} <a href={href(lang, "/methodology/")}>{t.how}</a>
        </p>
      </div>
    </>
  );
}
