# Faz 2 raporu: Elo motoru, geriye dönük test, model v1.0

> 14 Kasım 2026. Sayıların tamamı `uv run tlelo backtest` ile yeniden üretilir: [backtest.md](backtest.md). Halka açık anlatım: [METODOLOJI.md](METODOLOJI.md).

## Özet

- **Elo motoru:** PLAN §4'teki model kodlandı (`pipeline/src/tlelo/elo/`). Bütün 2016-17 → bugün verisi (25.288 maç) tek geçişte ~0,1 saniyede işleniyor, Avrupa modelinin uydurulmasıyla birlikte ~0,3 saniye.
- **Tahmin başarısı:** Model v1.0, kontrol sezonlarında (2024-25 → bugün, ayarda hiç kullanılmadı) log-loss **0,980** veriyor. Kıyaslar: sabit oranlar 1,074, sadece lig seviyesi 1,069, plandaki başlangıç değerleri 0,990.
- **Parametreler:** Plandaki başlangıç değerlerinden sadece 8'i değişti, hepsi verinin açıkça desteklediği yerlerde. Diğerleri plandaki gibi kaldı.
- **Puan dağılımı:** 737–1657 arası, en iyi ile en kötü arası 920 puan. Hedeflenen 700–2000 aralığında ve beklenen 700–900 marjına yakın.
- **Açık sorulara verilen cevaplar** (bkz. aşağıdaki "Sorulara cevaplar"):
  - Avrupa maçları yurt içi tahminlere zarar vermiyor.
  - Turnuva seviyesi için ayrı bir terim gerekmiyor.
  - Şampiyonluk bonusu tahmine bir şey eklemiyor.
  - P ve B zararsız, korunuyor.

## Ne yapıldı

| Modül | İş |
|---|---|
| `elo/data.py` | Yurt içi ve Avrupa CSV'lerini sezon sezon tek bir maç akışına çevirir. Profesyonel, amatör (PGL) ve yabancı tarafları ayırır. Tarafsız saha, seyircisiz dönem ve Süper Lig şampiyonu burada belirlenir |
| `elo/engine.py` | Sezon geçişi (P, ortalamaya çekme, yeni ve dönen takımlar, ölçek sabitleme), maç güncellemesi, kupa bonusu |
| `elo/fit.py` | Avrupa rakip modeli (a, b, Avrupa ev avantajı) ve galibiyet/beraberlik/mağlubiyet modeli (sıralı lojistik) |
| `elo/backtest.py` | Puanlama, kıyas modelleri, parametre taraması |
| `elo/report.py`, `elo/output.py` | `docs/backtest.md` raporu, `data/ratings/current.csv` ve `history.csv` |

## Yöntem

- **Sızıntı yok:** Her maç sadece kendisinden önceki puanlarla tahmin edildi. Motor her maçın maç öncesi puanlarını kaydediyor.
- **Ne tahmin ediliyor:** 90 dakika sonucu (ev sahibi / beraberlik / deplasman), bahis piyasalarındaki gibi. Puan farkından üç olasılığa geçiş sıralı lojistik modelle yapıldı. Bu modelin 3 parametresi ayar sezonlarında uyduruldu, kontrol sezonlarına aynen uygulandı.
- **Hangi maçlar puanlanıyor:** İki profesyonel takım arasındaki yurt içi maçlar (lig, play-off, kupa, Süper Kupa). Ayar sezonlarında 7.238, kontrol sezonlarında 5.708 maç.
- **Dönemler:**
  - 2016-17 → 2020-21: ısınma dönemi, hiç puanlanmadı.
  - 2021-22 → 2023-24: ayar.
  - 2024-25 → 2026-27 (bugüne kadar): kontrol.
- **Tarama:** Parametrelerin her biri sırayla en iyi değerine getirildi, birkaç tur. Geri alma kontrolleriyle birlikte toplam ~900 tam hesaplama yapıldı.
- **Seçim kuralı:** Tarama küçük ve gürültülü kazançlar da buluyor. Bu yüzden her değişiklik tek tek geri alınarak kontrol sezonlarındaki etkisi ölçüldü (eşleştirilmiş fark ± standart hata). Bir değer sadece hem ayar hem kontrol sezonlarında aynı yönde iyileştirdiyse değiştirildi. Diğer değerler plandaki başlangıç değerinde bırakıldı.

## Model v1.0: plandan değişen değerler

| Parametre | Plan | v1.0 | Gerekçe (kontrol sezonlarında geri almanın maliyeti) |
|---|---|---|---|
| K | 20 | **24** | +0,0008 ± 0,0003 |
| Sezon arası ortalamaya çekme (α) | 0,10 | **0,30** | +0,0008 ± 0,0005; ilk taramada +0,0024 ± 0,0006 |
| Başlangıç puanları | 1450 / 1275 / 1125 / 1000 | **1360 / 1220 / 1100 / 1000** | +0,0003 ± 0,0002 |
| Yeni gelen takım (3. Lig ortalamasına göre) | −50 | **+50** | +0,0042 ± 0,0013 (en büyük etki) |
| Amatörden dönen takım | Yarı yolda | **Yeni gelen gibi** | +0,0014 ± 0,0005 |
| Amatör kupa rakibinin sabit puanı | 3. Lig − 100 | **3. Lig ortalaması** | +0,0001 ± 0,0001 |
| Amatörle kupa maçı ağırlığı | ×0,5 | **×1,5** | +0,0002 ± 0,0002 |
| Seyircisiz maçta ev avantajı | 65 | **50** | Doğrudan ölçüm (aşağıda). Bu maçların hepsi ısınma döneminde olduğu için test ölçemiyor |

Ölçülüp plandaki değerinde bırakılanlar:
- H = 65. 85 ile fark gürültü düzeyinde.
- W: kupa 0,75 (final 1), Süper Kupa 0,75, play-off 1, Avrupa 1.
- Geçici K: ilk 10 maç ×1,5.
- P: 30 / 25 / 20.
- B: Türkiye Kupası 15, Süper Kupa 5.
- Şampiyonluk bonusu yok.

**Yeni gelen takımlar:**
- **Bulgu:** 2017-18'den bu yana 90 kulüp amatör ligden 3. Lig'e çıktı. İlk sezonlarında maç başına 1,375 puan aldılar; diğer 3. Lig takımları 1,356 aldı. Plandaki varsayım (ortalamanın 50 altı) yanlıştı.
- **Hata ve düzeltme:** İlk taramada bu parametre +100 gibi aşırı bir değere gitti. Sebep, yeni takımın sezon geçişinde ortalamaya çekme ve ölçek sabitlemesinden önce eklenmesiydi. Sıra düzeltildi: yeni takım artık "3. Lig'in önceki sezondan kalan takımlarının ortalamasının X üstü" olarak giriyor. Bu tanımla en iyi değer +50 çıktı ve ayar ile kontrol sezonları bunda uyuştu.

**Seyircisiz maçlar:** Ev sahibinin ortalama Elo skoru seyirciyle 0,582 (21.672 maç), seyircisiz 0,566 (2.901 maç). Bunun puan karşılığı yaklaşık 58'e karşı 46. Ev avantajı azalmış ama kaybolmamış. 65 × (46 / 58) ≈ 50.

## Sorulara cevaplar

**Avrupa maçları yurt içi puanlara zarar veriyor mu?** Hayır. Kontrol sezonlarındaki yurt içi log-loss:

| Avrupa maçları | v1.0'a göre fark |
|---|---|
| Hariç (W = 0) | −0,0002 ± 0,0002 |
| Yarım ağırlık (W = 0,5) | −0,0001 ± 0,0001 |
| Tam ağırlık (W = 1, v1.0) | 0 |

Üç seçenek arasındaki fark gürültü düzeyinde. Avrupa maçları gerçek maçlar ve Türk takımlarını dış bir referansa karşı ölçüyor. Bu yüzden tam ağırlık korundu.

**Turnuva seviyesi ayrıca hesaba katılmalı mı?**
- **Eski bulgu:** Plandaki başlangıç değerleriyle Türk takımları Şampiyonlar Ligi'nde beklentinin 0,074 altında kalıyordu.
- **v1.0'da sapmalar:** Ayarlanmış modelde turnuva başına ortalama sapma ŞL +0,002, AL +0,006, KL −0,015, yani üçü de sıfıra çok yakın.
- **Terim testi:** Turnuva terimi eklendiğinde olabilirlik oranı testi p = 0,91 verdi.

Seviye farkı rakibin katsayısından zaten geliyor. Ayrı bir terim eklenmedi.

**Avrupa rakip modeli:** Rakip puanı = 1061 + 140,2 × ln(1 + katsayı). Avrupa'da ev avantajı 73. 446 oynanmış maçtan, Türk takımlarının o anki puanlarıyla birlikte uyduruldu.

**Süper Lig şampiyonluk bonusu:**
- **Tarama:** İlk taramada +60'a kadar çıktı. Sebebi, güçlü ortalamaya çekmeyle (α = 0,3) birbirini dengelemeleriydi: Büyük kulüpler, ortalamaya çekmenin varsaydığından daha istikrarlı.
- **Geri alma testi:** Tek başına ele alındığında kontrol sezonlarındaki etkisi +0,0002 ± 0,0002, yani gürültü. Alınmadı.
- **Not:** Büyük kulüplerin istikrarı için daha doğru bir yol "takımın kendi uzun dönem ortalamasına çekme" olabilir. v1.1 için not edildi.

**P ve B:** İkisi de tahmini bozmuyor:
- P'yi kaldırmak: +0,0002 ± 0,0002
- B'yi kaldırmak: +0,0001 ± 0,0000

Plandaki değerleriyle korundu.

## Lig seviyeleri

| Eşleşme | Kupa maçı | Üst ligin ortalama skoru | Puan karşılığı |
|---|---|---|---|
| Süper Lig – 1. Lig | 80 | 0,844 | 293 |
| 1. Lig – 2. Lig | 63 | 0,754 | 195 |
| 2. Lig – 3. Lig | 159 | 0,541 | 28 |

2. Lig ile 3. Lig takımları kupada neredeyse eşit. Model bunu kendisi buluyor: Şu anki lig ortalamaları Süper Lig 1470, 1. Lig 1294, 2. Lig 1140, 3. Lig 1005. Kupa maçlarındaki rotasyon üst ligleri olduğundan zayıf gösterdiği için kupa farkları birebir alınmadı. Puanlar maç akışından kendiliğinden oluşuyor.

## Çıktılar

- `data/ratings/current.csv`: Güncel sezonun 127 takımı, puan sırasıyla.
- `data/ratings/history.csv`: Her takımın her puan değişikliği: maçlar, P, ortalamaya çekme, bonuslar, ölçek kayması. Yaklaşık 53 bin satır ve 6 MB olduğu için repoya girmiyor (`.gitignore`). `uv run tlelo elo` ile yeniden üretiliyor.

## Yapılmayanlar ve sınırlar

- **Bahis oranlarıyla kıyas** (PLAN §4.9 b, football-data.co.uk) henüz yapılmadı. Süper Lig için ayrı bir adım olarak eklenebilir.
- **Seyircisiz ev avantajı** test ile değil doğrudan ölçümle seçildi.
- **Avrupa'da tarafsız saha:** Wikipedia'daki stat adresine göre belirleniyor. Ülke adı yazıyorsa maç yurt dışında oynanmıştır. Türkiye'de oynanmışsa Türk takımı fiilen ev sahibidir (örn. BATE–Konyaspor, Konya).
- **Güncel sezon** yarım. Kontrol sezonlarına bugüne kadar oynanan maçlarla dahil.

## Sıradaki adım

Faz 3: Next.js statik site.
- Genel sıralama, lig tabloları, takım sayfası (puan grafiği, maç maç değişim) ve metodoloji sayfası.
- Veri `data/ratings/` çıktılarından JSON'a çevrilecek.
