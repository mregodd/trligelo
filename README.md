# turkish-leagues-elo

Türk profesyonel futbol ligleri (Süper Lig, 1. Lig, 2. Lig, 3. Lig) için açık kaynaklı, düzenli güncellenen bir Elo puanlama sistemi.

- Bütün takımlar tek bir ölçekte puanlanır. Lig maçları, Türkiye Kupası, Süper Kupa ve UEFA turnuvaları hesaba katılır, hazırlık maçları katılmaz.
- Puanlar maçlar sonuçlandıktan kısa bir süre sonra otomatik olarak güncellenir.
- Formül, parametreler ve hesaplama adımları herkese açıktır. Repoyu klonlayan herkes aynı puanları yeniden üretebilir.
- Proje kâr amacı gütmez: üyelik ve reklam yoktur.

## Durum

Veri katmanı ve Elo motoru hazır (model v1.0). 2016-17'den bugüne yurt içi ve Avrupa maçları [data/](data/README.md) klasöründe, güncel puanlar [data/ratings/current.csv](data/ratings/current.csv) dosyasında. Puanların nasıl hesaplandığı: [docs/METODOLOJI.md](docs/METODOLOJI.md). Parametrelerin nasıl seçildiği: [docs/backtest.md](docs/backtest.md). Web sitesi [web/](web/README.md) klasöründe; sıradaki adım otomatik güncelleme ve yayın (Cloudflare).

## Veri kaynakları

- Yurt içi maç sonuçları: [Türkiye Futbol Federasyonu (tff.org)](https://www.tff.org). TFF kullanım şartları gereği kaynak gösterilerek ve ticari olmayan amaçla kullanılır.
- Kulüp logoları: kulüplerin TFF sayfaları. Logolar kulüplerin markasıdır; repoda yer almaz, site derlenirken indirilen önbellekten kopyalanır ve bu reponun lisansına girmez.
- Avrupa kupası maç sonuçları ve UEFA kulüp/ülke katsayıları: [Wikipedia](https://en.wikipedia.org/wiki/UEFA_Champions_League) (İngilizce) turnuva sayfaları, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Avrupa maçlarının çapraz doğrulaması: [openfootball](https://github.com/openfootball/champions-league) (CC0)
