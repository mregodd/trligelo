# Veri

Bu klasördeki CSV dosyaları `pipeline/` içindeki kodla üretilir. Elle düzenlenmez; istisnalar aşağıda belirtilmiştir.

**Kaynak:** Maç sonuçları [Türkiye Futbol Federasyonu (tff.org)](https://www.tff.org) sayfalarından derlenmiştir. TFF'nin kullanım şartları gereği kaynak gösterilerek ve **ticari olmayan amaçla** yayımlanır.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `matches/<sezon>.csv` | O sezonun bütün maçları: Süper Lig, 1. Lig, 2. Lig, 3. Lig (play-off'lar dahil), Ziraat Türkiye Kupası, Süper Kupa |
| `teams.csv` | Kulüp başına bir satır. Kimlik, TFF'deki en son adı, ilk ve son görüldüğü sezon, profesyonel ligde geçirdiği sezon sayısı |
| `team_names.csv` | Kulübün her sezonki adı. Sponsor adları değiştiği için eşleştirmede kullanılır |
| `team_seasons.csv` | Kulübün her sezon hangi ligde ve grupta oynadığı. Bu dosyada olmayan kulüpler o sezon amatördü (PGL/BAL) |
| `sources/tff_pages.csv` | Hangi sezonun hangi TFF sayfasında olduğu (elle tutulur) |
| `sources/supercup_extra.csv` | TFF'de maç kimliği bulunamayan Süper Kupa maçları. Elle, kaynağıyla birlikte girilir |
| `raw/` | İndirilen ham sayfaların önbelleği. **Repoya girmez** (`.gitignore`) |

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
| `status` | `played` (oynandı), `forfeit` (hükmen), `not_played` (oynanmadı, örn. pandemide yarıda kalan sezon) |
| `venue_id`, `venue` | Stat (sadece detay sayfası çekilen maçlarda: play-off'lar, finaller, hükmen kontrolü yapılanlar) |

**Kulüp kimliği:** TFF her kulübe değişmeyen bir `kulupID` verir. Sponsor adı değişse de kimlik aynı kalır. Örneğin "ATİKER KONYASPOR" (2016-17) ve "TÜMOSAN KONYASPOR" (2026-27) ikisi de `3600`.

**Hükmen tespiti:** TFF fikstürde hükmen sonuçları normal skor gibi gösterir. 3-0 veya 0-3 biten her maçın detay sayfasına bakılır. Hakem ataması yoksa maç `forfeit` olarak işaretlenir.

## Yeniden üretmek

```bash
cd pipeline
uv run tlelo fetch      # sayfaları indirir (önbellekte olanları atlar)
uv run tlelo details    # hükmen kontrolü ve stat için maç detayları
uv run tlelo build      # CSV'leri yazar
uv run tlelo validate   # TFF puan cetvelleriyle karşılaştırır
```

İlk indirme yaklaşık 3–3,5 saat sürer: TFF sunucusuna yük olmamak için istekler arasında 2 saniye beklenir. Sonraki çalıştırmalar sadece eksik ya da değişen sayfaları indirir.
