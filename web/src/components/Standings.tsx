"use client";

import { useMemo, useState } from "react";

import { delta, rating } from "@/lib/format";
import { groupName, LEAGUES, leagueName } from "@/lib/labels";
import type { LeagueCode, TeamSummary } from "@/lib/types";

import { Form } from "./Form";
import { LeagueKey } from "./LeagueKey";
import { Ruler } from "./Ruler";
import styles from "./Standings.module.css";

interface Props {
  teams: TeamSummary[];
  rulerLabel: string;
  aside: React.ReactNode;
  heading: React.ReactNode;
}

type Filter = "all" | LeagueCode;

const trLower = (s: string) => s.toLocaleLowerCase("tr-TR");

export function Standings({ teams, rulerLabel, aside, heading }: Props) {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [lit, setLit] = useState<string | null>(null);

  const active = useMemo(() => teams.filter((t) => t.active), [teams]);
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
          />
        </div>
      </section>

      <div className={`wrap ${styles.layout}`}>
        <div className={styles.main}>
          <div className={styles.controls}>
            <div className={styles.tabs} role="group" aria-label="Lige göre süz">
              {[{ code: "all" as Filter, name: "Tümü" }, ...LEAGUES].map((l) => (
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
              <span className="visually-hidden">Kulüp ara</span>
              <input
                type="search"
                placeholder="Kulüp ara"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
          </div>

          <table className={styles.table}>
            <caption className="visually-hidden">
              Elo puanına göre sıralama{filter !== "all" ? `, ${leagueName(filter)}` : ""}
            </caption>
            <thead>
              <tr>
                <th scope="col" className="num">
                  Sıra
                </th>
                <th scope="col">Kulüp</th>
                <th scope="col" className={styles.wideOnly}>
                  Lig
                </th>
                <th scope="col" className="num">
                  Puan
                </th>
                <th scope="col" className="num" title="Son 7 gündeki değişim">
                  7 gün
                </th>
                <th scope="col" className={styles.formCol}>
                  Son 5 maç
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t) => (
                <tr
                  key={t.slug}
                  data-lit={t.slug === lit || undefined}
                  data-inactive={!t.active || undefined}
                  onPointerEnter={() => setLit(t.slug)}
                  onPointerLeave={() => setLit(null)}
                  onFocus={() => setLit(t.slug)}
                  onBlur={() => setLit(null)}
                >
                  <td className="num">{t.rank ?? "–"}</td>
                  <th scope="row" className={styles.club}>
                    <a href={`/takim/${t.slug}/`}>{t.name}</a>
                    <span className={styles.sub}>
                      <LeagueKey code={t.league} />
                      {t.active
                        ? leagueName(t.league)
                        : t.withdrawn
                          ? `${t.lastSeason}'de ${leagueName(t.league)}'den çekildi`
                          : `${t.lastSeason} sezonunda ${leagueName(t.league)}`}
                    </span>
                  </th>
                  <td className={styles.wideOnly}>
                    <LeagueKey code={t.league} />
                    {leagueName(t.league)}
                    {t.group ? <span className="muted">, {groupName(t.group)}</span> : null}
                  </td>
                  <td className={`num ${styles.rating}`}>{rating(t.rating)}</td>
                  <td className={`num ${t.week > 0 ? "gain" : t.week < 0 ? "loss" : "muted"}`}>
                    {t.active ? delta(t.week) : ""}
                  </td>
                  <td className={styles.formCol}>
                    <Form form={t.form} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {rows.length === 0 && (
            <p className={styles.empty}>
              “{query}” ile eşleşen kulüp yok.{" "}
              <button type="button" onClick={() => setQuery("")}>
                Aramayı temizle
              </button>
            </p>
          )}

          <label className={styles.toggle}>
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
            />
            2021-22'den beri profesyonel ligden ayrılan kulüpleri de göster
          </label>
        </div>
        <aside className={styles.aside}>{aside}</aside>
      </div>
    </>
  );
}

