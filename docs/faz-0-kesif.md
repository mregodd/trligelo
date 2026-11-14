# Faz 0 — Keşif Raporu

> **Tarih:** 14 Kasım 2026
> **Amaç:** Veri kaynaklarına erişimi doğrulamak, 2016-17'den bugüne arşivin eksiksiz olup olmadığını görmek ve Faz 1'e (veri katmanı) girdi hazırlamak.
> Bağlam için bkz. [PLAN.md](PLAN.md).

## Özet

| Durum | Bulgu |
|---|---|
| ✅ | **TFF arşivi 2016-17'den bugüne eksiksiz.** Dört lig ve Türkiye Kupası için her sezonun kendi sayfası var. Maç sayıları beklenen değerlerle örtüşüyor (§2). |
| ✅ | **Takım kimliği sorunu büyük ölçüde çözülüyor.** TFF her kulübe kalıcı bir `kulupID` veriyor. Sponsor adı değişse de kimlik değişmiyor. Örneğin Konyaspor 2016-17'de "ATİKER KONYASPOR", bugün "TÜMOSAN KONYASPOR" adıyla geçiyor, ikisinin de kimliği `3600`. |
| ✅ | **Süper Kupa:** Bütün finaller tarihçe sayfasında; stat, penaltı ve hükmen bilgisiyle birlikte. Yılda bir iki maç olduğu için veriyi elle tutacağız. |
| ⚠️ | **Lig maçlarının tarihleri** sezon sayfasındaki fikstürde yok. Haftalık görünümden çekilmeleri gerekiyor. Tek seferlik ~2.800 istek demek, nazik hızda ~2–2,5 saat (§4). |
| ⚠️ | **Hükmen maçların** fikstürde bir işareti yok, 3-0 normal bir skor gibi görünüyor. Bunları güvenilir biçimde ayırmanın bir yolu var (§3.3). |
| ⚠️ | **Avrupa maç sonuçları** TFF'de yapılandırılmış biçimde yok, sadece haber akışı var. openfootball (CC0) kısmen kapsıyor (§5). |
| ❌ | **ClubElo kullanılamıyor.** API'si 1 Eylül 2026'dan beri her istekte 502 veriyor, site de Cloudflare bot korumasının arkasında. **Alınmış bir kararın yeniden ele alınması gerekiyor** (§6). |
| ℹ️ | BAL'ın yeni adı **"Profesyonelliğe Geçiş Ligi" (PGL)**. Amatör bir lig, kapsamımızın dışında. |
| ℹ️ | Bu makinede Python ve Node kurulu değil. Faz 1'den önce kurulum gerekiyor (§7). |

---

## 1. TFF sayfa envanteri

### 1.1 Sezon sayfaları (`pageID`)

| Sezon | Süper Lig | 1. Lig | 2. Lig | 3. Lig | Türkiye Kupası |
|---|---|---|---|---|---|
| 2016-17 | 1413 | 1414 | 1415 | 1416 | 1425 |
| 2017-18 | 1440 | 1441 | 1443 | 1442 | 1463 |
| 2018-19 | 1467 | 1469 | 1470 | 1471 | 1487 |
| 2019-20 | 1501 | 1502 | 1505 | 1506 | 1517 |
| 2020-21 | 1529 | 1530 | 1531 | 1532 | 1540 |
| 2021-22 | 1576 | 1580 | 1579 | 1577 | 1578 |
| 2022-23 | 1628 | 1629 | 1632 | 1633 | 1634 |
| 2023-24 | 1648 | 1649 | 1650 | 1651 | 1666 |
| 2024-25 | 1730 | 1731 | 1732 | 1733 | 1734 |
| 2025-26 | 1768 | 1772 | 1769 | 1770 | 1771 |
| 2026-27 (güncel) | 198 | 142 | 976 | 971 | 598 |

Diğer sayfalar: Süper Kupa tarihçesi `412`, Avrupa kupaları `593`, lig arşivleri `545` / `563` / `371` / `376`, Türkiye Kupası arşivi `411`.

### 1.2 Adres kalıpları

| Kalıp | İçerik |
|---|---|
| `default.aspx?pageID={sezon}` | Tam fikstür (hafta, ev, deplasman, skor, kulüp ve maç kimliği), puan cetveli, play-off maçları. Gruplu liglerde varsayılan olarak ilk grup gösteriliyor |
| `…&grupID={grup}` | Belirli bir grubun fikstürü |
| `…&grupID={grup}&hafta={n}` | O haftanın maçları, **tarih ve saatleriyle** |
| `Default.aspx?pageId=29&macId={maç}` | Maç detayı: stat, hakemler, kadrolar |
| `Default.aspx?pageID=28&kulupID={kulüp}` | Kulüp sayfası. `kulupID` kalıcı |

### 1.3 Teknik notlar

- **Karakter kodlaması:** Sayfalar `windows-1254`. Okurken UTF-8'e çevrilmeli.
- **robots.txt** yok (404). Kullanım Şartları kaynak gösterilerek ve ticari olmayan amaçla yayına izin veriyor.
- Site bir CDN arkasında (önbellek süresi 120 sn). Bot koruması ile karşılaşmadık.
- Sayfalar büyük: sezon sayfası 0,4–1,1 MB.

## 2. Kapsam doğrulaması

Her sezon sayfasındaki tekil maç kimliği sayısı (play-off'lar dahil):

| Sezon | Süper Lig | 1. Lig | 2. Lig | 3. Lig | Türkiye Kupası |
|---|---|---|---|---|---|
| 2016-17 | 306 | 311 | 625 | 969 | 243 |
| 2017-18 | 306 | 311 | 625 | 933 | 189 |
| 2018-19 | 306 | 312 | 625 | 899 | 195 |
| 2019-20 | 306 | 311 | 619 ¹ | 893 ¹ | 189 |
| 2020-21 | 420 ² | 311 | 735 | 1.082 | 144 |
| 2021-22 | 380 | 347 | 735 ³ | 969 | 133 |
| 2022-23 | 342 ⁴ | 347 | 735 | 899 | 149 |
| 2023-24 | 380 | 311 | 697 | 866 | 165 |
| 2024-25 | 342 | 385 | 625 | 986 | 141 |
| 2025-26 | 306 | 385 | 658 | 986 | 142 |
| 2026-27 (devam ediyor) | 306 (99 oynandı) | 380 (139) | 578 (170) | 918 (296) | 114 |

1. Pandemi yüzünden sezon yarıda kesildi. 2. Lig'de ~108, 3. Lig'de ~157 maç oynanmadı.
2. Süper Lig 2020-21'de 21 takımla oynandı (42 hafta).
3. 36 maçın skoru yok. Büyük ihtimalle ligden çekilen bir takım. Faz 1'de incelenecek.
4. Depremden sonra çekilen Hatayspor ve Gaziantep FK'nin kalan maçları hükmen 3-0 olarak kayıtlı.

**Toplam:** 10 tamamlanmış sezonda ~24.500 maç. Güncel sezonda şu ana kadar ~800 maç oynandı.

**Grup yapısı değişiyor:** 2. Lig her sezon 2 grup. 3. Lig sezona göre 3 veya 4 grup (2020-21 ve 2023-24 → 2025-26 arası 4 grup). Takım sayıları da sezondan sezona değişiyor. Bu bilgiler sabit kodlanmamalı, her sezon sayfadan okunmalı.

## 3. Veri biçimi bulguları

### 3.1 Lig maçları
- **Tam fikstür:** Hafta numarası, ev sahibi ve deplasman (o sezonki adı + `kulupID`), skor, `macId`. Tarih yok.
- **Haftalık görünüm:** `gg.aa.yyyy` biçiminde tarih ve `ss:dd` biçiminde saat.

### 3.2 Play-off ve kupa maçları
- Tur adı ("Ön Eleme", "1.Tur", "A Grubu", "Son 16", "Çeyrek Final", "Yarı Final", "Final").
- Uzun biçimli tarih: "14 Mayıs 2017 15:00".
- Skor 90 dakikanın sonucu. Ek bilgiler ayrı yazılıyor: `(Uzt. 2-1)` uzatmalar sonrası, `(Pen. 1-4)` penaltılar.
- Türkiye Kupası'nın ilk turlarında amatör takımlar da oynuyor. Bir takımın amatör olup olmadığını, o sezon profesyonel bir ligde oynayıp oynamadığına bakarak anlayacağız.
- Kupa formatı sezona göre değişiyor: 2016-17'de 8 grup vardı, 2024-25 ve 2025-26'da da grup aşaması var.

### 3.3 Hükmen maçlar

Fikstürde ve haftalık görünümde hükmen maçların bir işareti yok. Ancak iki fark var:
- Haftalık görünümde hükmen maçın **başlama saati boş** (örnek: 19.04.2023, Beşiktaş 3-0 Hatayspor).
- Maç detay sayfasında **hakem ve kadro bilgisi yok**. Normal maçlarda ikisi de var.

**Tespit kuralı:** Skor 3-0 veya 0-3 ve saat boşsa, detay sayfası çekilir. Hakem bilgisi yoksa maç hükmen sayılır. Böylece sadece şüpheli maçlar için ek istek yapılır.

Süper Kupa sayfasında ise hükmen açıkça yazıyor: "3-0 (HÜKMEN)" (7 Nisan 2024).

### 3.4 Tarafsız saha
Maç detay sayfasında stat adı var. Tarafsız saha olma ihtimali olan maçlar için (kupa finali, play-off finalleri, Süper Kupa) sadece bu maçların detayı çekilir.

## 4. İstek bütçesi

| İş | İstek sayısı | Süre (2,5 sn arayla) |
|---|---|---|
| Sezon ve grup sayfaları | ~150 | ~6 dk |
| Haftalık görünümler (tarihler için) | ~2.800 | ~2 saat |
| Maç detayları (hükmen şüphelileri, finaller) | ~300–500 | ~20 dk |
| **Tek seferlik toplam** | **~3.300–3.500** | **~2,5 saat** |
| Güncelleme başına (sadece güncel haftalar) | ~15–25 | ~1 dk |

Ham sayfalar bir kez indirilip önbelleğe alınır (repoya girmez). Repoya sadece işlenmiş CSV'ler girer.

## 5. Avrupa kupaları: maç sonuçları

> **Güncelleme (Faz 1b):** Wikipedia birincil kaynak oldu. Çünkü maç kutularıyla birlikte çekiliş tablolarındaki kulüp katsayılarını da veriyor ve bütün sezonları kapsıyor. openfootball çapraz doğrulama için kullanıldı: 202 ortak maçın 201'i birebir aynı. Bkz. [PLAN.md §3](PLAN.md).

| Kaynak | Kapsam | Lisans | Not |
|---|---|---|---|
| TFF `pageID=593` | Güncel sezon, haber başlıkları ("Celtic 3-2 Beşiktaş") | Kaynak gösterilerek | Yapılandırılmış değil. Kadın takımlarının maçları da aynı akışta |
| openfootball/champions-league | Şampiyonlar Ligi: bütün sezonlar. Avrupa Ligi: 2020-21 ve sonrası. Konferans Ligi: 2021-22 ve sonrası. Ön elemeler: sadece 2024-25 ve 2025-26 | CC0 | 2025-26'nın Avrupa Ligi ve Konferans Ligi ana tur dosyaları henüz yok. Güncellemeler düzensiz |
| Wikipedia turnuva sayfaları | Bütün turnuvalar, ön elemeler dahil | CC BY-SA | Boşlukları doldurmak için |

**Öneri:**
- **Geçmiş sezonlar:** openfootball'u temel al, eksikleri Wikipedia'dan tamamla. Bir sezonda Türk takımlarının ~40–60 Avrupa maçı oluyor, 10 sezonda ~450–500 maç. openfootball bunların 202'sini içeriyor. Eksiklerin çoğu ön eleme maçları (2024 öncesi) ve 2020 öncesinin Avrupa Ligi maçları.
- **Güncel sezon:** Avrupa haftalarında 3–6 maç oynanıyor. Küçük bir CSV, yarı otomatik güncellenir: TFF haber başlıklarından öneri üretilir, kontrol edildikten sonra eklenir.

## 6. ClubElo durumu ve alternatif

**Bulgular:**
- `api.clubelo.com` her adres için 502 dönüyor. Geliştirici raporlarına göre bu durum 1 Eylül 2026'dan beri sürüyor. API'nin kimlik doğrulama arkasına taşındığı ya da kapatıldığı konuşuluyor. Resmi bir açıklama bulamadık.
- `clubelo.com` Cloudflare bot korumasıyla 403 dönüyor. Bu korumayı aşmaya çalışmayacağız.

> **Güncelleme (Faz 1b):** kassiesa.net'in robots.txt dosyası bütün otomatik istemcileri engelliyor (`User-agent: *`, `Disallow: /`). Faz 0'da bu gözden kaçmıştı. Site kullanılmıyor. Katsayılar Wikipedia'daki çekiliş tablolarından alınıyor.

**Alternatif A (öneri): UEFA kulüp katsayısı.**
- UEFA'nın 5 sezonluk kulüp katsayıları her sezon için yayımlanıyor. kassiesa.net'teki 2026 tablosunda ~410 kulüp var, Türk takımları da içinde.
- Yabancı rakibin puanı katsayısından türetilir: `R = a + b × ln(1 + katsayı puanı)`.
- a ve b, Türk takımlarının ~500 Avrupa maçının sonuçlarını en iyi açıklayacak şekilde veriden hesaplanır.
- Tabloda bulunmayan kulüplere ülke katsayısına göre bir puan bandı atanır.
- Sadece Türk takımının puanı değişir. Bu ilke aynen korunur.
- Eksi yanı: Katsayı yavaş değişir ve rakibin o haftaki formunu yansıtmaz. Ancak sezonda ~50 maç için bu kabul edilebilir.
- Bütün sezonların tabloları mevcut. 2017 ve öncesi `method4/trankYYYY.html`, 2018 ve sonrası `method5/trankYYYY.html` adresinde.

**Maliyet:**

| Kalem | Tek seferlik | Sonra |
|---|---|---|
| Katsayı tabloları (kulüp + ülke, 11 sezon) | ~22 istek, ~1 dk, ~250 KB CSV | Sezonda 2 istek |
| Katsayıyı puana çeviren formülün (a, b) hesabı | ~450 maç ve 2 parametre. Milisaniyeler sürer | Her hesaplamada yeniden yapılır, fark edilmez |
| Parametre taramasına etkisi | Her denemede a ve b yeniden hesaplanır. Toplam süreye etkisi %1'in altında | — |
| Para | 0 | 0 |
| **Asıl maliyet: işçilik** | Katsayı tablosu ayrıştırıcısı (~yarım gün). Yabancı kulüp adı eşleştirme (~yarım gün) | Yeni rakip geldikçe eşleştirme tablosuna bir satır |

- **Ad eşleştirme:** openfootball'da 10 sezonda 34 ülkeden 84 farklı rakip var. Eksikler tamamlanınca bu sayı tahminen 150–200'e çıkar. Ülke kodu ve benzer ad eşleştirmesiyle çoğu otomatik bulunur. Bulunamayanlar o sezon ülke katsayısı bandını kullanır, yani hiçbir maç işlenmeden kalmaz. Eşleştirme tablosu zamanla elle iyileştirilir.
- **Not:** Avrupa maç sonuçlarını toplama işi (openfootball + Wikipedia, ~1 gün) hangi yöntem seçilirse seçilsin gerekiyor; ClubElo çalışsaydı da gerekecekti. Katsayı yönteminin getirdiği ek iş yaklaşık 1 gün.

**Alternatif B: Kendi küçük Avrupa Elo'muz.** Bütün Avrupa kupası maçlarından (openfootball) yabancı kulüpler için ayrı bir Elo hesaplanır. Daha isabetli olabilir ama veri boşlukları büyük (ön elemeler 2024 öncesinde yok) ve işçiliği çok daha fazla.

**Alternatif C: ClubElo'nun geri dönmesini beklemek.** Belirsiz. Gelirse A'nın yerine ya da yanına eklenebilir.

## 7. Geliştirme ortamı

Bu makinede Python, `uv` ve Node kurulu değil. Faz 0 keşfi Git ile gelen `curl` ve `perl` araçlarıyla yapıldı.

Faz 1 için gerekenler:
- **uv:** Python sürümünü de kendisi yönetir.
- **Node LTS:** Faz 3'te (web sitesi) gerekir.

Önerilen kurulum yöntemi `winget` (Windows'un resmi paket yöneticisi). Kurulum senin onayınla yapılacak.

## 8. Faz 1 için girdiler

1. **Kazıyıcı iki katmanlı olmalı:** İndirme (önbellekli, hız sınırlı) ve ayrıştırma (çevrimdışı, test edilebilir) ayrı tutulur. Ham HTML `data/raw/` altında önbelleğe alınır ve `.gitignore`'a eklenir.
2. **Testler gerçek sayfalardan alınmış örneklerle yazılmalı:** Normal maç, hükmen, uzatma, penaltı, pandemide oynanmamış maç, gruplu lig.
3. **`teams.csv`:** Birincil anahtar TFF `kulupID`. Her sezonun adı ayrı tutulur.
4. **Sezon, lig ve grup yapısı** sabit kodlanmaz, sayfadan okunur. §1.1'deki tablo `data/sources/tff_pages.csv` dosyasına yazılır.
5. **Hükmen tespiti:** §3.3'teki kural.
6. **Doğrulama:** Ayrıştırılan maçlardan hesaplanan puan durumu, TFF'nin puan cetveliyle karşılaştırılır.
7. **Çekilen takımlar:** 2. Lig 2021-22'deki skorsuz 36 maç incelenir.
8. **Avrupa:** openfootball dosyaları indirilir, boşlukların listesi çıkarılır.

## Kaynaklar

- TFF: https://www.tff.org (Kullanım Şartları: `pageID=179`)
- openfootball/champions-league (CC0): https://github.com/openfootball/champions-league
- UEFA kulüp katsayıları (Bert Kassies): https://kassiesa.net/uefa/
- ClubElo API'sinin durumuyla ilgili geliştirici raporları: https://github.com/probberechts/soccerdata/issues/977
