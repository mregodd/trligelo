"use client";

import { useRouter } from "next/navigation";
import { useMemo, useRef, useState } from "react";

import { rating as fmtRating } from "@/lib/format";
import { LEAGUES } from "@/lib/labels";
import type { LeagueCode } from "@/lib/types";

import styles from "./Ruler.module.css";

export interface RulerTeam {
  slug: string;
  name: string;
  league: LeagueCode;
  rating: number;
  leagueRank: number | null;
}

interface Props {
  teams: RulerTeam[];
  /** A club lit from outside (the hovered table row). */
  highlight?: string | null;
  onHover?: (slug: string | null) => void;
  /** League page: this lane stays strong, the others step back. */
  focusLeague?: LeagueCode;
  /** Club page: this club is always marked. */
  pinned?: string;
  label: string;
}

const LANE_VAR: Record<LeagueCode, string> = {
  SL: "var(--band-sl)",
  "1L": "var(--band-l1)",
  "2L": "var(--band-l2)",
  "3L": "var(--band-l3)",
};

export function Ruler({ teams, highlight, onHover, focusLeague, pinned, label }: Props) {
  const router = useRouter();
  const [hover, setHover] = useState<{ slug: string; lane: LeagueCode } | null>(null);
  const tracks = useRef<Partial<Record<LeagueCode, HTMLDivElement | null>>>({});

  const { lo, hi, ticks, lanes } = useMemo(() => {
    const values = teams.map((t) => t.rating);
    const lo = Math.floor((Math.min(...values) - 20) / 100) * 100;
    const hi = Math.ceil((Math.max(...values) + 20) / 100) * 100;
    const ticks: number[] = [];
    for (let v = lo; v <= hi; v += 50) ticks.push(v);
    const lanes = LEAGUES.map((l) => ({
      ...l,
      teams: teams.filter((t) => t.league === l.code).sort((a, b) => a.rating - b.rating),
    }));
    return { lo, hi, ticks, lanes };
  }, [teams]);

  const pct = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const bySlug = useMemo(() => new Map(teams.map((t) => [t.slug, t])), [teams]);

  function nearest(lane: LeagueCode, clientX: number) {
    const el = tracks.current[lane];
    const list = lanes.find((l) => l.code === lane)?.teams ?? [];
    if (!el || list.length === 0) return null;
    const rect = el.getBoundingClientRect();
    const value = lo + ((clientX - rect.left) / rect.width) * (hi - lo);
    let best = list[0];
    for (const t of list) if (Math.abs(t.rating - value) < Math.abs(best.rating - value)) best = t;
    return best;
  }

  function move(lane: LeagueCode, e: React.PointerEvent) {
    const t = nearest(lane, e.clientX);
    if (!t) return;
    setHover({ slug: t.slug, lane });
    onHover?.(t.slug);
  }

  function leave(e: React.PointerEvent) {
    if (e.pointerType !== "mouse") return; // touch keeps the selection until the next tap
    setHover(null);
    onHover?.(null);
  }

  function up(lane: LeagueCode, e: React.PointerEvent) {
    const t = nearest(lane, e.clientX);
    if (t && e.pointerType === "mouse") router.push(`/takim/${t.slug}/`);
  }

  const lit = hover?.slug ?? highlight ?? null;
  const shown = lit ? bySlug.get(lit) : pinned ? bySlug.get(pinned) : undefined;

  return (
    <figure className={styles.figure}>
      <div className={styles.ruler} role="img" aria-label={label}>
        <div className={styles.scale} aria-hidden="true">
          {ticks.map((v) => (
            <span
              key={v}
              className={v % 100 === 0 ? styles.major : styles.minor}
              style={{ left: `${pct(v)}%` }}
            >
              {v % 100 === 0 && (
                <span className={v % 200 === 0 ? styles.tickLabel : `${styles.tickLabel} ${styles.odd}`}>
                  {v}
                </span>
              )}
            </span>
          ))}
        </div>
        <div className={styles.lanes}>
        {lanes.map((lane) => {
          const dim = focusLeague && focusLeague !== lane.code;
          return (
            <div key={lane.code} className={styles.lane} data-dim={dim || undefined} aria-hidden="true">
              <span className={styles.laneLabel}>{lane.name}</span>
              <div
                className={styles.track}
                ref={(el) => {
                  tracks.current[lane.code] = el;
                }}
                onPointerMove={(e) => move(lane.code, e)}
                onPointerDown={(e) => move(lane.code, e)}
                onPointerLeave={leave}
                onPointerUp={(e) => up(lane.code, e)}
              >
                {lane.teams.map((t) => (
                  <span
                    key={t.slug}
                    className={styles.mark}
                    data-lit={t.slug === lit || t.slug === pinned || undefined}
                    style={{ left: `${pct(t.rating)}%`, background: LANE_VAR[lane.code] }}
                  />
                ))}
              </div>
            </div>
          );
        })}
        </div>
        <div className={styles.overlay}>
          {shown && (
            <>
              <span className={styles.guide} style={{ left: `${pct(shown.rating)}%` }} />
              <div
                className={styles.tip}
                style={{ left: `${pct(shown.rating)}%` }}
                data-edge={
                  pct(shown.rating) > 70 ? "end" : pct(shown.rating) < 30 ? "start" : undefined
                }
              >
                <strong>{fmtRating(shown.rating)}</strong>
                <a href={`/takim/${shown.slug}/`} tabIndex={-1}>
                  {shown.name}
                </a>
              </div>
            </>
          )}
        </div>
      </div>
    </figure>
  );
}
