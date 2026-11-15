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
          <h1>Türkiye'nin profesyonel kulüpleri, tek cetvelde</h1>
          <p>
            Elo, maç sonuçlarından hesaplanan bir güç puanı: her maçtan sonra iki takım arasında
            puan el değiştirir, beklenmeyen sonuç daha çok puan taşır. Süper Lig'den 3. Lig'e{" "}
            {meta.activeTeams} kulüp aynı ölçekte; Avrupa kupalarındaki maçlar da sayılır,
            yabancı rakiplerin gücü UEFA katsayısından gelir.
          </p>
          <p>
            Puanlar {dateLong(meta.lastMatch)} maçlarına kadar güncel.{" "}
            <a href="/metodoloji/">Puanlar nasıl hesaplanıyor?</a>
          </p>
        </div>
      }
      aside={<Movers teams={teams} meta={meta} />}
    />
  );
}
