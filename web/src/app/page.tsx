import { Movers } from "@/components/Movers";
import { Standings } from "@/components/Standings";
import { getMeta, getTeams } from "@/lib/data";
import { dateLong, rating } from "@/lib/format";
import { LEAGUES } from "@/lib/labels";

import styles from "./page.module.css";

export default function Home() {
  const meta = getMeta();
  const teams = getTeams();
  const active = teams.filter((t) => t.active);

  // Spoken summary of the ruler for screen readers (the table below carries every value).
  const ranges = LEAGUES.map((l) => {
    const r = active.filter((t) => t.league === l.code).map((t) => t.rating);
    return `${l.name} ${rating(Math.min(...r))}–${rating(Math.max(...r))}`;
  }).join("; ");

  return (
    <Standings
      teams={teams}
      rulerLabel={`Bütün kulüplerin puanları tek ölçekte. Puan aralıkları: ${ranges}.`}
      heading={
        <div className={styles.heading}>
          <h1>Bütün profesyonel kulüpler, tek cetvelde</h1>
          <p>
            Süper Lig'den 3. Lig'e {meta.activeTeams} kulüp aynı Elo ölçeğinde. Puanlar{" "}
            {dateLong(meta.lastMatch)} maçlarına kadar güncel.
          </p>
        </div>
      }
      aside={<Movers teams={teams} meta={meta} />}
    />
  );
}
