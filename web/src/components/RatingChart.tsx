"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { dateLong, delta, rating } from "@/lib/format";
import type { LeagueCode } from "@/lib/types";

import styles from "./RatingChart.module.css";

export interface ChartPoint {
  t: number; // ms
  date: string;
  r: number; // rating after the event
  d: number; // change
  label: string;
}

export interface ChartBand {
  season: string;
  league: LeagueCode;
  leagueName: string;
  start: number;
  end: number;
}

const BAND_FILL: Record<LeagueCode, string> = {
  SL: "var(--sl)",
  "1L": "var(--l1)",
  "2L": "var(--l2)",
  "3L": "var(--l3)",
};

function niceStep(span: number) {
  return span > 600 ? 200 : span > 300 ? 100 : 50;
}

export function RatingChart({
  points,
  bands,
  summary,
}: {
  points: ChartPoint[];
  bands: ChartBand[];
  summary: string;
}) {
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [hi, setHi] = useState<number | null>(null);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const height = width < 600 ? 220 : 280;
  const m = { l: 44, r: 12, t: 26, b: 28 };
  const iw = Math.max(0, width - m.l - m.r);
  const ih = height - m.t - m.b;

  const geo = useMemo(() => {
    const t0 = Math.min(points[0].t, bands[0]?.start ?? points[0].t);
    const t1 = points[points.length - 1].t;
    const rs = points.map((p) => p.r);
    const step = niceStep(Math.max(...rs) - Math.min(...rs));
    const lo = Math.floor((Math.min(...rs) - 10) / step) * step;
    const hi = Math.ceil((Math.max(...rs) + 10) / step) * step;
    const ticks: number[] = [];
    for (let v = lo; v <= hi; v += step) ticks.push(v);
    return { t0, t1, lo, hi, ticks };
  }, [points, bands]);

  const x = (t: number) => m.l + ((t - geo.t0) / Math.max(1, geo.t1 - geo.t0)) * iw;
  const y = (r: number) => m.t + (1 - (r - geo.lo) / (geo.hi - geo.lo)) * ih;

  // Steps, not slopes: a rating holds between events and jumps at each one (no diagonal
  // across a summer break pretending the change was gradual).
  const path = points
    .map((p, i) =>
      i === 0
        ? `M${x(p.t).toFixed(1)},${y(p.r).toFixed(1)}`
        : `H${x(p.t).toFixed(1)}V${y(p.r).toFixed(1)}`,
    )
    .join("");

  function nearest(clientX: number) {
    const rect = box.current!.getBoundingClientRect();
    const px = clientX - rect.left;
    let best = 0;
    for (let i = 1; i < points.length; i++) {
      if (Math.abs(x(points[i].t) - px) < Math.abs(x(points[best].t) - px)) best = i;
    }
    return best;
  }

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      const step = e.key === "ArrowLeft" ? -1 : 1;
      setHi((h) => Math.min(points.length - 1, Math.max(0, (h ?? points.length - 1) + step)));
    } else if (e.key === "Escape") {
      setHi(null);
    }
  }

  const p = hi != null ? points[hi] : null;
  const px = p ? x(p.t) : 0;
  const shown = p ?? points[points.length - 1]; // the readout rests on the latest change

  return (
    <div>
      {/* Above the plot, never on it: the line under the cursor stays visible. */}
      <p className={styles.readout} aria-live="polite">
        <strong>{rating(shown.r)}</strong>
        <span className={shown.d > 0 ? "gain" : shown.d < 0 ? "loss" : "muted"}>
          {delta(shown.d)}
        </span>
        <span>{shown.label}</span>
        <span className={styles.readDate}>{dateLong(shown.date)}</span>
      </p>
      <div
        ref={box}
        className={styles.chart}
        style={{ height }}
        tabIndex={0}
        role="img"
        aria-label={summary}
        onPointerMove={(e) => setHi(nearest(e.clientX))}
        onPointerDown={(e) => setHi(nearest(e.clientX))}
        onPointerLeave={(e) => e.pointerType === "mouse" && setHi(null)}
        onKeyDown={onKey}
        onBlur={() => setHi(null)}
      >
        {width > 0 && (
          <svg width={width} height={height} aria-hidden="true">
            {bands.map((b) => {
              const bx = x(b.start);
              const bw = Math.max(0, x(b.end) - bx);
              return (
                <g key={b.season}>
                  <rect x={bx} y={m.t} width={bw} height={ih} fill={BAND_FILL[b.league]} opacity={0.09} />
                  <line x1={bx} x2={bx} y1={m.t} y2={m.t + ih} className={styles.season} />
                  {bw > 34 && (
                    <text x={bx + 4} y={m.t - 8} className={styles.bandLabel}>
                      {/* Narrow bands keep the time reference: "21-22". */}
                      {bw > 120 ? `${b.season} ${b.leagueName}` : b.season.slice(2)}
                    </text>
                  )}
                </g>
              );
            })}
            {geo.ticks.map((v) => (
              <g key={v}>
                <line x1={m.l} x2={m.l + iw} y1={y(v)} y2={y(v)} className={styles.grid} />
                <text x={m.l - 8} y={y(v)} dy="0.32em" textAnchor="end" className={styles.tick}>
                  {v}
                </text>
              </g>
            ))}
            <path d={path} className={styles.line} />
            {p && (
              <g>
                <line x1={px} x2={px} y1={m.t} y2={m.t + ih} className={styles.cross} />
                <circle cx={px} cy={y(p.r)} r={4.5} className={styles.dot} />
              </g>
            )}
          </svg>
        )}
      </div>
    </div>
  );
}
