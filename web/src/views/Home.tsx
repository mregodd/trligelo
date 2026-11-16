import type { Metadata } from "next";

import { Movers } from "@/components/Movers";
import { Standings } from "@/components/Standings";
import { getMeta, getTeams } from "@/lib/data";
import { fmt } from "@/lib/format";
import { href, type Lang } from "@/lib/i18n";
import { LEAGUES } from "@/lib/labels";
import { SITE } from "@/lib/site";
import { msg } from "@/messages";

import styles from "./Home.module.css";

export function homeMetadata(lang: Lang): Metadata {
  const t = msg(lang).home;
  // The short name alone says little in a tab or a search result, so the home page spells it out.
  return { title: { absolute: t.docTitle(SITE) }, description: t.description };
}

export function HomeView({ lang }: { lang: Lang }) {
  const t = msg(lang).home;
  const meta = getMeta();
  const teams = getTeams();
  const active = teams.filter((c) => c.active);
  const f = fmt(lang);

  // Spoken summary of the ruler for screen readers (the table below carries every value).
  const ranges = LEAGUES.map((l) => {
    const r = active.filter((c) => c.league === l.code).map((c) => c.rating);
    return `${l.name} ${f.rating(Math.min(...r))}–${f.rating(Math.max(...r))}`;
  }).join("; ");

  return (
    <Standings
      lang={lang}
      teams={teams}
      rulerLabel={t.ruler(ranges)}
      heading={
        <div className={styles.heading}>
          <h1>{t.title}</h1>
          <p>{t.intro(meta.activeTeams)}</p>
          <p>
            {t.updated(f.dateLong(meta.lastMatch))} <a href={href(lang, "/metodoloji/")}>{t.how}</a>
          </p>
        </div>
      }
      aside={<Movers teams={teams} meta={meta} lang={lang} />}
    />
  );
}
