// Every short text on the site, in English. Same shape as tr.ts (checked by the compiler).
import type { Messages } from "./tr";

export const en: Messages = {
  locale: "en-GB",
  months: ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
  result: {
    letter: { G: "W", B: "D", M: "L" },
    word: { G: "win", B: "draw", M: "loss" },
  },

  frame: {
    skip: "Skip to content",
    updated: (date, model) => `Ratings last updated after the matches of ${date}. Model ${model}.`,
    footerNav: "About this site",
    how: "How the ratings work",
    about: "About",
    sources: "Sources",
    privacy: "Privacy",
  },
  nav: {
    label: "Main menu",
    rankings: "Rankings",
    fixtures: "Fixtures",
    methodology: "Methodology",
    switchTo: "Türkçe",
  },
  theme: {
    system: "System",
    light: "Light",
    dark: "Dark",
    aria: (choice) => `Colour theme: ${choice}. Change`,
  },
  notFound: {
    title: "This page does not exist",
    text: "This page does not exist.",
    home: "Go to the rankings",
  },

  home: {
    description:
      "Every professional football club in Turkey, from the Süper Lig to the 3. Lig, on one Elo scale. Every rating change explained.",
    title: "Turkey's professional clubs, on one ruler",
    intro: (n) =>
      `Elo is a strength rating built from results: after every match the two clubs exchange points, and an unexpected result moves more of them. ${n} clubs from the Süper Lig down to the 3. Lig share one scale; European matches count too, with foreign opponents rated from their UEFA coefficient.`,
    updated: (date) => `Ratings include the matches of ${date}.`,
    how: "How the ratings work",
    ruler: (ranges) => `Every club's rating on one scale. Ranges: ${ranges}.`,
  },
  standings: {
    filter: "Filter by league",
    all: "All",
    search: "Find a club",
    caption: "Ranked by Elo rating",
    rank: "Rank",
    club: "Club",
    league: "League",
    rating: "Rating",
    week: "7 days",
    weekTitle: "Change over the last 7 days",
    form: "Last 5",
    withdrew: (season, league) => `Withdrew from the ${league} in ${season}`,
    left: (season, league) => `${league} in ${season}`,
    none: (q) => `No club matches “${q}”.`,
    clear: "Clear the search",
    inactive: "Also show clubs that have left the professional leagues since 2021-22",
  },
  movers: {
    title: "This week",
    range: (a, b) => `Matches from ${a} to ${b}`,
    up: "Biggest gains",
    down: "Biggest losses",
    none: "No change this week.",
  },
  form: {
    label: (n, words) => `Last ${n} matches: ${words}`,
  },
  league: {
    title: (league) => `${league} Elo ranking`,
    lead: (n, lo, hi, mean, date) =>
      `${n} clubs, rated from ${lo} to ${hi}, mean ${mean}. The other leagues' clubs are shown faded on the same ruler. Includes the matches of ${date}.`,
    ruler: (league) => `${league} clubs' ratings on the same scale as every other league.`,
    caption: "Elo ranking",
    head: ["Rank", "Club", "Rating", "7 days", "Last 5", "Overall"],
    weekTitle: "Change over the last 7 days",
    note: "This table is ordered by Elo rating, not the official standings. Strength in matches decides it: the opponent's strength, the score and the ground all count.",
    how: "How the ratings work",
  },
  team: {
    title: (club) => `${club} Elo rating`,
    description: (club, rating, league) =>
      `${club}: Elo rating ${rating}, ${league}. How the rating changed, match by match.`,
    withdrew: (season, league, date) =>
      `Withdrew from the ${league} in ${season}: since ${date} its matches count as forfeits and do not change its rating.`,
    left: (season, league) =>
      `Last played in the ${league} in ${season}. No longer in the professional leagues; its rating has not changed since.`,
    official: "Name at the TFF",
    rating: "Elo rating",
    rank: "Overall rank",
    leagueRank: (league) => `${league} rank`,
    last: "Last match",
    ruler: (club, rating, rank) => `${club}, rated ${rating}, ranks ${rank} among all clubs.`,
    next: (n) => (n > 1 ? "Next matches" : "Next match"),
  },
  timeline: {
    away: ", away",
    title: "Rating history",
    high: "Highest",
    low: "lowest",
    summary: (team, n, hi, lo, now) =>
      `${team} rating chart: ${n} changes, highest ${hi}, lowest ${lo}, now ${now}. Every value is in the match list below.`,
    list: "Rating change match by match",
    hint: "Open a match's row to see how its rating change was worked out.",
    rules: "How it is calculated",
  },
  history: {
    season: (s) => `${s} season`,
    matches: (n) => `${n} matches`,
    head: ["Date", "Opponent", "Score", "Change", "Rating"],
    away: "away",
    neutral: "neutral ground",
    pens: "pens",
    et: "a.e.t.",
    oppPage: (name) => `${name} rating page`,
    formula: "The formula",
    formulaAnchor: "#2-formula",
    permalink: "Link to this calculation",
    start: "Pre-season",
    startRow: (s) => `Adjustments before ${s}`,
    newcomer: (rating) => `Starting rating ${rating}.`,
  },
  fixture: {
    noDate: "Date not announced yet",
    week: (n) => `matchweek ${n}`,
    stakes: (club) => `Rating change for ${club}`,
    draw: "draw",
    odds: (home, h, d, away, a) => `Chances: ${home} win ${h}%, draw ${d}%, ${away} win ${a}%.`,
    pct: (n) => `${n}%`,
  },
  matches: {
    title: "Upcoming matches",
    description:
      "Every league's next matchweek and the cup ties: chances from the Elo ratings and what each result is worth.",
    lead: (date) =>
      `Every league's next matchweek and the cup ties with a date. Chances and rating changes use the ratings after the matches of ${date}; a change is for a one-goal result and grows with the margin. Dates are added as the TFF announces them.`,
    sections: "Sections",
    cup: "Cup",
    week: (n) => `matchweek ${n}`,
    noDates: "Dates not announced yet.",
  },
  methodology: {
    title: "How the ratings work",
    description: "The method behind Türk Ligleri Elo: formula, parameters, test results and limits.",
    lead: "The formula, the parameters and how they were chosen. This page is generated from",
    leadEnd: "in the repository.",
  },
  pages: {
    about: {
      title: "About",
      lead: (site) => `What ${site} is, who makes it, how to get in touch.`,
      description: (site) => `${site}: what it is, who makes it, how to get in touch.`,
    },
    sources: {
      title: "Sources",
      lead: () => "Where the data comes from and on what terms it is used.",
      description: (site) => `Where ${site}'s data comes from and on what terms.`,
    },
    privacy: {
      title: "Privacy",
      lead: () => "What this site collects about visitors, and what it does not.",
      description: (site) => `What ${site} collects about visitors, and what it does not.`,
    },
  },

  competitions: {
    TK: { name: "Turkish Cup", short: "Cup" },
    SK: { name: "Turkish Super Cup", short: "Super Cup" },
    UCL: { name: "Champions League", short: "UCL" },
    UEL: { name: "Europa League", short: "UEL" },
    UECL: { name: "Conference League", short: "UECL" },
  },
  leagueShort: "League",
  europeRounds: {
    PR: "preliminary round", Q1: "first qualifying round", Q2: "second qualifying round",
    Q3: "third qualifying round", PO: "play-off round", GS: "group stage", LP: "league phase",
    KPO: "knockout play-off", R32: "round of 32", R16: "round of 16", QF: "quarter-final",
    SF: "semi-final", F: "final",
  },
  rounds: {
    tur: (n) => `Round ${n}`,
    known: {
      "yarı final": "Semi-final", "çeyrek final": "Quarter-final", final: "Final",
      "son 16": "Round of 16", "son 32": "Round of 32", "ön eleme": "Preliminary round",
    },
  },
  groups: {
    numbered: (n) => `Group ${n}`,
    named: (g) => `${g} Group`,
    colours: { Beyaz: "White", Kırmızı: "Red" },
  },
  adjustments: (p) => ({
    promotion: { name: "Promotion adjustment", why: "A promoted club gains points for its new league." },
    relegation: { name: "Relegation adjustment", why: "A relegated club loses points." },
    regression: {
      name: "Pull to the mean",
      why: `Squads change over the summer, so the rating moves ${p.pct}% of the way to the league mean.`,
    },
    anchor: {
      name: "Scale shift",
      why: `Every rating moves by the same amount so that the 3. Lig mean is ${p.anchor}. The order does not change.`,
    },
    cup: { name: "Turkish Cup winners", why: "A bonus for winning the cup." },
    supercup: { name: "Super Cup winners", why: "A bonus for winning the Super Cup." },
    champion: { name: "Title bonus", why: "" },
    newcomer: {
      name: "Joined the professional leagues",
      why: `A club coming up from amateur football starts ${p.gap} points ${p.below ? "below" : "above"} the 3. Lig mean.`,
    },
    return: { name: "Back in the professional leagues", why: "A club back from amateur football starts like a newcomer." },
  }),

  explain: {
    before: (team, r, opp, ro) => `Before the match: ${team} ${r}, ${opp} ${ro}.`,
    foreign: " A foreign opponent's rating comes from its UEFA club coefficient.",
    amateur: " Amateur opponents always have the same rating.",
    neutral: " Neutral ground, no home advantage.",
    closed: (host, h) => ` ${host} were at home; behind closed doors, home advantage counted as ${h} points.`,
    home: (host, h) => ` ${host} were at home, worth ${h} points of advantage.`,
    chances: (team, w, d, l) => `With these ratings, ${team}'s chances were: win ${w}%, draw ${d}%, loss ${l}%.`,
    result: (score, word, why, delta) => `Result ${score}, ${word}. ${why}: ${delta}.`,
    why: {
      G: ["An upset win, so the rating rose a lot", "An even match, won",
          "As favourites, the win raised the rating only a little"],
      B: ["As the weaker side, the draw gained points", "In an even match the draw changed little",
          "As favourites, the draw cost points"],
      M: ["An expected defeat, so the rating fell only a little", "An even match, lost",
          "An unexpected defeat, so the rating fell a lot"],
    },
    pens: " A penalty shoot-out counts as a draw in Elo.",
    extraTime: (a, b) => ` (after extra time; ${a}-${b} after 90 minutes)`,
    shootout: (a, b) => `, ${a}-${b} on penalties`,
    margin: (n, g) => `A ${n}-goal margin multiplied the change by ${g}.`,
    amateurWeight: (w) => `A cup match against an amateur club counts with weight ${w}.`,
    weight: (comp, w) => `${comp} matches count with weight ${w}.`,
    provisional: (n, f) =>
      `One of the club's first ${n} professional matches, so the change was multiplied by ${f}.`,
    regression: (gap, above, pct, delta) =>
      `${gap} points ${above ? "above" : "below"} the league mean. Squads change over the summer, so ${pct}% of that gap was closed: ${delta}.`,
  },
};
