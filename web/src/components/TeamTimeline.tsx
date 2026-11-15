"use client";

import { useMemo } from "react";

import { dateLong, rating } from "@/lib/format";
import { ADJUSTMENTS, leagueName } from "@/lib/labels";
import type { TeamEvent, TeamSeason } from "@/lib/types";

import { History } from "./History";
import { type ChartBand, type ChartPoint, RatingChart } from "./RatingChart";
import styles from "./TeamTimeline.module.css";

interface Props {
  team: string;
  events: TeamEvent[];
  seasons: TeamSeason[];
  peak: { r: number; date: string } | null;
  low: { r: number; date: string } | null;
  current: number;
  lastMatch: string;
}

/** The club's chart and match list, from one copy of its events (the page ships them once). */
export function TeamTimeline({ team, events, seasons, peak, low, current, lastMatch }: Props) {
  const { points, bands } = useMemo(() => {
    const points: ChartPoint[] = events
      .filter((e) => e.date)
      .map((e) => ({
        t: Date.parse(e.date!),
        date: e.date!,
        r: e.ra,
        d: e.d,
        label:
          e.t === "match"
            ? `${e.opp.name} ${e.gf}-${e.ga}${e.venue === "a" ? ", deplasman" : ""}`
            : ADJUSTMENTS[e.t].name,
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
  }, [events, seasons]);

  const first = points[0];
  return (
    <>
      <section className={styles.chartSection} aria-labelledby="chart-title">
        <div className={styles.chartHead}>
          <h2 id="chart-title">Puan geçmişi</h2>
          <p>
            {first ? `${dateLong(first.date)} – ${dateLong(lastMatch)}` : ""}
            {peak && low && (
              <>
                . En yüksek {rating(peak.r)} ({dateLong(peak.date)}), en düşük {rating(low.r)} (
                {dateLong(low.date)}).
              </>
            )}
          </p>
        </div>
        {points.length > 1 && (
          <RatingChart
            points={points}
            bands={bands}
            summary={`${team} puan grafiği: ${points.length} değişiklik, en yüksek ${peak ? rating(peak.r) : "–"}, en düşük ${low ? rating(low.r) : "–"}, şu an ${rating(current)}. Bütün değerler aşağıdaki maç listesinde.`}
          />
        )}
      </section>

      <section className={styles.matches} aria-label="Maç maç puan değişimi">
        <p className={styles.hint}>
          Bir maçın satırını açınca o maçın puan hesabı görünür.{" "}
          <a href="/metodoloji/">Hesabın kuralları</a>
        </p>
        <History team={team} events={events} seasons={seasons} />
      </section>
    </>
  );
}
