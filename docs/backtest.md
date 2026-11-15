# Geriye dönük test: model v1.0

> Bu dosya `uv run tlelo backtest` ile üretilir, elle düzenlenmez. Yorumlar için bkz. [METODOLOJI.md](METODOLOJI.md).

- Ayar sezonları: 2021-22, 2022-23, 2023-24. Kontrol sezonları (ayarda hiç kullanılmadı): 2024-25, 2025-26, 2026-27.
- Ölçüt: iki profesyonel takım arasındaki yurt içi maçlarda 90 dakika sonucunun (ev sahibi / beraberlik / deplasman) log-loss'u. Düşük olan daha iyi.

## Tahmin başarısı

| Model | Ayar log-loss | Kontrol log-loss | Kontrol Brier |
|---|---|---|---|
| Sabit oranlar (ev/beraberlik/deplasman sıklığı) | 1.0673 | 1.0735 | 0.6495 |
| Sadece lig seviyesi | 1.0635 | 1.0687 | 0.6461 |
| Elo, plandaki başlangıç değerleri | 0.9962 | 0.9900 | 0.5897 |
| **Elo v1.0** | **0.9903** | **0.9802** | **0.5836** |

Maç sayısı: ayar 7238, kontrol 5708.

### Kontrol sezonlarında lig bazında

| Organizasyon | Maç | Sabit oranlar | Elo v1.0 |
|---|---|---|---|
| SL | 747 | 1.0640 | 0.9682 |
| 1L | 909 | 1.0726 | 0.9822 |
| 2L | 1419 | 1.0718 | 0.9543 |
| 3L | 2250 | 1.0769 | 0.9988 |
| TK | 379 | 1.0811 | 0.9852 |

## Plandan sapan her değerin etkisi

Değer plandaki başlangıç değerine geri alınınca log-loss ne kadar değişiyor (pozitif: geri almak kötüleştiriyor, yani değişiklik işe yarıyor).

| Parametre | Plan | v1.0 | Ayar farkı | Kontrol farkı |
|---|---|---|---|---|
| `k` | 20.0 | 24.0 | +0.0001 ± 0.0002 | +0.0008 ± 0.0003 |
| `home_closed` | 65.0 | 50.0 | +0.0000 ± 0.0000 | +0.0000 ± 0.0000 |
| `w_amateur` | 0.5 | 1.5 | +0.0001 ± 0.0001 | +0.0002 ± 0.0002 |
| `newcomer` | -50.0 | 50.0 | +0.0035 ± 0.0009 | +0.0042 ± 0.0013 |
| `amateur` | -100.0 | 0.0 | +0.0001 ± 0.0000 | +0.0001 ± 0.0001 |
| `return_pull` | 0.5 | 1.0 | +0.0001 ± 0.0001 | +0.0014 ± 0.0005 |
| `regression` | 0.1 | 0.3 | +0.0001 ± 0.0004 | +0.0008 ± 0.0005 |
| `seeds` | (1450.0, 1275.0, 1125.0, 1000.0) | (1360.0, 1220.0, 1100.0, 1000.0) | +0.0003 ± 0.0002 | +0.0003 ± 0.0002 |

## Denenen seçenekler

v1.0 üzerine tek bir değişiklik (pozitif: seçenek kötüleştiriyor).

| Seçenek | Ayar farkı | Kontrol farkı |
|---|---|---|
| Süper Lig şampiyonluk bonusu +30 | -0.0000 ± 0.0001 | -0.0001 ± 0.0001 |
| Yükselme/düşme düzeltmesi yok (P = 0) | -0.0001 ± 0.0002 | +0.0002 ± 0.0002 |
| Kupa bonusu yok (B = 0) | +0.0000 ± 0.0000 | +0.0001 ± 0.0000 |
| Avrupa maçları hariç (W = 0) | +0.0000 ± 0.0002 | -0.0002 ± 0.0002 |
| Avrupa maçları yarım ağırlık (W = 0,5) | -0.0000 ± 0.0001 | -0.0001 ± 0.0001 |
| Avrupa'da turnuva terimi (ŞL/AL/KL) | +0.0000 ± 0.0000 | +0.0000 ± 0.0000 |
| Gol farkı çarpanı yok (G = 1) | +0.0035 ± 0.0007 | +0.0052 ± 0.0009 |
| Geçici K yok | -0.0001 ± 0.0002 | +0.0000 ± 0.0003 |
| Kulübün son 3 sezon ortalamasına çekme | -0.0001 ± 0.0006 | +0.0025 ± 0.0008 |
| Lig ortalaması ile kulübün ortalamasının ortasına çekme | -0.0004 ± 0.0003 | +0.0008 ± 0.0004 |

## Avrupa

Rakip puanı = 1061 + 140.2 × ln(1 + katsayı). Avrupa'da ev sahibi avantajı 73 puan (446 oynanmış maçtan).

| UEFA kulüp katsayısı | 1 | 5 | 10 | 20 | 50 | 100 | 140 |
|---|---|---|---|---|---|---|---|
| Rakip puanı | 1158 | 1312 | 1397 | 1488 | 1612 | 1708 | 1755 |

Turnuva terimi (Şampiyonlar Ligi'ne göre): UEL -0, UECL +20. Olabilirlik oranı testi: 0.19, p = 0.91.

| Turnuva | Maç | Türk takımının ortalama (S − E) farkı |
|---|---|---|
| UCL | 101 | +0.002 |
| UECL | 112 | -0.015 |
| UEL | 233 | +0.006 |

## Ligler arası fark

Kupada farklı liglerden takımların maçları: üst lig takımının ortalama skoru ve bunun puan karşılığı (`400 × log10(p / (1 − p))`).

| Eşleşme | Maç | Üst ligin ortalama skoru | Puan farkı karşılığı |
|---|---|---|---|
| Süper Lig – 1. Lig | 80 | 0.844 | 293 |
| Süper Lig – 2. Lig | 76 | 0.875 | 338 |
| Süper Lig – 3. Lig | 46 | 0.913 | 408 |
| 1. Lig – 2. Lig | 63 | 0.754 | 195 |
| 1. Lig – 3. Lig | 72 | 0.701 | 148 |
| 2. Lig – 3. Lig | 159 | 0.541 | 28 |

### Puan dağılımı (2026-27, şu an)

| Lig | Takım | En düşük | Ortalama | En yüksek |
|---|---|---|---|---|
| Süper Lig | 18 | 1292 | 1470 | 1657 |
| 1. Lig | 20 | 1118 | 1294 | 1449 |
| 2. Lig | 35 | 919 | 1140 | 1301 |
| 3. Lig | 54 | 737 | 1005 | 1211 |

En iyi ile en kötü takım arası: 920 puan.
