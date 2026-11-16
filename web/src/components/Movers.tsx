import { ClubLogo } from "@/components/ClubLogo";
import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { leagueName } from "@/lib/labels";
import type { Meta, TeamSummary } from "@/lib/types";
import { msg } from "@/messages";

import styles from "./Movers.module.css";

/** The week's biggest gains and losses (last 7 days up to the latest match). */
export function Movers({ teams, meta, lang }: { teams: TeamSummary[]; meta: Meta; lang: Lang }) {
  const t = msg(lang).movers;
  const f = fmt(lang);
  const moved = teams.filter((t) => t.active && t.week !== 0);
  const up = [...moved].sort((a, b) => b.week - a.week).slice(0, 5).filter((t) => t.week > 0);
  const down = [...moved].sort((a, b) => a.week - b.week).slice(0, 5).filter((t) => t.week < 0);
  return (
    <section className={styles.movers} aria-labelledby="movers-title">
      <h2 id="movers-title">{t.title}</h2>
      <p className={styles.range}>
        {t.range(f.dateShort(meta.weekFrom), f.dateShort(meta.lastMatch))}
      </p>
      <div className={styles.cols}>
        <List title={t.up} teams={up} lang={lang} />
        <List title={t.down} teams={down} lang={lang} />
      </div>
    </section>
  );
}

function List({ title, teams, lang }: { title: string; teams: TeamSummary[]; lang: Lang }) {
  const f = fmt(lang);
  return (
    <div>
      <h3>{title}</h3>
      {teams.length === 0 ? (
        <p className={styles.none}>{msg(lang).movers.none}</p>
      ) : (
        <ol className={styles.list}>
          {teams.map((c) => (
            <li key={c.slug}>
              <a href={href(lang, `/club/${c.slug}/`)}>
                <ClubLogo src={c.logo} size={16} keepSpace /> {c.name}
              </a>
              <span className={`num ${c.week > 0 ? "gain" : "loss"}`}>{f.delta(c.week)}</span>
              <span className={styles.meta}>
                {leagueName(c.league)}, {f.rating(c.rating)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
