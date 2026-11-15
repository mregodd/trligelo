import { ClubLogo } from "@/components/ClubLogo";
import { dateShort, delta, rating } from "@/lib/format";
import { leagueName } from "@/lib/labels";
import type { Meta, TeamSummary } from "@/lib/types";

import styles from "./Movers.module.css";

/** The week's biggest gains and losses (last 7 days up to the latest match). */
export function Movers({ teams, meta }: { teams: TeamSummary[]; meta: Meta }) {
  const moved = teams.filter((t) => t.active && t.week !== 0);
  const up = [...moved].sort((a, b) => b.week - a.week).slice(0, 5).filter((t) => t.week > 0);
  const down = [...moved].sort((a, b) => a.week - b.week).slice(0, 5).filter((t) => t.week < 0);
  return (
    <section className={styles.movers} aria-labelledby="movers-title">
      <h2 id="movers-title">Bu hafta</h2>
      <p className={styles.range}>
        {dateShort(meta.weekFrom)} – {dateShort(meta.lastMatch)} arasındaki maçlar
      </p>
      <div className={styles.cols}>
        <List title="En çok kazananlar" teams={up} />
        <List title="En çok kaybedenler" teams={down} />
      </div>
    </section>
  );
}

function List({ title, teams }: { title: string; teams: TeamSummary[] }) {
  return (
    <div>
      <h3>{title}</h3>
      {teams.length === 0 ? (
        <p className={styles.none}>Bu hafta değişim yok.</p>
      ) : (
        <ol className={styles.list}>
          {teams.map((t) => (
            <li key={t.slug}>
              <a href={`/takim/${t.slug}/`}>
                <ClubLogo src={t.logo} size={16} keepSpace /> {t.name}
              </a>
              <span className={`num ${t.week > 0 ? "gain" : "loss"}`}>{delta(t.week)}</span>
              <span className={styles.meta}>
                {leagueName(t.league)}, {rating(t.rating)}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
