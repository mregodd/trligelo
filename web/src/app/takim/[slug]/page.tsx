import type { Metadata } from "next";

import { Ruler } from "@/components/Ruler";
import { TeamTimeline } from "@/components/TeamTimeline";
import { getMeta, getTeam, getTeams } from "@/lib/data";
import { dateShort, delta, rating } from "@/lib/format";
import { groupName, leagueName, leagueSlug } from "@/lib/labels";
import type { MatchEvent } from "@/lib/types";

import styles from "./page.module.css";

export function generateStaticParams() {
  return getTeams().map((t) => ({ slug: t.slug }));
}

type Params = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { slug } = await params;
  const t = getTeam(slug);
  return {
    title: `${t.name} Elo puanı`,
    description: `${t.name}: Elo puanı ${rating(t.rating)}, ${leagueName(t.league)}. Puanın maç maç nasıl değiştiği.`,
  };
}


export default async function TeamPage({ params }: Params) {
  const { slug } = await params;
  const team = getTeam(slug);
  const meta = getMeta();
  const last = [...team.events].reverse().find((e): e is MatchEvent => e.t === "match");
  // The ruler needs only position data for each club.
  const active = getTeams()
    .filter((t) => t.active)
    .map(({ slug, name, league, rating, leagueRank }) => ({ slug, name, league, rating, leagueRank }));

  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <div className={styles.top}>
            <div>
              <h1>{team.name}</h1>
              <p className={styles.where}>
                {team.active ? (
                  <>
                    <a href={`/lig/${leagueSlug(team.league)}/`}>{leagueName(team.league)}</a>
                    {team.group ? `, ${groupName(team.group)}` : ""}
                  </>
                ) : (
                  <>
                    Son olarak {team.lastSeason} sezonunda {leagueName(team.league)}'de oynadı. Şu an
                    profesyonel ligde değil; puanı o günden beri değişmedi.
                  </>
                )}
              </p>
              {team.official !== team.name.toLocaleUpperCase("tr-TR") && (
                <p className={styles.official}>TFF'deki adı: {team.official}</p>
              )}
            </div>
            <dl className={styles.figures}>
              <div className={styles.hero}>
                <dt>Elo puanı</dt>
                <dd>{rating(team.rating)}</dd>
              </div>
              {team.rank != null && (
                <div>
                  <dt>Genel sıra</dt>
                  <dd>
                    {team.rank}
                    <span> / {meta.activeTeams}</span>
                  </dd>
                </div>
              )}
              {team.leagueRank != null && (
                <div>
                  <dt>{leagueName(team.league)} sırası</dt>
                  <dd>{team.leagueRank}</dd>
                </div>
              )}
              {last && (
                <div className={styles.last}>
                  <dt>Son maç</dt>
                  <dd>
                    <a href={`#mac-${last.seq}`}>{delta(last.d)}</a>
                    <span>
                      {last.opp.name} {last.gf}-{last.ga}, {dateShort(last.date)}
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
              label={`${team.name}, ${rating(team.rating)} puanla bütün kulüpler arasında ${team.rank}. sırada.`}
            />
          )}
        </div>
      </section>

      <div className="wrap">
        <TeamTimeline
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
