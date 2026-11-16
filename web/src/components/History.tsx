"use client";

import { Fragment, useEffect, useId, useMemo, useState } from "react";

import { chances, closedDoors, model, regressionText, stakes } from "@/lib/calc";
import { fmt, result, type Result } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import {
  adjustments,
  competitionLabel,
  competitionName,
  competitionShort,
  groupName,
  leagueName,
} from "@/lib/labels";
import { type Streak, streaks } from "@/lib/streaks";
import type { AdjustmentEvent, MatchEvent, TeamEvent, TeamSeason } from "@/lib/types";
import { msg } from "@/messages";

import { ClubLogo } from "./ClubLogo";
import styles from "./History.module.css";

const RESULTS = ["G", "B", "M"] as const;

/** Home, away and neutral ground, drawn on a 16-unit grid. */
const VENUE_ICONS = {
  h: (
    <path
      d="M2.75 7.25 8 3l5.25 4.25M4.25 6.25v6.5h2.5v-3h2.5v3h2.5v-6.5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  ),
  a: (
    <path
      d="M7.3 2.6a.7.7 0 0 1 1.4 0v3.9l5.3 3.1v1.2L8.7 9.3v3l1.6 1.1v.9L8 13.7l-2.3.6v-.9l1.6-1.1v-3L2 10.8V9.6l5.3-3.1z"
      fill="currentColor"
    />
  ),
  n: (
    <g fill="none" stroke="currentColor" strokeWidth="1.3">
      <rect x="1.75" y="3.75" width="12.5" height="8.5" rx="1" />
      <path d="M8 3.75v8.5" />
      <circle cx="8" cy="8" r="1.8" />
    </g>
  ),
};

/** A message with {placeholders} filled in by text or elements (a link, a bold number). */
function fill(template: string, values: Record<string, React.ReactNode>) {
  return template
    .split(/\{(\w+)\}/)
    .map((part, i) => <Fragment key={i}>{i % 2 ? values[part] : part}</Fragment>);
}

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
  const runs = useMemo(() => streaks(events), [events]);
  // A link like /club/<club>/#match-<n> opens that match and its calculation.
  useEffect(() => {
    const openFromHash = () => {
      const id = window.location.hash.slice(1); // ids are plain ASCII ("match-123"): no decoding
      const el = id.startsWith("match-") ? document.getElementById(id) : null;
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
                  <MatchRow
                    key={item.e.seq}
                    lang={lang}
                    team={team}
                    m={item.e}
                    streak={runs.get(item.e.seq)}
                  />
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

interface RowProps {
  lang: Lang;
  team: string;
  m: MatchEvent;
  streak?: Streak;
}

function MatchRow({ lang, team, m, streak }: RowProps) {
  // The calculation is built when the row is first opened, not shipped in the page.
  const [open, setOpen] = useState(false);
  const t = msg(lang).history;
  const f = fmt(lang);
  const changeClass = m.d > 0 ? "gain" : m.d < 0 ? "loss" : "muted";
  return (
    <li>
      <details
        id={`match-${m.seq}`}
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
            <Venue lang={lang} venue={m.venue} />
            <span className={styles.mark}>
              {m.opp.country ? (
                <span className={styles.country}>{m.opp.country}</span>
              ) : (
                <ClubLogo src={m.opp.logo ?? null} size={16} keepSpace />
              )}
            </span>
            {m.opp.name}
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
        {open && <MatchCalc lang={lang} team={team} m={m} streak={streak} />}
      </details>
    </li>
  );
}

/** Home, away or neutral ground as an icon; its name is there for screen readers. */
function Venue({ lang, venue }: { lang: Lang; venue: MatchEvent["venue"] }) {
  const t = msg(lang).history;
  const label = venue === "h" ? t.home : venue === "a" ? t.away : t.neutral;
  return (
    <span className={styles.venue} title={label}>
      <svg viewBox="0 0 16 16" aria-hidden="true">
        {VENUE_ICONS[venue]}
      </svg>
      <span className="visually-hidden">{label}, </span>
    </span>
  );
}

/**
 * One match told in plain words, top to bottom: the ratings before it, what home advantage
 * did, the chances with what each result was worth, then the result and what it meant.
 */
function MatchCalc({ lang, team, m, streak }: RowProps) {
  const t = msg(lang).explain;
  const f = fmt(lang);
  const pct = msg(lang).fixture.pct;
  const c = chances(m);
  const r = result(m.s);
  const fav = m.e >= 0.55 ? 1 : m.e <= 0.45 ? -1 : 0; // favourite, underdog, or even
  const had = r === "G" ? c.win : r === "M" ? c.loss : c.draw; // the result's chance before
  const opp = m.opp.slug ? <a href={href(lang, `/club/${m.opp.slug}/`)}>{m.opp.name}</a> : m.opp.name;
  let score = `${m.gf}-${m.ga}`;
  if (m.g90) score += t.extraTime(m.g90[0], m.g90[1]);
  if (m.pens) score += t.shootout(m.pens[0], m.pens[1]);
  const weight = m.opp.kind === "amateur" ? t.amateurWeight(f.factor(m.w))
    : t.weight(competitionName(m.comp, lang), f.factor(m.w)); // fmt: skip
  const notes = [
    m.g > 1 && t.margin(Math.abs(m.gf - m.ga), f.factor(m.g)),
    m.w !== 1 && weight,
    m.k !== model.k && t.provisional(model.provisionalGames, f.factor(model.provisionalFactor)),
  ].filter(Boolean);
  return (
    <div className={styles.calc}>
      <p className={styles.calcTitle}>
        {f.dateLong(m.date)}, {competitionLabel(m.comp, m.round, lang)}
      </p>
      <p>
        {fill(t.before, {
          team,
          opp,
          r: <strong>{f.num(m.r, 0)}</strong>,
          ro: <strong>{f.num(m.ro, 0)}</strong>,
        })}
        {m.opp.kind === "foreign" && t.foreign}
        {m.opp.kind === "amateur" && t.amateur}
      </p>
      <p className={styles.withHint}>
        {m.venue === "n"
          ? t.neutral
          : fill(m.venue === "h" ? t.hostTeam : t.hostOpp, {
              team,
              opp,
              with: pct(c.win),
              without: pct(c.neutralWin),
              q: <Hint label={t.neutralLabel} text={t.neutralHint} />,
            })}
        {closedDoors(m) && t.closed}
      </p>
      <Odds lang={lang} shares={[c.win, c.draw, c.loss]} worth={stakes(m)} actual={r} />
      <p className={styles.result}>{t.result(score, msg(lang).result.word[r], f.delta(m.d))}</p>
      <p>
        {t.why[r][fav + 1]}.{r !== "B" && had > 0 && had <= 30 && t.surprise(had, Math.round(100 / had))}
        {streak && ` ${t.streak[streak.kind](streak.n)}`}
        {m.pens && t.pens}
      </p>
      {notes.length > 0 && <p className={styles.notes}>{notes.join(" ")}</p>}
    </div>
  );
}

/** A "?" after a term: its meaning shows above the sentence on hover, keyboard focus or tap. */
function Hint({ label, text }: { label: string; text: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <span className={styles.hint} data-open={open || undefined}>
      <button
        type="button"
        aria-label={label}
        aria-describedby={id}
        onClick={() => setOpen(!open)}
        onBlur={() => setOpen(false)}
      >
        ?
      </button>
      <span id={id} role="tooltip" className={styles.tip}>
        {text}
      </span>
    </span>
  );
}

/** Win, draw and loss chances as one bar, each with what that result by one goal was worth. */
function Odds({ lang, shares, worth, actual }: { lang: Lang; shares: number[]; worth: number[]; actual: Result }) {
  const m = msg(lang);
  const f = fmt(lang);
  return (
    <div className={styles.odds}>
      <p className={styles.oddsTitle}>{m.explain.chances}</p>
      <div className={styles.bar} aria-hidden="true">
        {RESULTS.map((r, i) => (
          <span key={r} data-r={r} style={{ width: `${shares[i]}%` }} />
        ))}
      </div>
      <ul className={styles.outcomes}>
        {RESULTS.map((r, i) => (
          <li key={r} data-actual={r === actual || undefined}>
            <span className={styles.chip} data-r={r} aria-hidden="true">
              {m.result.letter[r]}
            </span>
            <span className="visually-hidden">{m.result.word[r]}:</span>
            {m.fixture.pct(shares[i])}
            <span>{f.delta(worth[i])}</span>
          </li>
        ))}
      </ul>
      <p className={styles.oddsNote}>{m.explain.chancesNote}</p>
    </div>
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
