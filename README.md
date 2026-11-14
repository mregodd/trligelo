# turkish-leagues-elo

Türk profesyonel futbol ligleri (Süper Lig, 1. Lig, 2. Lig, 3. Lig) için açık kaynaklı, düzenli güncellenen bir Elo puanlama sistemi.

- Bütün takımlar tek bir ölçekte puanlanır. Lig maçları, Türkiye Kupası, Süper Kupa ve UEFA turnuvaları hesaba katılır, hazırlık maçları katılmaz.
- Puanlar maçlar sonuçlandıktan kısa bir süre sonra otomatik olarak güncellenir.
- Formül, parametreler ve hesaplama adımları herkese açıktır. Repoyu klonlayan herkes aynı puanları yeniden üretebilir.
- Proje kâr amacı gütmez: üyelik ve reklam yoktur.

## Durum

Planlama aşamasında. Ayrıntılar için [docs/PLAN.md](docs/PLAN.md).

## Veri kaynakları

- Maç sonuçları: [Türkiye Futbol Federasyonu (tff.org)](https://www.tff.org). TFF kullanım şartları gereği kaynak gösterilerek ve ticari olmayan amaçla kullanılır.
- Avrupa kupası maç sonuçları: [openfootball](https://github.com/openfootball/champions-league) (CC0)
- Avrupa kupalarındaki rakiplerin gücü: UEFA kulüp katsayıları ([kassiesa.net](https://kassiesa.net/uefa/))
