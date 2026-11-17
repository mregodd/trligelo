import type { Metadata } from "next";

import { ClubLogo } from "@/components/ClubLogo";
import { FixtureList } from "@/components/FixtureCard";
import { Ruler } from "@/components/Ruler";
import { TeamTimeline } from "@/components/TeamTimeline";
import { getMeta, getTeam, getTeams } from "@/lib/data";
import { fmt } from "@/lib/format";
import { alternates, href, type Lang } from "@/lib/i18n";
import { groupName, leagueName, leagueSlug } from "@/lib/labels";
import type { MatchEvent } from "@/lib/types";
import { msg } from "@/messages";

import styles from "./Team.module.css";

export const teamParams = () => getTeams().map((c) => ({ slug: c.slug }));

export function teamMetadata(lang: Lang, slug: string): Metadata {
  const c = getTeam(slug);
  const t = msg(lang).team;
  return {
    title: t.title(c.name),
    description: t.description(c.name, fmt(lang).rating(c.rating), leagueName(c.league)),
    alternates: alternates(lang, `/club/${slug}/`),
  };
}

export function TeamView({ lang, slug }: { lang: Lang; slug: string }) {
  const t = msg(lang).team;
  const f = fmt(lang);
  const team = getTeam(slug);
  const meta = getMeta();
  const last = [...team.events].reverse().find((e): e is MatchEvent => e.t === "match");
  // The ruler needs only position data for each club.
  const active = getTeams()
    .filter((c) => c.active)
    .map(({ slug, name, league, rating, leagueRank }) => ({ slug, name, league, rating, leagueRank }));

  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <div className={styles.top}>
            <div>
              <div className={styles.title}>
                <ClubLogo src={team.logo} size={56} />
                <h1>{team.name}</h1>
              </div>
              <p className={styles.where}>
                {team.active ? (
                  <>
                    <a href={href(lang, `/league/${leagueSlug(team.league)}/`)}>{leagueName(team.league)}</a>
                    {team.group ? `, ${groupName(team.group, lang)}` : ""}
                  </>
                ) : team.withdrawn ? (
                  t.withdrew(team.lastSeason, leagueName(team.league), f.dateLong(team.withdrawn))
                ) : (
                  t.left(team.lastSeason, leagueName(team.league))
                )}
              </p>
              {team.official && team.official !== team.name.toLocaleUpperCase("tr-TR") && (
                <p className={styles.official}>
                  {t.official}: {team.official}
                </p>
              )}
            </div>
            <dl className={styles.figures}>
              <div className={styles.hero}>
                <dt>{t.rating}</dt>
                <dd>{f.rating(team.rating)}</dd>
              </div>
              {team.rank != null && (
                <div>
                  <dt>{t.rank}</dt>
                  <dd>
                    {team.rank}
                    <span> / {meta.activeTeams}</span>
                  </dd>
                </div>
              )}
              {team.leagueRank != null && (
                <div>
                  <dt>{t.leagueRank(leagueName(team.league))}</dt>
                  <dd>{team.leagueRank}</dd>
                </div>
              )}
              {last && (
                <div className={styles.last}>
                  <dt>{t.last}</dt>
                  <dd>
                    <a href={`#match-${last.seq}`}>{f.delta(last.d)}</a>
                    <span>
                      {last.opp.name} {last.gf}-{last.ga}, {f.dateShort(last.date)}
                    </span>
                  </dd>
                </div>
              )}
            </dl>
          </div>
          {team.active && (
            <Ruler
              teams={active}
              pinned={team.slug}
              label={t.ruler(team.name, f.rating(team.rating), team.rank)}
              lang={lang}
            />
          )}
        </div>
      </section>

      <div className="wrap">
        {team.next.length > 0 && (
          <section className={styles.next} aria-labelledby="next-title">
            <h2 id="next-title">{t.next(team.next.length)}</h2>
            <FixtureList fixtures={team.next} lang={lang} withCompetition />
          </section>
        )}
        <TeamTimeline
          lang={lang}
          team={team.name}
          events={team.events}
          seasons={team.seasons}
          peak={team.peak}
          low={team.low}
          current={team.rating}
          lastMatch={meta.lastMatch}
        />
      </div>
    </>
  );
}
