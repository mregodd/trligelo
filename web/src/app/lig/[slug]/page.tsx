import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Form } from "@/components/Form";
import { Ruler } from "@/components/Ruler";
import { getLeagues, getMeta, getTeamMap, getTeams } from "@/lib/data";
import { dateLong, delta, rating } from "@/lib/format";
import { groupName, LEAGUES } from "@/lib/labels";

import table from "@/components/Standings.module.css";
import styles from "./page.module.css";

export function generateStaticParams() {
  return LEAGUES.map((l) => ({ slug: l.slug }));
}

type Params = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { slug } = await params;
  const league = LEAGUES.find((l) => l.slug === slug);
  return { title: league ? `${league.name} Elo sıralaması` : "Lig" };
}

export default async function LeaguePage({ params }: Params) {
  const { slug } = await params;
  const league = LEAGUES.find((l) => l.slug === slug);
  if (!league) notFound();

  const meta = getMeta();
  const teams = getTeamMap();
  const active = getTeams()
    .filter((t) => t.active)
    .map(({ slug, name, league, rating, leagueRank }) => ({ slug, name, league, rating, leagueRank }));
  const groups = getLeagues().find((l) => l.code === league.code)?.groups ?? [];
  const members = groups.flatMap((g) => g.teams.map((s) => teams.get(s)!));
  const ratings = members.map((t) => t.rating);
  const mean = ratings.reduce((a, b) => a + b, 0) / ratings.length;

  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <h1>{league.name}</h1>
          <p className={styles.lead}>
            {members.length} kulüp, puanlar {rating(Math.min(...ratings))} ile{" "}
            {rating(Math.max(...ratings))} arasında, ortalama {rating(mean)}. Diğer liglerin
            kulüpleri aynı cetvelde soluk gösteriliyor. {dateLong(meta.lastMatch)} maçlarına kadar
            güncel.
          </p>
          <Ruler
            teams={active}
            focusLeague={league.code}
            label={`${league.name} kulüplerinin puanları bütün liglerle aynı ölçekte.`}
          />
        </div>
      </section>

      <div className="wrap">
        {groups.map((group) => (
          <section key={group.name ?? "all"} className={styles.group}>
            {group.name && <h2>{groupName(group.name)}</h2>}
            <table className={table.table}>
              <caption className="visually-hidden">
                {league.name}
                {group.name ? `, ${groupName(group.name)}` : ""}: Elo sıralaması
              </caption>
              <thead>
                <tr>
                  <th scope="col" className="num">
                    Sıra
                  </th>
                  <th scope="col">Kulüp</th>
                  <th scope="col" className="num">
                    Puan
                  </th>
                  <th scope="col" className="num" title="Son 7 gündeki değişim">
                    7 gün
                  </th>
                  <th scope="col" className={table.formCol}>
                    Son 5 maç
                  </th>
                  <th scope="col" className={`num ${table.wideOnly}`}>
                    Genel sıra
                  </th>
                </tr>
              </thead>
              <tbody>
                {group.teams.map((s, i) => {
                  const t = teams.get(s)!;
                  return (
                    <tr key={s}>
                      <td className="num">{i + 1}</td>
                      <th scope="row" className={table.club}>
                        <a href={`/takim/${s}/`}>{t.name}</a>
                      </th>
                      <td className={`num ${table.rating}`}>{rating(t.rating)}</td>
                      <td className={`num ${t.week > 0 ? "gain" : t.week < 0 ? "loss" : "muted"}`}>
                        {delta(t.week)}
                      </td>
                      <td className={table.formCol}>
                        <Form form={t.form} />
                      </td>
                      <td className={`num muted ${table.wideOnly}`}>{t.rank}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>
        ))}
        <p className={styles.note}>
          Bu tablo Elo puanına göre sıralanır, resmi puan durumu değildir. Sıralamayı maçlardaki
          güç belirler: rakibin gücü, skor ve sahası hesaba katılır.{" "}
          <a href="/metodoloji/">Puanlar nasıl hesaplanıyor?</a>
        </p>
      </div>
    </>
  );
}
