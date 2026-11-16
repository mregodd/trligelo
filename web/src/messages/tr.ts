// Every short text on the site, in Turkish. en.ts has the same shape and the compiler checks
// it: a missing or extra key there is a build error. To add a language, copy en.ts, translate
// it and register it in index.ts. Long pages (about, sources, privacy) are Markdown files in
// web/content/<lang>/; the methodology is docs/METODOLOJI.md and its translations.
import type { AdjustmentKind } from "@/lib/types";

type Adjustments = Record<AdjustmentKind, { name: string; why: string }>;
type Why = { G: string[]; B: string[]; M: string[] }; // each: [underdog, even, favourite]

export const tr = {
  locale: "tr-TR",
  months: ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
           "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
  result: {
    letter: { G: "G", B: "B", M: "M" }, // the data's own letters: win, draw, loss
    word: { G: "galibiyet", B: "beraberlik", M: "mağlubiyet" },
  },

  frame: {
    skip: "İçeriğe geç",
    updated: (date: string, model: string) =>
      `Puanlar son olarak ${date} tarihli maçlara göre hesaplandı. Model ${model}.`,
    footerNav: "Site bilgileri",
    how: "Puanlar nasıl hesaplanıyor?",
    about: "Hakkında",
    sources: "Kaynaklar",
    privacy: "Gizlilik",
  },
  nav: {
    label: "Ana menü",
    rankings: "Sıralama",
    fixtures: "Maçlar",
    methodology: "Metodoloji",
    switchTo: "English", // the other language, named in itself
  },
  theme: {
    system: "Sistem",
    light: "Açık",
    dark: "Koyu",
    aria: (choice: string) => `Renk teması: ${choice}. Değiştir`,
  },
  notFound: {
    title: "Bu sayfa yok",
    text: "Adres yanlış yazılmış ya da kulüp artık listede olmayabilir.",
    home: "Genel sıralamaya dön",
  },

  home: {
    docTitle: (site: string) => `${site}: Türk futbol kulüplerinin Elo puanları`,
    description:
      "Süper Lig, 1. Lig, 2. Lig ve 3. Lig'deki bütün profesyonel kulüpler tek bir Elo cetvelinde. Her maçın puan hesabı açık.",
    title: "Türkiye'nin profesyonel kulüpleri, tek cetvelde",
    intro: (n: number) =>
      `Elo, maç sonuçlarından hesaplanan bir güç puanı: her maçtan sonra iki takım arasında puan el değiştirir, beklenmeyen sonuç daha çok puan taşır. Süper Lig'den 3. Lig'e ${n} kulüp aynı ölçekte; Avrupa kupalarındaki maçlar da sayılır, yabancı rakiplerin gücü UEFA katsayısından gelir.`,
    updated: (date: string) => `Puanlar ${date} maçlarına kadar güncel.`,
    how: "Puanlar nasıl hesaplanıyor?",
    ruler: (ranges: string) => `Bütün kulüplerin puanları tek ölçekte. Puan aralıkları: ${ranges}.`,
  },
  standings: {
    filter: "Lige göre süz",
    all: "Tümü",
    search: "Kulüp ara",
    caption: "Elo puanına göre sıralama",
    rank: "Sıra",
    club: "Kulüp",
    league: "Lig",
    rating: "Puan",
    week: "7 gün",
    weekTitle: "Son 7 gündeki değişim",
    form: "Son 5 maç",
    withdrew: (season: string, league: string) => `${season}'de ${league}'den çekildi`,
    left: (season: string, league: string) => `${season} sezonunda ${league}`,
    none: (q: string) => `“${q}” ile eşleşen kulüp yok.`,
    clear: "Aramayı temizle",
    inactive: "2021-22'den beri profesyonel ligden ayrılan kulüpleri de göster",
  },
  movers: {
    title: "Bu hafta",
    range: (a: string, b: string) => `${a} – ${b} arasındaki maçlar`,
    up: "En çok kazananlar",
    down: "En çok kaybedenler",
    none: "Bu hafta değişim yok.",
  },
  form: {
    label: (n: number, words: string) => `Son ${n} maç: ${words}`,
  },
  league: {
    title: (league: string) => `${league} Elo sıralaması`,
    lead: (n: number, lo: string, hi: string, mean: string, date: string) =>
      `${n} kulüp, puanlar ${lo} ile ${hi} arasında, ortalama ${mean}. Diğer liglerin kulüpleri aynı cetvelde soluk gösteriliyor. ${date} maçlarına kadar güncel.`,
    ruler: (league: string) => `${league} kulüplerinin puanları bütün liglerle aynı ölçekte.`,
    caption: "Elo sıralaması",
    head: ["Sıra", "Kulüp", "Puan", "7 gün", "Son 5 maç", "Genel sıra"],
    weekTitle: "Son 7 gündeki değişim",
    note: "Bu tablo Elo puanına göre sıralanır, resmi puan durumu değildir. Sıralamayı maçlardaki güç belirler: rakibin gücü, skor ve sahası hesaba katılır.",
    how: "Puanlar nasıl hesaplanıyor?",
  },
  team: {
    title: (club: string) => `${club} Elo puanı`,
    description: (club: string, rating: string, league: string) =>
      `${club}: Elo puanı ${rating}, ${league}. Puanın maç maç nasıl değiştiği.`,
    withdrew: (season: string, league: string, date: string) =>
      `${season} sezonunda ${league}'den çekildi: ${date} tarihinden beri maçları hükmen sayılıyor ve puanını değiştirmiyor.`,
    left: (season: string, league: string) =>
      `Son olarak ${season} sezonunda ${league}'de oynadı. Şu an profesyonel ligde değil; puanı o günden beri değişmedi.`,
    official: "TFF'deki adı",
    rating: "Elo puanı",
    rank: "Genel sıra",
    leagueRank: (league: string) => `${league} sırası`,
    last: "Son maç",
    ruler: (club: string, rating: string, rank: number | null) =>
      `${club}, ${rating} puanla bütün kulüpler arasında ${rank}. sırada.`,
    next: (n: number): string => (n > 1 ? "Sıradaki maçlar" : "Sıradaki maç"),
  },
  timeline: {
    away: ", deplasman",
    title: "Puan geçmişi",
    high: "En yüksek",
    low: "en düşük",
    summary: (team: string, n: number, hi: string, lo: string, now: string) =>
      `${team} puan grafiği: ${n} değişiklik, en yüksek ${hi}, en düşük ${lo}, şu an ${now}. Bütün değerler aşağıdaki maç listesinde.`,
    list: "Maç maç puan değişimi",
    hint: "Bir maçın satırını açınca o maçın puan hesabı görünür.",
    rules: "Hesabın kuralları",
  },
  history: {
    season: (s: string) => `${s} sezonu`,
    matches: (n: number) => `${n} maç`,
    head: ["Tarih", "Rakip", "Skor", "Değişim", "Puan"],
    home: "iç saha",
    away: "deplasman",
    neutral: "tarafsız saha",
    pens: "pen.",
    et: "uz.",
    start: "Sezon başı",
    startRow: (s: string) => `${s} öncesi ayarlar`,
    newcomer: (rating: string) => `Başlangıç puanı ${rating}.`,
  },
  fixture: {
    noDate: "Tarih henüz açıklanmadı",
    week: (n: number) => `${n}. hafta`,
    stakes: (club: string) => `${club} için puan değişimi`,
    draw: "beraberlik",
    odds: (home: string, h: number, d: number, away: string, a: number) =>
      `Şanslar: ${home} kazanır %${h}, beraberlik %${d}, ${away} kazanır %${a}.`,
    pct: (n: number) => `%${n}`,
  },
  matches: {
    title: "Yaklaşan maçlar",
    description:
      "Her ligin sıradaki haftası ve kupa maçları: Elo puanlarına göre şanslar ve her sonucun puana etkisi.",
    lead: (date: string) =>
      `Her ligin sıradaki haftası ve tarihi açıklanmış kupa maçları. Şanslar ve puan değişimleri ${date} maçlarından sonraki puanlarla hesaplanır; değişimler bir farklı sonuç içindir, fark büyüdükçe artar. Tarihler TFF açıkladıkça eklenir.`,
    sections: "Bölümler",
    cup: "Kupa",
    week: (n: number) => `${n}. hafta`,
    noDates: "Tarihler henüz açıklanmadı.",
  },
  methodology: {
    title: "Puanlar nasıl hesaplanıyor?",
    description: "trligelo'nun yöntemi: formül, parametreler, test sonuçları ve sınırlamalar.",
    lead: "Formül, parametreler ve bunların nasıl seçildiği. Bu sayfa repodaki",
    leadEnd: "dosyasından üretilir.",
  },
  pages: {
    about: {
      title: "Hakkında",
      lead: (site: string) => `${site} nedir, kim geliştiriyor, nasıl ulaşılır.`,
      description: (site: string) => `${site}: ne olduğu, kimin geliştirdiği, nasıl ulaşılacağı.`,
    },
    sources: {
      title: "Kaynaklar",
      lead: (_site: string) => "Verilerin nereden geldiği ve hangi koşullarla kullanıldığı.",
      description: (site: string) => `${site} verilerinin kaynakları ve kullanım koşulları.`,
    },
    privacy: {
      title: "Gizlilik",
      lead: (_site: string) => "Bu site ziyaretçiler hakkında ne topluyor, ne toplamıyor.",
      description: (site: string) => `${site} ziyaretçiler hakkında ne topluyor, ne toplamıyor.`,
    },
  },

  competitions: {
    TK: { name: "Ziraat Türkiye Kupası", short: "Kupa" },
    SK: { name: "Süper Kupa", short: "Süper Kupa" },
    UCL: { name: "Şampiyonlar Ligi", short: "ŞL" },
    UEL: { name: "Avrupa Ligi", short: "AL" },
    UECL: { name: "Konferans Ligi", short: "KL" },
  } as Record<string, { name: string; short: string }>,
  leagueShort: "Lig",
  europeRounds: {
    PR: "ön eleme", Q1: "1. eleme turu", Q2: "2. eleme turu", Q3: "3. eleme turu",
    PO: "play-off turu", GS: "grup aşaması", LP: "lig aşaması", KPO: "eleme play-off'u",
    R32: "son 32", R16: "son 16", QF: "çeyrek final", SF: "yarı final", F: "final",
  } as Record<string, string>,
  rounds: {
    tur: (n: string) => `${n}. Tur`, // TFF writes "4.Tur"
    known: {} as Record<string, string>, // other TFF round names, by their lower-case Turkish name
  },
  groups: {
    numbered: (n: number) => `${n}. Grup`,
    named: (g: string) => `${g} Grup`,
    colours: {} as Record<string, string>,
  },
  adjustments: (p: { pct: string; gap: string; anchor: string; below: boolean }): Adjustments => ({
    promotion: { name: "Yükselme düzeltmesi", why: "Üst lige çıkan takım, yeni ligine uyum için puan alır." },
    relegation: { name: "Düşme düzeltmesi", why: "Alt lige düşen takım puan kaybeder." },
    regression: {
      name: "Ortalamaya çekme",
      why: `Yaz aylarında kadrolar değiştiği için puan, ligin ortalamasına doğru %${p.pct} çekilir.`,
    },
    anchor: {
      name: "Ölçek ayarı",
      why: `Bütün puanlar aynı miktarda kaydırılır, 3. Lig ortalaması ${p.anchor} olur. Sıralamayı değiştirmez.`,
    },
    cup: { name: "Türkiye Kupası şampiyonluğu", why: "Kupa şampiyonuna bonus." },
    supercup: { name: "Süper Kupa şampiyonluğu", why: "Süper Kupa şampiyonuna bonus." },
    champion: { name: "Şampiyonluk bonusu", why: "" },
    newcomer: {
      name: "Profesyonel lige katıldı",
      why: `Amatör ligden gelen takım, 3. Lig ortalamasının ${p.gap} puan ${p.below ? "altından" : "üstünden"} başlar.`,
    },
    return: { name: "Profesyonel lige döndü", why: "Amatöre düşüp dönen takım yeni gelen gibi başlar." },
  }),

  // A match told in plain words (components/History.tsx). Club names never take a suffix
  // here, since Turkish suffixes follow the word's sounds: sentences are built for names to
  // stand alone. {name} marks where a club or a number goes (it can be a link or bold).
  explain: {
    before: "Maç öncesi {team} {r}, {opp} {ro} puandaydı.",
    foreign: " Yabancı rakibin puanı UEFA kulüp katsayısından hesaplanır.",
    amateur: " Amatör rakiplerin puanı her maçta aynıdır.",
    neutral: "Maç tarafsız sahada oynandı, ev avantajı yok.",
    hostTeam: "{team} ev sahibiydi: kazanma şansı ev avantajıyla {with}, tarafsız sahada {without} olurdu.",
    hostOpp: "{opp} ev sahibiydi: {team} için kazanma şansı deplasmanda {with}, tarafsız sahada {without} olurdu.",
    closed: " Maç seyircisiz oynandığı için ev avantajı daha küçük sayıldı.",
    chances: "Maç öncesi şanslar",
    chancesNote: "Kalın olan gerçekleşen sonuç. Değişimler bir farklı sonuç içindir, fark büyüdükçe artar.",
    result: (score: string, word: string, delta: string) => `Sonuç ${score}, ${word}: ${delta}.`,
    surprise: (p: number, n: number) =>
      ` Maç öncesi ihtimali %${p} olan bir sonuçtu, yani yaklaşık ${n} maçta bir olur.`,
    streak: {
      wins: (n: number) => `Üst üste ${n}. galibiyeti.`,
      losses: (n: number) => `Üst üste ${n}. yenilgisi.`,
      unbeaten: (n: number) => `Yenilmezlik serisi ${n} maça çıktı.`,
      winless: (n: number) => `Galibiyetsiz seri ${n} maça çıktı.`,
      endedWins: (n: number) => `${n} maçlık galibiyet serisi sona erdi.`,
      endedLosses: (n: number) => `${n} maçlık yenilgi serisine son verdi.`,
      endedUnbeaten: (n: number) => `${n} maçlık yenilmezlik serisi sona erdi.`,
      endedWinless: (n: number) => `${n} maçlık galibiyet hasretine son verdi.`,
    },
    why: {
      G: ["Sürpriz bir galibiyet olduğu için puanı çok artırdı", "Denk bir maçı kazandı",
          "Favori olduğu için galibiyet puanı az artırdı"],
      B: ["Zayıf görülen taraf olduğu için beraberlik puan kazandırdı",
          "Denk bir maçta beraberlik puanı pek değiştirmedi",
          "Favori olduğu için beraberlik puan kaybettirdi"],
      M: ["Beklenen bir yenilgi olduğu için puanı az düşürdü", "Denk bir maçı kaybetti",
          "Beklenmeyen bir yenilgi olduğu için puanı çok düşürdü"],
    } as Why,
    pens: " Penaltı atışları Elo'da beraberlik sayılır.",
    extraTime: (a: number, b: number) => ` (uzatmalarda; 90 dakika ${a}-${b})`,
    shootout: (a: number, b: number) => `, penaltılar ${a}-${b}`,
    margin: (n: number, g: string) => `Fark ${n} gol olduğu için değişim ${g} katına çıktı.`,
    amateurWeight: (w: string) => `Amatör bir rakiple oynanan kupa maçı ${w} ağırlıkla sayılır.`,
    weight: (comp: string, w: string) => `${comp} maçları ${w} ağırlıkla sayılır.`,
    provisional: (n: number, f: string) =>
      `Kulübün profesyonel liglerdeki ilk ${n} maçından biri olduğu için değişim ${f} katına çıktı.`,
    regression: (gap: string, above: boolean, pct: string, delta: string) =>
      `Ligin ortalamasının ${gap} puan ${above ? "üstündeydi" : "altındaydı"}. Yaz aylarında kadrolar değiştiği için bu fark %${pct} oranında kapatıldı: ${delta}.`,
  },
};

export type Messages = typeof tr;
