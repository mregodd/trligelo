"use client";

import { useMemo, useState } from "react";

import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { groupName, LEAGUES, leagueName } from "@/lib/labels";
import type { LeagueCode, TeamSummary } from "@/lib/types";
import { msg } from "@/messages";

import { ClubLogo } from "./ClubLogo";
import { Form } from "./Form";
import { LeagueKey } from "./LeagueKey";
import { Ruler } from "./Ruler";
import styles from "./Standings.module.css";

interface Props {
  lang: Lang;
  teams: TeamSummary[];
  rulerLabel: string;
  aside: React.ReactNode;
  heading: React.ReactNode;
}

type Filter = "all" | LeagueCode;

const trLower = (s: string) => s.toLocaleLowerCase("tr-TR"); // club names are Turkish in both languages

export function Standings({ lang, teams, rulerLabel, aside, heading }: Props) {
  const t = msg(lang).standings;
  const f = fmt(lang);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [lit, setLit] = useState<string | null>(null);

  const active = useMemo(() => teams.filter((t) => t.active), [teams]);
  // The toggle only where it adds rows: departed clubs nearly all left from the 3. Lig.
  const hasInactive = teams.some((t) => !t.active && (filter === "all" || t.league === filter));
  const rows = useMemo(() => {
    const q = trLower(query.trim());
    return teams
      .filter((t) => showInactive || t.active)
      .filter((t) => filter === "all" || t.league === filter)
      .filter((t) => !q || trLower(t.name).includes(q) || trLower(t.official).includes(q))
      .sort((a, b) => b.rating - a.rating);
  }, [teams, filter, query, showInactive]);

  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          {heading}
          <Ruler
            teams={active}
            highlight={lit}
            onHover={setLit}
            focusLeague={filter === "all" ? undefined : filter}
            label={rulerLabel}
            lang={lang}
          />
        </div>
      </section>

      <div className={`wrap ${styles.layout}`}>
        <div className={styles.main}>
          <div className={styles.controls}>
            <div className={styles.tabs} role="group" aria-label={t.filter}>
              {[{ code: "all" as Filter, name: t.all }, ...LEAGUES].map((l) => (
                <button
                  key={l.code}
                  type="button"
                  aria-pressed={filter === l.code}
                  onClick={() => setFilter(l.code)}
                >
                  {l.name}
                </button>
              ))}
            </div>
            <label className={styles.search}>
              <span className="visually-hidden">{t.search}</span>
              <input
                type="search"
                placeholder={t.search}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
          </div>

          <table className={styles.table}>
            <caption className="visually-hidden">
              {t.caption}{filter !== "all" ? `, ${leagueName(filter)}` : ""}
            </caption>
            <thead>
              <tr>
                <th scope="col" className="num">
                  {t.rank}
                </th>
                <th scope="col">{t.club}</th>
                <th scope="col" className={styles.wideOnly}>
                  {t.league}
                </th>
                <th scope="col" className="num">
                  {t.rating}
                </th>
                <th scope="col" className="num" title={t.weekTitle}>
                  {t.week}
                </th>
                <th scope="col" className={styles.formCol}>
                  {t.form}
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr
                  key={c.slug}
                  data-league={c.active ? c.league : undefined}
                  data-lit={c.slug === lit || undefined}
                  data-inactive={!c.active || undefined}
                  onPointerEnter={() => setLit(c.slug)}
                  onPointerLeave={() => setLit(null)}
                  onFocus={() => setLit(c.slug)}
                  onBlur={() => setLit(null)}
                >
                  <td className="num">{c.rank ?? "–"}</td>
                  <th scope="row" className={styles.club}>
                    <ClubLogo src={c.logo} keepSpace />
                    <a href={href(lang, `/takim/${c.slug}/`)}>{c.name}</a>
                    <span className={styles.sub}>
                      <LeagueKey code={c.league} />
                      {c.active
                        ? leagueName(c.league)
                        : c.withdrawn
                          ? t.withdrew(c.lastSeason, leagueName(c.league))
                          : t.left(c.lastSeason, leagueName(c.league))}
                    </span>
                  </th>
                  <td className={styles.wideOnly}>
                    <LeagueKey code={c.league} />
                    {leagueName(c.league)}
                    {c.group ? <span className="muted">, {groupName(c.group, lang)}</span> : null}
                  </td>
                  <td className={`num ${styles.rating}`}>{f.rating(c.rating)}</td>
                  <td className={`num ${c.week > 0 ? "gain" : c.week < 0 ? "loss" : "muted"}`}>
                    {c.active ? f.delta(c.week) : ""}
                  </td>
                  <td className={styles.formCol}>
                    <Form form={c.form} lang={lang} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {rows.length === 0 && (
            <p className={styles.empty}>
              {t.none(query)}{" "}
              <button type="button" onClick={() => setQuery("")}>
                {t.clear}
              </button>
            </p>
          )}

          {hasInactive && (
            <label className={styles.toggle}>
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
              />
              {t.inactive}
            </label>
          )}
        </div>
        <aside className={styles.aside}>{aside}</aside>
      </div>
    </>
  );
}

