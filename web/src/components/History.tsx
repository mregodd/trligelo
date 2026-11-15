"use client";

import { useEffect, useState } from "react";

import { explain, regressionText } from "@/lib/calc";
import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { adjustments, competitionLabel, competitionShort, groupName, leagueName } from "@/lib/labels";
import type { AdjustmentEvent, MatchEvent, TeamEvent, TeamSeason } from "@/lib/types";
import { msg } from "@/messages";

import { ClubLogo } from "./ClubLogo";
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
  lang: Lang;
  team: string;
  events: TeamEvent[];
  seasons: TeamSeason[];
}

export function History({ lang, team, events, seasons }: Props) {
  const t = msg(lang).history;
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
              {t.season(s.season)}
              <span className={styles.seasonMeta}>
                {leagueName(s.league)}
                {s.group ? `, ${groupName(s.group, lang)}` : ""}, {t.matches(matches)}
              </span>
            </h2>
            <div className={styles.head} aria-hidden="true">
              <span>{t.head[0]}</span>
              <span>{t.head[1]}</span>
              <span className="num">{t.head[2]}</span>
              <span className="num">{t.head[3]}</span>
              <span className="num">{t.head[4]}</span>
            </div>
            <ol className={styles.list}>
              {items.map((item) =>
                item.kind === "match" ? (
                  <MatchRow key={item.e.seq} lang={lang} team={team} m={item.e} />
                ) : item.kind === "bonus" ? (
                  <BonusRow key={item.e.seq} lang={lang} e={item.e} />
                ) : (
                  <StartRow key={`start-${item.season}`} lang={lang} season={item.season} items={item.items} />
                ),
              )}
            </ol>
          </section>
        );
      })}
    </div>
  );
}

function MatchRow({ lang, team, m }: { lang: Lang; team: string; m: MatchEvent }) {
  // The calculation is built when the row is first opened, not shipped in the page.
  const [open, setOpen] = useState(false);
  const t = msg(lang).history;
  const f = fmt(lang);
  const venue = m.venue === "a" ? t.away : m.venue === "n" ? t.neutral : "";
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
            <time dateTime={m.date}>{f.dateShort(m.date)}</time>
            <span className={styles.comp}>{competitionShort(m.comp, lang)}</span>
          </span>
          <span className={styles.opp}>
            <ClubLogo src={m.opp.logo ?? null} size={16} keepSpace /> {m.opp.name}
            {venue && <span className={styles.venue}>{venue}</span>}
          </span>
          <span className={`num ${styles.score}`}>
            {m.gf}-{m.ga}
            {m.pens ? (
              <small>
                {" "}
                {t.pens} {m.pens[0]}-{m.pens[1]}
              </small>
            ) : m.g90 ? (
              <small> {t.et}</small>
            ) : null}
          </span>
          <span className={`num ${styles.delta} ${changeClass}`}>{f.delta(m.d)}</span>
          <span className={`num ${styles.after}`}>{f.rating(m.ra)}</span>
        </summary>
        {open && (
          <div className={styles.calc}>
            <p className={styles.calcTitle}>
              {f.dateLong(m.date)}, {competitionLabel(m.comp, m.round, lang)}
            </p>
            <p className={styles.calcLinks}>
              {m.opp.slug && <a href={href(lang, `/takim/${m.opp.slug}/`)}>{t.oppPage(m.opp.name)}</a>}
              <a href={href(lang, `/metodoloji/${t.formulaAnchor}`)}>{t.formula}</a>
              <a href={`#mac-${m.seq}`} className={styles.permalink}>
                {t.permalink}
              </a>
            </p>
            <div className={styles.explain}>
              {explain(team, m, lang).map((text) => (
                <p key={text}>{text}</p>
              ))}
            </div>
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

function BonusRow({ lang, e }: { lang: Lang; e: AdjustmentEvent }) {
  const a = adjustments(lang)[e.t];
  const f = fmt(lang);
  return (
    <li className={styles.adjust}>
      <span className={styles.date}>{e.date ? f.dateShort(e.date) : ""}</span>
      <span className={styles.opp}>
        {a.name}
        <span className={styles.why}>{a.why}</span>
      </span>
      <span className={styles.blank} />
      <span className={`num ${styles.delta} gain`}>{f.delta(e.d)}</span>
      <span className={`num ${styles.after}`}>{f.rating(e.ra)}</span>
    </li>
  );
}

function StartRow({ lang, season, items }: { lang: Lang; season: string; items: AdjustmentEvent[] }) {
  const t = msg(lang).history;
  const f = fmt(lang);
  const adj = adjustments(lang);
  const total = items.reduce((a, b) => a + b.d, 0);
  const last = items[items.length - 1];
  return (
    <li>
      <details className={`${styles.row} ${styles.startRow}`}>
        <summary>
          <Chevron />
          <span className={styles.date}>{t.start}</span>
          <span className={styles.opp}>{t.startRow(season)}</span>
          <span className={styles.blank} />
          <span className={`num ${styles.delta} ${total > 0 ? "gain" : total < 0 ? "loss" : "muted"}`}>
            {f.delta(total)}
          </span>
          <span className={`num ${styles.after}`}>{f.rating(last.ra)}</span>
        </summary>
        <div className={styles.calc}>
          <dl>
            {items.map((e) => (
              <div key={e.seq}>
                <dt>{adj[e.t].name}</dt>
                <dd>
                  {e.t === "regression"
                    ? regressionText(e.d, lang)
                    : `${e.t === "newcomer" ? t.newcomer(f.num(e.ra, 1)) : `${f.delta(e.d)}.`} ${adj[e.t].why}`}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </details>
    </li>
  );
}
