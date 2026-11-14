# Türk Ligleri Elo — Proje Planı

> **Durum:** v0.5 (14 Kasım 2026). Faz 0, 1a, 1b ve 2 tamamlandı; model v1.0. Faz 0 bulguları için bkz. [faz-0-kesif.md](faz-0-kesif.md). Avrupa kaynağı Wikipedia'ya geçti (bkz. §3 ve §4.7).
> Sayılar ve parametreler **başlangıç önerisidir**. Son değerleri geçmiş veri üzerinde yapılacak geriye dönük test belirleyecek.

---

## 1. Amaç ve ilkeler

- Türk profesyonel liglerindeki (Süper Lig, 1. Lig, 2. Lig, 3. Lig) bütün takımları **tek bir ölçekte** puanlayan, açık kaynaklı ve düzenli güncellenen bir Elo sistemi.
- **Ticari değil:** Üyelik, reklam ve ücretli API yok. Kod, veri işleme adımları ve formül herkese açık.
- **Şeffaflık:** Formül ve parametreler sitede yazılı. Her maçın hesabı tek tek görülebiliyor. İsteyen herkes repoyu klonlayıp aynı puanları üretebilmeli (bkz. §7).
- **"Doğru parametre" ölçülebilir olmalı:** Doğru parametre, maç sonuçlarını en iyi tahmin eden parametredir. Değerler sezgiyle değil, geçmiş sezonlar üzerinde geriye dönük testle seçilir (bkz. §4.9).
- **Güncellik:** Puanlar maçlar bittikten kısa bir süre sonra güncellenir. Maç sırasında dakika dakika güncelleme yapılmaz.
- **Minimum maliyet:** Hedef 0 TL/ay. Tek gider alan adı (yıllık).

## 2. Kapsam

| Dahil | Hariç (şimdilik) |
|---|---|
| Lig maçları (play-off dahil) | Hazırlık maçları |
| Ziraat Türkiye Kupası | Yaz turnuvaları ve özel kupalar |
| Süper Kupa | A Milli Takım |
| UEFA kulüp turnuvaları (Şampiyonlar Ligi, Avrupa Ligi, Konferans Ligi, ön elemeler dahil) | Kadın, genç ve U-ligleri |

## 3. Veri kaynakları

| Kaynak | Kapsam | Maliyet / koşul | Karar |
|---|---|---|---|
| **tff.org** | 4 profesyonel lig, gruplar, play-off'lar, kupa, arşiv | Ücretsiz. Kullanım Şartları: *"kaynak gösterilmek suretiyle yayımlanabilir; ancak bu bilgiler ticari amaçlarla kullanılamaz."* | **Birincil kaynak.** Sitede ve repoda kaynak gösterilir. |
| **Wikipedia (İngilizce), UEFA turnuva sayfaları** | Türk takımlarının bütün Avrupa maçları (ön elemeler dahil). Çekiliş tablolarındaki UEFA kulüp katsayıları. Sezon sayfalarındaki ülke katsayısı sıralaması | CC BY-SA 4.0, kaynak gösterilir. Sadece makale sayfaları (`/wiki/`) okunur; robots.txt bunlara izin veriyor | **Avrupa için birincil kaynak** (bkz. §4.7) |
| openfootball/champions-league | Avrupa kupası maç sonuçları (kısmi kapsam: 202 Türk takımı maçı) | CC0 | Çapraz doğrulama: 201 maç birebir aynı, 1 maçta tarih farkı (yarıda kalıp ertesi gün tamamlanan PSG–Başakşehir) |
| kassiesa.net | Bütün sezonların UEFA kulüp ve ülke katsayıları | robots.txt bütün otomatik istemcileri engelliyor (`User-agent: *`, `Disallow: /`) | **Kullanılmayacak** |
| ClubElo (api.clubelo.com) | Avrupa kulüplerinin günlük Elo puanları | API 1 Eylül 2026'dan beri 502 veriyor, site bot korumasının arkasında | **Şu an kullanılamıyor.** Geri gelirse yeniden değerlendirilir |
| football-data.co.uk | Sadece Süper Lig, 1994'ten bu yana, CSV ve **bahis oranları** | Ücretsiz | Çapraz kontrol ve testte piyasa kıyası |
| Wikipedia, yurt içi lig sayfaları | Çoğu lig için sezon sayfaları | CC BY-SA | Gerekirse çapraz doğrulama |
| TheSportsDB | Süper Lig, 1. Lig | Ücretsiz anahtarın sınırları var | Yedek |
| API-Football | Bütün Türk ligleri | Ücretsiz plan güncel sezonu kapsamıyor (yalnızca 2022–2024) | Elendi |
| football-data.org | Süper Lig ve 1. Lig | Sadece ücretli planlarda | Elendi |
| Sofascore, Mackolik, Flashscore, Transfermarkt | Her şey | Resmi açık API yok, şartları kazımaya uygun değil | Kullanılmayacak |

TFF sayfaları seyrek ve nazik biçimde taranır: önbellekli, düşük sıklıkta, sadece değişen sayfalar.

---

## 4. Elo modeli

### 4.1 İlham kaynakları: hangi sistemden ne alıyoruz

| Sistem | Aldığımız fikir | Almadığımız |
|---|---|---|
| Satranç (FIDE Elo) | Temel formül. Yeni oyuncuya daha yüksek K verilmesi (bizde yeni giren veya uzun aradan dönen takımlar için) | Bireysel oyuncu mantığı |
| CS2 VRS | Zaman penceresi, eski sonuçların etkisinin azalması (bizde görünürlük penceresi ve sezon arası ortalamaya çekme) | Ödül parası gibi futbola uymayan faktörler |
| Futbol Elo'ları (World Football Elo, ClubElo, FiveThirtyEight) | Ev sahibi avantajı, gol farkı çarpanı, turnuva ağırlığı | — |

### 4.2 Temel formül

"Önce sabit bir puan, üstüne sıralama farkına göre ekstra veya eksik" fikri Elo'nun kendisi. Sabit kısım K, ekstra kısım ise beklenen skorla gerçekleşen sonuç arasındaki fark.

```
Ev sahibinin beklenen skoru:
  E = 1 / (1 + 10^( -(R_ev + H - R_dep) / 400 ))

Maç sonrası değişim:
  Δ = K × W × G × (S − E)
  R_ev  ← R_ev  + Δ
  R_dep ← R_dep − Δ          (biri ne kazanırsa diğeri onu kaybeder)
```

| Sembol | Anlamı |
|---|---|
| R | Takımın maç öncesi puanı |
| H | Ev sahibi avantajı (puan cinsinden). Tarafsız sahada 0 |
| S | Sonuç: galibiyet 1, beraberlik 0,5, mağlubiyet 0 |
| E | Beklenen skor (0–1 arası; kazanma olasılığı + beraberlik olasılığının yarısı) |
| K | Temel hassasiyet katsayısı (bir maçın en fazla kaç puan oynatabileceği) |
| W | Turnuva ağırlığı (lig, kupa, Avrupa…) |
| G | Gol farkı çarpanı |

**Örnekler** (K=20, W=1, G=1, H=0):

| Durum | E | Δ (kazanan veya favori için) |
|---|---|---|
| 1500'lük iki takım, biri kazanır | 0,50 | +10,0 ("sabit getiri") |
| 1400'lük takım 1600'lüğü yener | 0,24 | +15,2 (sürpriz, daha çok puan) |
| 1600'lük takım 1400'lüğü yener | 0,76 | +4,8 (beklenen sonuç, az puan) |
| 1600 ile 1400 berabere kalır | 0,76 | favori −5,2 kaybeder |

Paydaki 400 değiştirilmez. Satranç ve ClubElo ile aynı anlamı taşısın: 200 puan fark ≈ güçlü takım için %76 beklenen skor.

### 4.3 Parametreler

Başlangıç değerleri planlamada seçildi. v1.0 değerleri Faz 2'deki geriye dönük testle belirlendi; bkz. [faz-2-rapor.md](faz-2-rapor.md). Sadece testin açıkça desteklediği değerler değiştirildi.

| Parametre | Başlangıç | **v1.0** | Not |
|---|---|---|---|
| K | 20 | **24** | |
| H (ev sahibi avantajı) | ~65 | **65** | Tarafsız sahada 0 |
| H seyircisiz (pandemi) | — | **50** | Doğrudan ölçüldü: ev sahibinin ortalama skoru 0,582'den 0,566'ya düştü |
| H Avrupa | — | **73** | Avrupa maçlarından a ve b ile birlikte uydurulur |
| G (gol farkı) | 1 farkta 1; 2 farkta 1,5; N≥3 farkta (11+N)/8 | **Aynı** | eloratings.net yaklaşımı. Testte en büyük etkilerden biri |
| W lig / play-off | 1,0 | **1,0** | |
| W Türkiye Kupası | 0,75 (final 1,0) | **0,75 (final 1,0)** | Büyük takımlar erken turlarda rotasyon yapıyor |
| W Süper Kupa | 0,75 | **0,75** | Tek maç, sezon başı |
| W Avrupa | 1,0 | **1,0** | |
| W amatörle kupa maçı | — | **Kupa ağırlığı × 1,5** | |
| Geçici K | İlk 10 maçta ×1,5 | **Aynı** | Sisteme yeni giren veya amatörden dönen takımlar için |
| Sezon arası ortalamaya çekme (α) | 0,10 | **0,30** | Her yaz `R ← R − α × (R − lig ortalaması)`. Kadro değişimini yansıtır, lig toplamını değiştirmez |
| Yükselme/düşme düzeltmesi (P) | Bkz. §4.6 | **Aynı** | |
| Kupa şampiyonluğu bonusu (B) | Bkz. §4.6 | **Aynı** | |

Ek kurallar:
- **Penaltılar:** Maç berabere sayılır. Uzatmalı maçlarda 120 dakikanın sonucu esas alınır.
- **Hükmen sonuçlar:** Elo'ya katılmaz, çünkü maç sahada oynanmadı.

### 4.4 Başlangıç puanları ve ligler arası kalibrasyon

**Sorun:** Her takım neredeyse bütün maçlarını kendi liginde oynuyor ve lig içinde puan toplamı sabit. Ligler arasında puan sadece kupa maçları ve küme düşen/yükselen takımlar üzerinden akıyor. Herkes 1000'den başlarsa ligler arasındaki gerçekçi farkın oluşması 5–8 sezon sürer.

**Karar:**
1. **Sabit başlangıç puanı:** Hesaplama döneminin ilk sezonunda (bkz. §4.8) her takıma liginin seviyesine göre sabit bir puan verilir. Sonra bütün maçlar tarih sırasıyla bugüne kadar işlenir. Taslak değerler: Süper Lig 1450, 1. Lig 1275, 2. Lig 1125, 3. Lig 1000.
2. **Isınma dönemi:** İlk sezonların puanları oturana kadar sitede gösterilmez.
3. **Veriyle kalibrasyon:** Seviyeler arasındaki fark tahminle değil, kupadaki farklı lig maçlarından ölçülür. Üst lig takımının alt lig takımına karşı ortalama skoru p ise:
   `fark = 400 × log10(p / (1 − p))`. Örneğin p = 0,70 için fark ≈ 147 puan.
   Kupadaki rotasyon bu farkı olduğundan küçük gösterebilir. Bu yüzden yükselen takımların ilk sezon performansı ikinci bir ölçüt olarak kullanılır.

### 4.5 Ölçek: okunabilir bir aralık (~700–2000)

Elo'da sadece puan farkları anlamlıdır. Bütün puanlara aynı sabit eklenirse hiçbir tahmin değişmez. Bu yüzden ölçeğin nereye oturacağını biz seçeriz.

- **Hedef:** Puanların kabaca **700–2000** aralığında, okunması kolay sayılar olması.
- **Referans noktası:** Her sezon başında 3. Lig ortalaması 1000'e sabitlenir. Ligler arası fark ~150–175 puan civarında çıkarsa tahmini tablo şöyle olur:

  | Lig | Tahmini aralık |
  |---|---|
  | Süper Lig | ~1300–1750 |
  | 1. Lig | ~1200–1450 |
  | 2. Lig | ~1050–1300 |
  | 3. Lig | ~850–1150 |

  Bu tablo hedef aralığın içinde kalıyor. Süper Lig takımları 3000 gibi değerlere çıkmaz, çünkü en iyi ve en kötü takım arasındaki fark ~700–900 puan bekleniyor.
- Veri işlendiğinde dağılım hedef aralığın dışına taşarsa referans noktası kaydırılır (bütün puanlara aynı sabit eklenir veya çıkarılır). Bu, hiçbir sıralamayı veya tahmini değiştirmez.
- Referans noktasını sabitlemek, amatör ligden gelen ve amatöre düşen takımların ve kupa bonuslarının zamanla ölçeği şişirmesini de önler.

### 4.6 Yükselme/düşme düzeltmesi ve kupa bonusu

**Yükselme/düşme düzeltmesi (P):** Sezon sonunda, play-off'lar da bittikten sonra, yükselen takıma +P eklenir, düşen takımdan −P düşülür. P lig seviyesine göre değişir.

| Geçiş | P (başlangıç) |
|---|---|
| 1. Lig ↔ Süper Lig | 30 |
| 2. Lig ↔ 1. Lig | 25 |
| 3. Lig ↔ 2. Lig | 20 |
| 3. Lig → BAL | Takım pasif olur (§4.8). BAL'dan gelen takım sabit giriş puanıyla başlar |

- Bir sınırda yükselen ve düşen takım sayısı eşitse puan toplamı değişmez. Eşit değilse sezon başındaki ölçek sabitlemesi farkı dengeler.
- Bu düzeltme ligler arasındaki ayrışmayı da hızlandırır (§4.4'teki soruna yardımcı olur).
- **Test:** Geriye dönük test, yükselen takımların yeni liglerindeki ilk sezon sonuçlarını puanlarının beklentisiyle karşılaştırır. Yükselen takımlar beklenenden kötü oynuyorsa düzeltme fazla büyük demektir. Rapor P'nin tahmin başarısına etkisini gösterecek, son değere birlikte karar vereceğiz.

**Kupa şampiyonluğu bonusu (B):**

| Başarı | B (başlangıç) |
|---|---|
| Ziraat Türkiye Kupası şampiyonluğu | +15 |
| Süper Kupa şampiyonluğu | +5 |

- Bonus, kupayı kazanan takımın puan geçmişinde ayrı bir satır olarak görünür (örneğin "Türkiye Kupası şampiyonluğu: +15"). Böylece maç sonuçlarından gelen puanla karışmaz.
- Bu puan bir rakipten alınmadığı için havuza eklenir. Ölçek sabitlemesi (§4.5) bunu dengeler.
- Testte bonusun tahmin başarısını bozmadığı kontrol edilecek. Elo mantığına daha yakın bir alternatif de var: Kupanın son turlarına daha yüksek W vermek. İkisi birlikte de kullanılabilir.

**Lig sıralaması bonusu yok (önerim, §9.2 #14):** Ligi kaç numarada bitirdiği, takımın o sezonki maç sonuçlarının toplamıdır ve bu sonuçlar Elo'ya zaten işlenmiştir. Şampiyonluğa ya da ilk dörde ayrıca puan vermek aynı başarıyı iki kez saymak olur. Kupada durum farklı: Penaltıyla kazanılan tur Elo'da beraberlik sayıldığı için kupayı kazanmak maç sonuçlarına tam yansımaz. B bu boşluğu kapatır. P ise bir ödül değil, ligler arası ölçeği düzelten yapısal bir düzeltmedir. Başarılar (şampiyonluk, kupa, yükselme, Avrupa'da tur atlama) sitede puan değil **rozet** olarak gösterilir.

### 4.7 Avrupa kupaları ve amatör (PGL/BAL) rakipler

**Avrupa:** Yabancı rakip **sabit referans** olarak ele alınır. Maçtan sonra **sadece Türk takımının puanı değişir.** Avrupa'da iyi oynayan takım kazandığı puanı kendi ligine taşır ve lig zamanla güçlenir.

> **Değişiklik (Faz 0):** İlk karar rakibin puanını ClubElo'dan almaktı. ClubElo'nun API'si 1 Eylül 2026'dan beri çalışmıyor (bkz. [faz-0-kesif.md §6](faz-0-kesif.md)). Yerine UEFA kulüp katsayısı seçildi.
>
> **Değişiklik (Faz 1b):** Katsayılar kassiesa.net'ten alınacaktı. Sitenin robots.txt dosyası otomatik istemcileri engellediği için katsayılar Wikipedia'daki çekiliş tablolarından alınıyor. Bunlar o sezonun çekilişlerinde UEFA'nın kullandığı resmi kulüp katsayıları.

**Yöntem: UEFA kulüp katsayısı.**
- Rakibin o sezonki 5 yıllık UEFA kulüp katsayısı bizim ölçeğimize dönüştürülür: `R = a + b × ln(1 + katsayı puanı)`.
- a ve b, Türk takımlarının geçmiş Avrupa maçlarının (2016-17'den bu yana 446 oynanmış maç) sonuçlarını en iyi açıklayacak şekilde veriden hesaplanır.
- **Yedek:** Katsayı tablosunda bulunmayan rakiplere ülkelerinin UEFA katsayısına göre bir puan bandı atanır. Faz 1b sonunda bütün rakiplerin kulüp katsayısı bulundu; yedek sadece ileride bulunamayan bir rakip için var.
- Katsayılar her sezon ilgili Wikipedia sayfalarından okunur. Ek maliyeti yok.
- ClubElo geri gelirse onun puanı da kullanılabilir.
- **Tarafsız saha:** Wikipedia kutuları maçın tarafsız sahada oynandığını ayrıca belirtmiyor. Faz 2'de ev sahibi avantajı için elle tutulan kısa bir liste kullanılacak.
- **Turnuva seviyesi (ŞL / AL / KL):** Ayrı bir çarpan yok. Seviye farkı rakibin puanından gelir: Bayern'i yenmek, katsayısı düşük bir Konferans Ligi rakibini yenmekten çok daha fazla puan kazandırır, ona kaybetmek ise az kaybettirir. Katsayı 5 yıllık olduğu için yavaş değişir. O yüzden testte `R = a + b × ln(1 + katsayı) + c_turnuva` biçimi de denenecek. Örneğin katsayısı düşük ama Şampiyonlar Ligi'ne kalmış rakipler beklenenden güçlü çıkıyorsa c anlamlı olur ve modele eklenir (§9.2 #13).
- **Avrupa'da oynayan takımların puanı şişer mi?** a ve b, Türk takımlarının Avrupa sonuçlarına uydurulduğu için bütün Avrupa maçlarından gelen net puan yaklaşık sıfırdır. Beklentinin üstünde oynayan kazanır, altında oynayan kaybeder. Gruptan puansız çıkan takım puan kaybeder. Testte Avrupa maçları dahil ve hariç iki model de kurulacak. Ölçüt, yurt içi maçları tahmin başarısı. Avrupa maçları yurt içi tahminleri kötüleştiriyorsa W düşürülür.

**Amatör takımlar (Türkiye Kupası):** TFF'deki adıyla "Profesyonelliğe Geçiş Ligi" (PGL), eski adıyla BAL. Sabit bir puan (örneğin 3. Lig ortalamasının ~100 altı) ve düşük W. Sadece profesyonel takımın puanı değişir. Profesyonel ve amatör takımlar arasındaki maçlar yılda birkaç kez oynandığı için etkisi küçük.

### 4.8 Hesaplama dönemi ve görünürlük

**Puanlar ne kadar hızlı oturuyor?** K=20 ile bir takımın başlangıçtaki puan hatası her maçta ~%3,5 azalıyor. Yarılanma süresi ~20 maç. Bir sezon sonunda başlangıç hatasının ~%30'u, iki sezon sonunda ~%10'u kalıyor. Ligler arası fark ise daha yavaş oturuyor, çünkü sadece kupa maçları ve yükselen/düşen takımlarla besleniyor.

**İki seçeneğin karşılaştırması:**

| | 10 yıl (2016-17'den) | Pandemi sonrası 5 yıl (2021-22'den) |
|---|---|---|
| Isınma | 2016-17 → 2020-21 | 2021-22 → 2022-23 |
| Güvenilir dönem | 2021-22 → bugün (5 sezon + güncel) | 2023-24 → bugün (~3 sezon) |
| Kalibrasyon için kupa maçı | ~2 kat | Az |
| Pandemi etkisi | Isınma dönemine düşer. 2019-20'de lig kesintiye uğradı, 2020-21 seyircisiz oynandı. Seyircisiz maçlar için ev avantajı ayrı ölçülür | Yok |
| Ek iş | Veri toplama ve takım eşleştirme ~2 kat | Daha az |

**Önerim: İkisini birleştirmek.** Hesaplama 2016-17'de sabit başlangıç puanlarıyla başlar. 2016-17 → 2020-21 ısınma ve kalibrasyon dönemi olur. Sitede gösterilen tablolar, grafikler ve test değerlendirmesi pandemi sonrası dönemi (2021-22 → bugün) kapsar. Böylece pandeminin bozduğu sezonlar gösterilmez ama puanların oturması için kullanılır. Hesaplama maliyetinde fark yok: 10 sezon ~27 bin maç, saniyeler sürer.

**Diğer kurallar:**
- Her çalıştırmada hesaplama baştan yapılır. Sonuç deterministik olur ve bir parametre değiştiğinde bütün geçmiş tutarlı biçimde yeniden hesaplanır.
- **Görünürlük:** Gösterim döneminde (2021-22 ve sonrası) profesyonel bir ligde oynamış takımlar listelenir.
- **Amatöre düşen takım:** Puanı dondurulur ve "pasif" olarak işaretlenir. Geri dönerse dondurulmuş puanı giriş seviyesine doğru çekilir ve geçici K ile başlar.

### 4.9 Doğrulama (geriye dönük test)

- Her maçta, sadece o maçtan önceki bilgiyle sonuç tahmin edilir ve tahmin hatası ölçülür (Brier skoru, log-loss).
- Galibiyet, beraberlik ve mağlubiyet olasılıkları için puan farkına dayalı bir sıralı lojistik model kurulur.
- **Kıyaslar:** (a) "her zaman ev sahibi kazanır" gibi basit bir taban, (b) Süper Lig için bahis oranları (football-data.co.uk).
- K, H, G, W, α, P, B ve seviye farkları ızgara araması (grid search) ile taranır.
- Model seçimleri de testle yapılır: Avrupa maçları dahil/hariç, Avrupa turnuva terimi var/yok, kupa bonusu var/yok.
- **Çıktı:** Parametre raporu, lig bazında puan dağılımı grafikleri ve en iyi/en kötü takım arasındaki marj.

### 4.10 Özel durumlar

| Durum | Kural |
|---|---|
| Hükmen maç | Elo'da hariç. Resmi sonuç puan cetvelinde ve bonuslarda geçerli (§9.1) |
| Ligden çekilen takım (örn. 2023 depremi sonrası) | Sahada oynanmış maçlar işlenir, oynanmayanlar hariç |
| Tarafsız saha (Süper Kupa, kupa finali, play-off finali) | H = 0 |
| Seyircisiz maç (pandemi) | Ev avantajı ayrı ölçülür |
| Ertelenen maç | Oynandığı tarihte işlenir |
| İsim, sponsor veya şehir değişikliği, birleşme | Kanonik takım tablosu (`teams.csv`: kimlik, güncel ad, eski adlar, şehir) |
| Puan silme cezası | Elo'yu etkilemez |

---

## 5. Mimari

```
                ┌──────────── GitHub Actions (zamanlanmış görev) ─────────────┐
 tff.org  ──►   │ 1. Yeni sonuçları çek (önbellekli, nazik)                    │
 UEFA kat.──►   │ 2. Normalize et (takım kimliği eşleştirme)  → data/*.csv     │
                │ 3. Elo'yu baştan hesapla                                     │
                │ 4. Statik JSON üret                         → web/public/data│
                │ 5. Next.js statik build  →  deploy                           │
                └──────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                              Cloudflare (statik site + alan adı)
```

**Sunucu yok, veritabanı yok.** Bütün site önceden üretilmiş statik dosyalardan oluşur.

### Teknoloji seçimi

| Katman | Seçim |
|---|---|
| Veri ve hesaplama | Python 3.12+, `uv`, `httpx`, `selectolax` veya BeautifulSoup, `polars`/`pandas`, `pytest` |
| Veri saklama | Repoda CSV (maçlar, takımlar). Kaynak gösterilir |
| Web | Next.js (App Router, `output: 'export'`), TypeScript, Tailwind, grafikler için Recharts veya ECharts |
| Otomasyon | GitHub Actions (public repolarda ücretsiz) |
| Yayın | Cloudflare. Faz 4'te Cloudflare'in o gün önerdiği yolu kullanacağız: Pages veya Workers statik varlıklar (Cloudflare yeni projeleri Workers'a yönlendirmeye başladı) |
| Alan adı | `.com` gibi uzantılar için Cloudflare Registrar (maliyet fiyatına satıyor, DNS aynı yerde kalıyor). `.com.tr` istenirse Türk bir kayıt firması gerekir |

**Zamanlama:** Günde bir tam çalışma. Maç günlerinin akşam saatlerinde 1–2 saatte bir kontrol.
*Not:* Public repolarda 60 gün hiç aktivite olmazsa zamanlanmış görevler otomatik kapanır. Görev kendi commit'lerini attığı için sezon içinde sorun olmaz, ama yaz arasında kontrol edilmeli.

### Üretilecek statik veri dosyaları

- `ratings/current.json`: Bütün takımlar; lig, puan, son 5 maçın toplam değişimi, 30 günlük değişim
- `teams/{id}.json`: Takımın puan geçmişi; maç maç değişimler ve **her maçın hesap dökümü** (R_ev, R_dep, H, E, K, W, G, Δ); bonus ve düzeltme satırları
- `leagues/{lig}.json`: Lig ve grup bazında Elo sıralaması
- `meta.json`: Son güncelleme zamanı, model sürümü, kullanılan parametreler, kaynaklar

### Repo yapısı

```
turkish-leagues-elo/
├── pipeline/                  # Python projesi (uv), paket adı: tlelo
│   ├── src/tlelo/
│   │   ├── http.py            # önbellekli, nazik HTTP istemcisi
│   │   ├── tff/               # TFF: sayfa seçimi, ayrıştırıcılar, Süper Kupa
│   │   ├── europe/            # Wikipedia: sayfa bulma, maç kutuları, katsayı tabloları
│   │   ├── elo/               # Elo motoru, Avrupa rakip modeli, geriye dönük test
│   │   ├── build.py           # CSV üretimi
│   │   ├── validate.py        # TFF puan cetvelleriyle karşılaştırma
│   │   └── cli.py             # uv run tlelo fetch | details | build | validate | europe-*
│   └── tests/
├── data/
│   ├── matches/               # sezon bazında yurt içi maçlar (CSV)
│   ├── europe/                # Türk takımlarının Avrupa maçları, kulüp ve ülke katsayıları
│   ├── ratings/               # model çıktısı: current.csv (history.csv repoya girmez)
│   ├── teams.csv, team_names.csv, team_seasons.csv
│   ├── sources/               # elle tutulan dosyalar: TFF sayfa envanteri, düzeltmeler, eşleştirmeler
│   └── raw/                   # ham sayfa önbelleği (repoya girmez)
├── web/                       # Next.js (Faz 3)
├── docs/                      # bu plan, Faz raporları, METODOLOJI.md
└── .github/workflows/         # update.yml (Faz 4)
```

Elo motoru ve geriye dönük test `tlelo/elo/` altında (Faz 2). Site için JSON üretimi Faz 3'te eklenecek. Veri dosyalarının sütunları için bkz. [data/README.md](../data/README.md).

## 6. Site sayfaları (ilk sürüm)

1. **Genel sıralama:** Bütün aktif takımlar. Lig filtresi, aktif/pasif filtresi, son güncelleme zamanı, haftanın en çok yükselen ve düşen takımları.
2. **Lig tabloları:** Süper Lig, 1. Lig, 2. Lig (gruplar), 3. Lig (gruplar). Elo sıralaması; isteğe bağlı olarak resmi puan durumuyla yan yana.
3. **Takım sayfası:** Puan grafiği, maç maç değişim listesi (rakip, skor, Δ), bonus ve düzeltme satırları, en yüksek ve en düşük puan. Her maç satırı açılınca o maçın hesabı adım adım görünür.
4. **Metodoloji:** Sistemin nasıl çalıştığını anlatan kamuya açık doküman (bkz. §7).

**Sonraki sürümler:** Maç önü kazanma olasılıkları, "şu maç şöyle biterse" hesaplayıcı, takım kıyaslama, İngilizce arayüz.

## 7. Kamuya açık metodoloji dokümanı

Siteyi inceleyen herkes puanların nasıl hesaplandığını açıkça görüp anlayabilmeli.

- **Tek kaynak:** `docs/METODOLOJI.md` dosyası. Sitedeki `/metodoloji` sayfası bu dosyadan üretilir. Böylece repo ve site birbirinden farklılaşmaz.
- **Dil:** Teknik olmayan okuyucu için yazılır. Formüller yanında düz Türkçe açıklama ve gerçek maç örnekleri bulunur.
- **İçerik:**
  1. Elo nedir? (bir paragraf, futbolsever diliyle)
  2. Formül ve sembollerin anlamı
  3. Gerçek bir maç üzerinden adım adım hesap
  4. Ev avantajı, gol farkı ve turnuva ağırlıkları
  5. Yükselme/düşme düzeltmesi, kupa bonusu, sezon arası ortalamaya çekme
  6. Avrupa ve amatör takımlarla oynanan maçlar nasıl işleniyor
  7. Başlangıç puanları ve ısınma dönemi
  8. Parametreler nasıl seçildi (test sonuçları ve tahmin başarısı)
  9. Sınırlamalar (Elo neyi ölçmez: sakatlıklar, transferler, teknik direktör değişiklikleri…)
  10. Kendin hesapla: repoyu klonlayıp tek komutla aynı puanları üretme
  11. Sürüm geçmişi: Bir parametre değiştiğinde tarih, ne değiştiği ve neden
  12. Veri kaynakları ve atıflar
- **Model sürümü:** Her parametre değişikliği yeni bir model sürümüdür (`v1.0`, `v1.1`…). Sitede hangi sürümle hesaplandığı yazar.

## 8. Yol haritası

| Faz | İçerik | Tamamlanma ölçütü |
|---|---|---|
| **0. Keşif** ✅ | Kalan kararları netleştirmek. TFF'den her ligin bir sezonunu ve bir kupa sezonunu deneme amaçlı çekmek. 2016-17'ye kadar arşivin eksiksiz olduğunu doğrulamak. ClubElo erişimini ve koşullarını doğrulamak | **Tamamlandı (14 Kasım 2026).** Bkz. [faz-0-kesif.md](faz-0-kesif.md) |
| **1a. Veri katmanı: yurt içi** ✅ | Repo iskeleti, veri şeması, TFF kazıyıcısı (lig, play-off, kupa, Süper Kupa), takım kimlik tablosu, veri kalite testleri | 2016-17'den bugüne bütün yurt içi maçlar normalize CSV'de; puan durumları TFF ile tutarlı |
| **1b. Veri katmanı: Avrupa** ✅ | Türk takımlarının Avrupa maçları (Wikipedia, openfootball ile çapraz doğrulama), UEFA kulüp ve ülke katsayı tabloları, yabancı kulüp ad eşleştirmesi | 2016-17'den bugüne Türk takımlarının bütün Avrupa maçları CSV'de, rakiplerin katsayısı eşleşmiş |
| **2. Elo motoru ve test** ✅ | Motor ve birim testleri, geriye dönük test, parametre taraması, dağılım raporu, `METODOLOJI.md` ilk taslağı | **Tamamlandı (14 Kasım 2026).** Model v1.0, kontrol sezonlarında log-loss 0,980 (taban 1,074). Bkz. [faz-2-rapor.md](faz-2-rapor.md) |
| **3. Web sitesi** | Next.js statik site, 4 sayfa, maç hesap dökümü, mobil uyum | Yerelde bütün sayfalar gerçek veriyle çalışıyor |
| **4. Otomasyon ve yayın** | GitHub Actions zamanlanmış görevi, Cloudflare kurulumu (adım adım), alan adı, hata bildirimi | Site kendi alan adında yayında ve kendi kendine güncelleniyor |
| **5. Ek özellikler** | Tahminler, hesaplayıcı, İngilizce, indirilebilir veri | — |

## 9. Kararlar

### 9.1 Alınan kararlar (14 Kasım 2026)

| Konu | Karar |
|---|---|
| Veri kaynağı | TFF, kaynak gösterilerek |
| Güncelleme | Maçlar sonuçlandıktan bir süre sonra. Dakika dakika canlı güncelleme yok |
| Başlangıç puanları | Hesaplama döneminin ilk sezonunda lig seviyesine göre sabit puan; sonra bugüne kadar simülasyon (§4.4) |
| Ligler arası kalibrasyon | Seviye başlangıç puanı + ısınma dönemi + kupa maçlarıyla kalibrasyon (§4.4) |
| Beklenen marj | ~700–900 puan kabul edilebilir. Veri işlendiğinde tekrar bakılacak |
| Ölçek | Okunabilir aralık, kabaca 700–2000 (§4.5) |
| Yükselme/düşme | Lig seviyesine göre puan eklenir/düşülür (§4.6) |
| Kupa başarısı | Türkiye Kupası ve Süper Kupa şampiyonuna bonus (§4.6) |
| Avrupa kupaları | Sadece Türk takımının puanı değişir. Rakibin puanı UEFA kulüp katsayısından türetilir (§4.7) |
| BAL takımları | Sabit puan (§4.7) |
| Hükmen maçlar | Elo'da hariç: iki takımın da puanı değişmez. Resmi sonuç puan cetvelinde, yükselme/düşme ve kupa bonuslarında geçerli. Tek maçlık disiplin kararlarını en küçük farkla (1-0) sayan ara seçenek ileride yeniden değerlendirilecek |
| Yayın | Cloudflare + alan adı |
| Metodoloji | Kamuya açık, okuyucu dostu doküman ve sitede ayrı sayfa (§7) |
| Hesaplama ve gösterim dönemi | 2016-17'den hesaplanır, 2021-22'den itibaren gösterilir (§4.8) |
| P ve B'nin değerleri (Faz 2) | Plandaki değerler korundu. Test ikisinin de tahmini bozmadığını gösterdi (§4.6) |
| Gol farkı (Faz 2) | Var. Kaldırmak tahmini belirgin biçimde kötüleştiriyor |
| Sezon arası ortalamaya çekme (Faz 2) | Var, α = 0,30. Testte plandaki 0,10'dan daha iyi |
| Penaltılar | Beraberlik. Uzatmada 120 dakikanın sonucu |
| Ham maç verisi | Repoda, kaynak gösterilerek |
| Avrupa'da turnuva seviyesi (Faz 2) | Ayrı terim yok. Testte bir katkısı çıkmadı (p = 0,91); seviye rakibin katsayısından geliyor (§4.7) |
| Lig sıralaması bonusu (Faz 2) | Yok. Süper Lig şampiyonluk bonusu testte tahmine bir şey katmadı. Başarılar sitede rozet olarak gösterilir |

### 9.2 Karar bekleyenler

Aksi belirtilmedikçe önerilen seçenekle ilerlenecek.

| # | Karar | Seçenekler | Önerim |
|---|---|---|---|
| 2 | Görünürlük | — | Gösterim döneminde (2021-22 ve sonrası) profesyonel ligde oynamış takımlar |
| 8 | Puan değişimini gösterme şekli | Maç maç / toplam +/− | **İkisi birden** |
| 10 | Lisans | — | Kod: **MIT**. Üretilen puan verisi: **CC BY-NC 4.0** (TFF'nin ticari olmayan kullanım şartıyla uyumlu) |
| 11 | Dil | — | Arayüz ve dokümanlar Türkçe, kod İngilizce |
| 12 | Proje/site adı ve alan adı | — | Sende |

## 10. Riskler

| Risk | Önlem |
|---|---|
| TFF sitesinin yapısı değişir, kazıyıcı bozulur | Kazıyıcı için testler, Actions hata bildirimi. Bozulursa site son geçerli veriyle yayında kalır |
| 2016-17 sonrası alt lig verisinde eksik veya hata | Faz 0'da doğrulama, puan durumlarıyla otomatik tutarlılık kontrolü |
| Takım kimliği eşleştirme hataları | Kanonik takım tablosu, elle gözden geçirilen eşleme listesi, testler |
| ClubElo'ya erişilemiyor (**gerçekleşti**, Eylül 2026) | Ana yöntem UEFA kulüp katsayısına geçti |
| Wikipedia'da hatalı veya vandalize edilmiş bir skor | Tutarlılık kontrolleri (grup maç sayısı, iki ayaklı eşleşmeler), openfootball ile çapraz doğrulama. Güncel sezon sayfaları her güncellemede yeniden çekilir |
| Wikipedia sayfa yapısı değişir | Ayrıştırıcı testleri gerçek sayfa yapısından örneklerle yazıldı. `tlelo europe-check` boşlukları raporlar |
| Bonuslar ve düzeltmeler tahmin başarısını bozar | Testte ölçülür, değerleri ona göre ayarlanır |
| TFF ve Wikipedia sunucularına gereksiz yük bindirmek | Düşük sıklık, önbellek, istekler arasında 2 saniye, sadece değişen sayfaları çekmek. robots.txt kurallarına uyulur |
