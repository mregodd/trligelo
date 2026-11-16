"use client";

import { useMemo } from "react";

import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { adjustments, leagueName } from "@/lib/labels";
import type { TeamEvent, TeamSeason } from "@/lib/types";
import { msg } from "@/messages";

import { History } from "./History";
import { type ChartBand, type ChartPoint, RatingChart } from "./RatingChart";
import styles from "./TeamTimeline.module.css";

interface Props {
  lang: Lang;
  team: string;
  events: TeamEvent[];
  seasons: TeamSeason[];
  peak: { r: number; date: string } | null;
  low: { r: number; date: string } | null;
  current: number;
  lastMatch: string;
}

/** The club's chart and match list, from one copy of its events (the page ships them once). */
export function TeamTimeline({ lang, team, events, seasons, peak, low, current, lastMatch }: Props) {
  const t = msg(lang).timeline;
  const f = fmt(lang);
  const { points, bands } = useMemo(() => {
    const adj = adjustments(lang);
    const points: ChartPoint[] = events
      .filter((e) => e.date)
      .map((e) => ({
        t: Date.parse(e.date!),
        date: e.date!,
        r: e.ra,
        d: e.d,
        label:
          e.t === "match"
            ? `${e.opp.name} ${e.gf}-${e.ga}${e.venue === "a" ? msg(lang).timeline.away : ""}`
            : adj[e.t].name,
      }));
    const starts = seasons.map((s) => {
      const first = events.find((e) => e.season === s.season && e.date);
      return first ? Date.parse(first.date!) : NaN;
    });
    const end = points[points.length - 1]?.t ?? 0;
    const bands: ChartBand[] = seasons
      .map((s, i) => ({
        season: s.season,
        league: s.league,
        leagueName: leagueName(s.league),
        start: starts[i],
        end: starts.slice(i + 1).find((v) => !Number.isNaN(v)) ?? end,
      }))
      .filter((b) => !Number.isNaN(b.start));
    return { points, bands };
  }, [events, seasons, lang]);

  const first = points[0];
  return (
    <>
      <section className={styles.chartSection} aria-labelledby="chart-title">
        <div className={styles.chartHead}>
          <h2 id="chart-title">{t.title}</h2>
          <p>
            {first ? `${f.dateLong(first.date)} – ${f.dateLong(lastMatch)}` : ""}
            {peak && low && (
              <>
                . {t.high} {f.rating(peak.r)} ({f.dateLong(peak.date)}), {t.low} {f.rating(low.r)} (
                {f.dateLong(low.date)}).
              </>
            )}
          </p>
        </div>
        {points.length > 1 && (
          <RatingChart
            lang={lang}
            points={points}
            bands={bands}
            summary={t.summary(
              team,
              points.length,
              peak ? f.rating(peak.r) : "–",
              low ? f.rating(low.r) : "–",
              f.rating(current),
            )}
          />
        )}
      </section>

      <section className={styles.matches} aria-label={t.list}>
        <p className={styles.hint}>
          {t.hint} <a href={href(lang, "/methodology/")}>{t.rules}</a>
        </p>
        <History lang={lang} team={team} events={events} seasons={seasons} />
      </section>
    </>
  );
}
