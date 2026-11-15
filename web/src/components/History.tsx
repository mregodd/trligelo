"use client";

import { useEffect, useState } from "react";

import { steps } from "@/lib/calc";
import { dateLong, dateShort, delta, num, rating } from "@/lib/format";
import { ADJUSTMENTS, COMPETITIONS, competitionLabel, groupName, leagueName } from "@/lib/labels";
import type { AdjustmentEvent, MatchEvent, TeamEvent, TeamSeason } from "@/lib/types";

import styles from "./History.module.css";

const SEASON_START = new Set([
  "regression",
  "anchor",
  "promotion",
  "relegation",
  "newcomer",
  "return",
  "champion",
]);

type Item =
  | { kind: "match"; e: MatchEvent }
  | { kind: "bonus"; e: AdjustmentEvent }
  | { kind: "start"; season: string; items: AdjustmentEvent[] };

function seasonItems(events: TeamEvent[], season: string): Item[] {
  const own = events.filter((e) => e.season === season);
  const start = own.filter((e): e is AdjustmentEvent => e.t !== "match" && SEASON_START.has(e.t));
  const rest: Item[] = own
    .filter((e) => e.t === "match" || !SEASON_START.has(e.t))
    .map((e) => (e.t === "match" ? { kind: "match", e } : { kind: "bonus", e: e as AdjustmentEvent }));
  const items = [...rest].reverse(); // newest first
  if (start.length) items.push({ kind: "start", season, items: start });
  return items;
}

interface Props {
  team: string;
  events: TeamEvent[];
  seasons: TeamSeason[];
}

export function History({ team, events, seasons }: Props) {
  // A link like /takim/<club>/#mac-<n> opens that match and its calculation.
  useEffect(() => {
    const openFromHash = () => {
      const id = window.location.hash.slice(1); // ids are plain ASCII ("mac-123"): no decoding
      const el = id.startsWith("mac-") ? document.getElementById(id) : null;
      if (el instanceof HTMLDetailsElement) {
        el.open = true;
        el.scrollIntoView({ block: "start" });
      }
    };
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    return () => window.removeEventListener("hashchange", openFromHash);
  }, []);
  return (
    <div className={styles.history}>
      {[...seasons].reverse().map((s) => {
        const items = seasonItems(events, s.season);
        const matches = items.filter((i) => i.kind === "match").length;
        return (
          <section key={s.season} className={styles.season} aria-labelledby={`season-${s.season}`}>
            <h2 id={`season-${s.season}`}>
              {s.season} sezonu
              <span className={styles.seasonMeta}>
                {leagueName(s.league)}
                {s.group ? `, ${groupName(s.group)}` : ""}, {matches} maç
              </span>
            </h2>
            <div className={styles.head} aria-hidden="true">
              <span>Tarih</span>
              <span>Rakip</span>
              <span className="num">Skor</span>
              <span className="num">Değişim</span>
              <span className="num">Puan</span>
            </div>
            <ol className={styles.list}>
              {items.map((item) =>
                item.kind === "match" ? (
                  <MatchRow key={item.e.seq} team={team} m={item.e} />
                ) : item.kind === "bonus" ? (
                  <BonusRow key={item.e.seq} e={item.e} />
                ) : (
                  <StartRow key={`start-${item.season}`} season={item.season} items={item.items} />
                ),
              )}
            </ol>
          </section>
        );
      })}
    </div>
  );
}

function MatchRow({ team, m }: { team: string; m: MatchEvent }) {
  // The calculation is built when the row is first opened, not shipped in the page.
  const [open, setOpen] = useState(false);
  const venue = m.venue === "a" ? "deplasman" : m.venue === "n" ? "tarafsız saha" : "";
  const comp = COMPETITIONS[m.comp]?.short ?? m.comp;
  const changeClass = m.d > 0 ? "gain" : m.d < 0 ? "loss" : "muted";
  return (
    <li>
      <details
        id={`mac-${m.seq}`}
        className={styles.row}
        onToggle={(e) => setOpen(e.currentTarget.open)}
      >
        <summary>
          <Chevron />
          <span className={styles.date}>
            <time dateTime={m.date}>{dateShort(m.date)}</time>
            <span className={styles.comp}>{comp}</span>
          </span>
          <span className={styles.opp}>
            {m.opp.name}
            {venue && <span className={styles.venue}>{venue}</span>}
          </span>
          <span className={`num ${styles.score}`}>
            {m.gf}-{m.ga}
            {m.pens ? (
              <small>
                {" "}
                pen. {m.pens[0]}-{m.pens[1]}
              </small>
            ) : m.g90 ? (
              <small> uz.</small>
            ) : null}
          </span>
          <span className={`num ${styles.delta} ${changeClass}`}>{delta(m.d)}</span>
          <span className={`num ${styles.after}`}>{rating(m.ra)}</span>
        </summary>
        {open && (
          <div className={styles.calc}>
            <p className={styles.calcTitle}>
              {dateLong(m.date)}, {competitionLabel(m.comp, m.round)}
            </p>
            <p className={styles.calcLinks}>
              {m.opp.slug && <a href={`/takim/${m.opp.slug}/`}>{m.opp.name} puan sayfası</a>}
              <a href={`#mac-${m.seq}`} className={styles.permalink}>
                Bu hesabın bağlantısı
              </a>
            </p>
            <dl>
              {steps(team, m).map((s) => (
                <div key={s.label}>
                  <dt>{s.label}</dt>
                  <dd>{s.text}</dd>
                </div>
              ))}
            </dl>
          </div>
        )}
      </details>
    </li>
  );
}

/** Drawn disclosure mark; turns a quarter when the row opens. */
function Chevron() {
  return (
    <svg className={styles.chev} viewBox="0 0 12 12" aria-hidden="true">
      <path
        d="M4.5 2.5 8 6l-3.5 3.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function BonusRow({ e }: { e: AdjustmentEvent }) {
  const a = ADJUSTMENTS[e.t];
  return (
    <li className={styles.adjust}>
      <span className={styles.date}>{e.date ? dateShort(e.date) : ""}</span>
      <span className={styles.opp}>
        {a.name}
        <span className={styles.why}>{a.why}</span>
      </span>
      <span className={styles.blank} />
      <span className={`num ${styles.delta} gain`}>{delta(e.d)}</span>
      <span className={`num ${styles.after}`}>{rating(e.ra)}</span>
    </li>
  );
}

function StartRow({ season, items }: { season: string; items: AdjustmentEvent[] }) {
  const total = items.reduce((a, b) => a + b.d, 0);
  const last = items[items.length - 1];
  return (
    <li>
      <details className={`${styles.row} ${styles.startRow}`}>
        <summary>
          <Chevron />
          <span className={styles.date}>Sezon başı</span>
          <span className={styles.opp}>{season} öncesi ayarlar</span>
          <span className={styles.blank} />
          <span className={`num ${styles.delta} ${total > 0 ? "gain" : total < 0 ? "loss" : "muted"}`}>
            {delta(total)}
          </span>
          <span className={`num ${styles.after}`}>{rating(last.ra)}</span>
        </summary>
        <div className={styles.calc}>
          <dl>
            {items.map((e) => (
              <div key={e.seq}>
                <dt>{ADJUSTMENTS[e.t].name}</dt>
                <dd>
                  {e.t === "newcomer" ? `Başlangıç puanı ${num(e.ra, 1)}.` : `${delta(e.d)}.`}{" "}
                  {ADJUSTMENTS[e.t].why}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </details>
    </li>
  );
}
