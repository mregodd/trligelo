import type { Metadata } from "next";

import { FixtureList } from "@/components/FixtureCard";
import { getFixtures, getMeta } from "@/lib/data";
import { dateLong } from "@/lib/format";
import { groupName, leagueName, leagueSlug } from "@/lib/labels";

import styles from "./page.module.css";

export const metadata: Metadata = {
  title: "Yaklaşan maçlar",
  description:
    "Her ligin sıradaki haftası ve kupa maçları: Elo puanlarına göre şanslar ve her sonucun puana etkisi.",
};

export default function FixturesPage() {
  const { rounds, cup } = getFixtures();
  const meta = getMeta();
  const sections = rounds.map((r) => ({
    id: `${leagueSlug(r.league)}${r.group ? `-${r.group.toLocaleLowerCase("tr-TR")}` : ""}`,
    title: `${leagueName(r.league)}${r.group ? `, ${groupName(r.group)}` : ""}`,
    ...r,
  }));
  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <h1>Yaklaşan maçlar</h1>
          <p className={styles.lead}>
            Her ligin sıradaki haftası ve tarihi açıklanmış kupa maçları. Şanslar ve puan değişimleri{" "}
            {dateLong(meta.lastMatch)} maçlarından sonraki puanlarla hesaplanır; değişimler bir farklı
            sonuç içindir, fark büyüdükçe artar. Tarihler TFF açıkladıkça eklenir.
          </p>
          <ul className={styles.jump} aria-label="Bölümler">
            {sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`}>{s.title}</a>
              </li>
            ))}
            {cup.length > 0 && (
              <li>
                <a href="#kupa">Kupa</a>
              </li>
            )}
          </ul>
        </div>
      </section>

      <div className="wrap">
        {sections.map((s) => (
          <section key={s.id} id={s.id} className={styles.round}>
            <h2>
              {s.title}, {s.week}. hafta
            </h2>
            {s.matches.every((m) => !m.date) && <p className={styles.note}>Tarihler henüz açıklanmadı.</p>}
            <FixtureList fixtures={s.matches} />
          </section>
        ))}
        {cup.length > 0 && (
          <section id="kupa" className={styles.round}>
            <h2>Ziraat Türkiye Kupası</h2>
            <FixtureList fixtures={cup} withCompetition />
          </section>
        )}
      </div>
    </>
  );
}
