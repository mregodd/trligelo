# Veri

Bu klasördeki CSV dosyaları `pipeline/` içindeki kodla üretilir. Elle düzenlenmez; istisnalar aşağıda belirtilmiştir.

**Kaynaklar:**
- Yurt içi maç sonuçları [Türkiye Futbol Federasyonu (tff.org)](https://www.tff.org) sayfalarından derlenmiştir. TFF'nin kullanım şartları gereği kaynak gösterilerek ve **ticari olmayan amaçla** yayımlanır.
- Avrupa kupası maçları ve UEFA katsayıları İngilizce [Wikipedia](https://en.wikipedia.org)'nın UEFA turnuva sayfalarından derlenmiştir ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). Her maçın hangi sayfadan alındığı `source` sütununda yazar.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `matches/<sezon>.csv` | O sezonun bütün maçları: Süper Lig, 1. Lig, 2. Lig, 3. Lig (play-off'lar dahil), Ziraat Türkiye Kupası, Süper Kupa |
| `teams.csv` | Kulüp başına bir satır. Kimlik, TFF'deki en son adı, ilk ve son görüldüğü sezon, profesyonel ligde geçirdiği sezon sayısı |
| `team_names.csv` | Kulübün her sezonki adı. Sponsor adları değiştiği için eşleştirmede kullanılır |
| `team_seasons.csv` | Kulübün her sezon hangi ligde ve grupta oynadığı. Bu dosyada olmayan kulüpler o sezon amatördü (PGL/BAL) |
| `sources/tff_pages.csv` | Hangi sezonun hangi TFF sayfasında olduğu (elle tutulur) |
| `sources/supercup_extra.csv` | TFF'de maç kimliği bulunamayan Süper Kupa maçları. Elle, kaynağıyla birlikte girilir |
| `sources/match_overrides.csv` | Fikstürde skoru olmayan ama TFF puan cetvelinin saydığı maçlar (disiplin kararıyla hükmen sayılanlar). Elle, açıklamasıyla girilir |
| `europe/matches.csv` | Türk takımlarının UEFA turnuvalarındaki bütün maçları (Şampiyonlar Ligi, Avrupa Ligi, Konferans Ligi, ön elemeler dahil) |
| `europe/coefficients.csv` | Her sezonun çekiliş tablolarındaki UEFA kulüp katsayıları. Türk takımlarının rakiplerinden çok daha fazla kulüp içerir |
| `europe/association_coefficients.csv` | Her sezonun ülke (federasyon) katsayı sıralaması. Kulüp katsayısı bulunamayan rakipler için yedek |
| `sources/europe_tr_clubs.csv` | Türk kulübünün Wikipedia sayfası ile TFF `kulupID` eşleştirmesi (elle tutulur) |
| `sources/team_display_names.csv` | Sitede gösterilen kulüp adları: sponsor adı taşıyan kulüpler için taraftarın kullandığı ad (örn. EKENLER BETON SİVASSPOR → Sivasspor). Elle tutulur; listede olmayan kulüplerin adı TFF adından şirket ekleri atılarak üretilir. `mask` = 1 olan kulüp sitede yalnızca bu adla görünür: TFF'deki adı ve logosu gösterilmez, aramada çıkmaz |
| `ratings/current.csv` | Model çıktısı: güncel sezonun takımları, Elo puanı sırasıyla (`uv run tlelo elo`) |
| `ratings/history.csv` | Model çıktısı: her takımın her puan değişikliği (maçlar, yükselme/düşme, ortalamaya çekme, bonuslar, ölçek kayması). ~6 MB, **repoya girmez**, aynı komutla üretilir |
| `raw/` | İndirilen ham sayfaların önbelleği (`raw/tff/`, `raw/wikipedia/`; kulüp sayfaları ve logolar `raw/tff/clubs/`, `raw/tff/logos/`). **Repoya girmez** (`.gitignore`) |

## `matches/<sezon>.csv` sütunları

| Sütun | Açıklama |
|---|---|
| `match_id` | TFF maç kimliği (`https://www.tff.org/Default.aspx?pageID=29&macId=<id>`). Negatif kimlikler elle girilmiş maçlardır |
| `season` | Sezon, örn. `2016-17` |
| `competition` | `SL`, `1L`, `2L`, `3L`, `TK` (Türkiye Kupası), `SK` (Süper Kupa) |
| `stage` | `league` (lig maçı), `playoff` (lig play-off'u), `cup` (kupa maçı) |
| `round` | Kupa veya play-off turu, TFF'deki adıyla ("Yarı Final", "3.Tur", "Grup") |
| `group` | Grup adı ("Beyaz", "Kırmızı", "01", "A"). Grupsuz liglerde boş |
| `week` | Lig haftası |
| `date`, `time` | Maç tarihi ve başlama saati. Hükmen maçlarda saat genellikle boştur |
| `home_id`, `home_name` | Ev sahibi kulübün TFF kimliği (`kulupID`) ve o sezonki adı |
| `away_id`, `away_name` | Deplasman takımı |
| `home_goals`, `away_goals` | Normal süre skoru |
| `et_home`, `et_away` | Uzatmalar sonrası skor (varsa) |
| `pen_home`, `pen_away` | Penaltı atışları (varsa) |
| `status` | `played` (oynandı), `forfeit` (hükmen), `double_forfeit` (iki takım da 0-3 hükmen mağlup; skor boş), `not_played` (oynanmadı: pandemide yarıda kalan sezon, sonradan başka kimlikle tekrar oynanan maç vb.) |
| `venue_id`, `venue` | Stat (sadece detay sayfası çekilen maçlarda: play-off'lar, finaller, hükmen kontrolü yapılanlar) |

**Kulüp kimliği:** TFF her kulübe değişmeyen bir `kulupID` verir. Sponsor adı değişse de kimlik aynı kalır. Örneğin "ATİKER KONYASPOR" (2016-17) ve "TÜMOSAN KONYASPOR" (2026-27) ikisi de `3600`.

**Hükmen tespiti:** TFF fikstürde hükmen sonuçları normal skor gibi gösterir. 3-0 veya 0-3 biten her maçın detay sayfasına bakılır. Hakem ataması yoksa maç `forfeit` olarak işaretlenir. Bazı maçlar ise sahada yarıda kalıp sonradan disiplin kararıyla sonuçlanır. TFF bunları fikstürde skorsuz bırakır ama puan cetveline işler. Bunlar `tlelo validate` ile bulunur ve `sources/match_overrides.csv` dosyasına elle eklenir.

## `europe/matches.csv` sütunları

Yabancı kulüpler İngilizce Wikipedia sayfa adıyla tanımlanır (örn. `S.L. Benfica`), Türk kulüpleri ayrıca TFF `kulupID` ile (`team_id`).

| Sütun | Açıklama |
|---|---|
| `match_id` | UEFA'nın maç kimliği (uefa.com rapor bağlantısından). 2022-23'ten sonraki sayfalarda bu bağlantı olmadığı için çoğu yeni maçta boştur |
| `season`, `competition` | Sezon ve turnuva: `UCL` (Şampiyonlar Ligi), `UEL` (Avrupa Ligi), `UECL` (Konferans Ligi) |
| `round` | `PR` ön eleme turu, `Q1`–`Q3` eleme turları, `PO` play-off turu, `GS` grup aşaması, `LP` lig aşaması (2024-25'ten itibaren), `KPO` eleme play-off'u, `R32`, `R16`, `QF`, `SF`, `F` |
| `group`, `leg` | Grup harfi. İki ayaklı eşleşmelerde 1. veya 2. maç |
| `date`, `time` | Tarih ve yerel başlama saati |
| `home_team`, `home_name`, `home_assoc` | Ev sahibinin Wikipedia sayfası, görünen adı ve ülke federasyonu (`away_*` deplasman için aynı) |
| `team_id`, `tr_home` | Türk kulübünün `kulupID`'si. `tr_home` = 1 ise Türk kulübü ev sahibi |
| `opponent`, `opponent_coefficient` | Rakibin Wikipedia sayfası ve o sezonki UEFA kulüp katsayısı |
| `home_goals`, `away_goals` | 90 dakika skoru. Uzatmaya giden maçlarda gol dakikalarından hesaplanır |
| `et_home`, `et_away`, `pen_home`, `pen_away` | Uzatmalar sonrası skor ve penaltı atışları (varsa) |
| `status` | `played`, `forfeit`, `not_played` (güncel sezonun oynanmamış maçları) |
| `venue`, `source` | Stat ve verinin alındığı Wikipedia sayfası |

**Doğrulama:** `tlelo europe-check` şunları kontrol eder:
- Grup aşamasında her kulübün 6, lig aşamasında 8 maçı (Konferans Ligi'nde 6) olmalı.
- İki ayaklı eşleşmelerin iki maçı da bulunmalı. Pandemide tek maç oynanan turlar istisna.
- Her rakibin kulüp ve ülke katsayısı bulunmalı.

[openfootball](https://github.com/openfootball/champions-league) (CC0) ile çapraz doğrulandı. openfootball'daki 202 Türk takımı maçının 201'i skoruyla birebir aynı. Kalan maç PSG–Başakşehir (2020): yarıda kalıp ertesi gün tamamlanmış, tarihler farklı ama skor aynı.

## Yeniden üretmek

```bash
cd pipeline
uv run tlelo fetch          # TFF sayfalarını indirir (önbellekte olanları atlar)
uv run tlelo details        # hükmen kontrolü ve stat için maç detayları
uv run tlelo build          # yurt içi CSV'leri yazar
uv run tlelo validate       # TFF puan cetvelleriyle karşılaştırır
uv run tlelo europe-fetch   # Wikipedia'daki UEFA turnuva sayfalarını indirir
uv run tlelo europe-build   # europe/ CSV'lerini yazar
uv run tlelo europe-check   # Avrupa verisindeki boşlukları raporlar
uv run tlelo elo            # puanları hesaplar (model v1.0), ratings/ klasörüne yazar
uv run tlelo backtest       # docs/backtest.md test raporunu yeniden üretir
uv run tlelo logos          # sitedeki kulüplerin logolarını TFF'deki kulüp sayfalarından indirir (~12 dakika, bir kez)
uv run tlelo site           # web sitesinin verisini web/src/data/ klasörüne yazar, logoları web/public/logos/ klasörüne kopyalar
```

İlk TFF indirmesi yaklaşık 3–3,5 saat, Wikipedia indirmesi yaklaşık 5 dakika sürer. Sunuculara yük olmamak için istekler arasında 2 saniye beklenir. Wikipedia'da sadece robots.txt'nin izin verdiği makale sayfaları (`/wiki/`) okunur. Sonraki çalıştırmalar sadece eksik ya da değişen sayfaları indirir.
