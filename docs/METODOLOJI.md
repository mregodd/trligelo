# Puanlar nasıl hesaplanıyor?

> **Model v1.0** · Taslak, 14 Kasım 2026. Bu doküman sitedeki metodoloji sayfasının kaynağıdır.

Bu sayfa Türk profesyonel liglerindeki (Süper Lig, 1. Lig, 2. Lig, 3. Lig) bütün takımların puanlarının nasıl hesaplandığını anlatıyor. Formüller var ama hepsinin yanında düz bir açıklama ve gerçek bir maç örneği bulacaksın. Kodun ve verinin tamamı açık: Aynı puanları kendin de üretebilirsin (bkz. [Kendin hesapla](#10-kendin-hesapla)).

## 1. Elo nedir?

Elo, satrançta oyuncuları sıralamak için geliştirilmiş bir puan sistemi. Fikri basit: Her takımın bir puanı var. İki takım karşılaştığında puan farkına bakılarak kimin ne kadar favori olduğu hesaplanır. Maçtan sonra takımlar puanlarını birbirine aktarır. Kaybeden ne kadar kaybederse kazanan o kadar kazanır.

Kilit nokta: **Beklenen sonuç az puan, sürpriz sonuç çok puan getirir.** Favori takım rakibini yenerse birkaç puan alır, çünkü zaten bekleniyordu. Ama güçsüz takım favoriyi yenerse büyük bir puan kazanır. Zamanla her takımın puanı gerçek gücünü yansıtacak bir yere oturur.

Puanların kendisinden çok **farkları** anlamlıdır. 200 puan önde olan takım rakibine karşı yaklaşık %76'lık bir "beklenen skor" taşır.

## 2. Formül

```
Ev sahibinin beklenen skoru:   E = 1 / (1 + 10^( −(R_ev + H − R_dep) / 400 ))
Maçtan sonra puan değişimi:    Δ = K × W × G × (S − E)
                               R_ev ← R_ev + Δ      R_dep ← R_dep − Δ
```

| Sembol | Anlamı | Değer (v1.0) |
|---|---|---|
| R | Takımın maç öncesi puanı | — |
| H | Ev sahibi avantajı, puan cinsinden | 65 (tarafsız sahada 0) |
| E | Beklenen skor: kazanma olasılığı + beraberlik olasılığının yarısı (0–1 arası) | — |
| S | Gerçek sonuç: galibiyet 1, beraberlik 0,5, mağlubiyet 0 | — |
| K | Bir maçın puanları en fazla ne kadar oynatabileceği | 24 |
| W | Organizasyonun ağırlığı | Bkz. §4 |
| G | Gol farkı çarpanı | Bkz. §4 |

## 3. Gerçek bir maç: Galatasaray 2-1 Fenerbahçe (26 Ekim 2026)

1. **Maç öncesi puanlar:** Galatasaray 1617,7, Fenerbahçe 1622,6. Galatasaray evinde oynadığı için 65 puan ev avantajı alır.
2. **Fark:** 1617,7 + 65 − 1622,6 = **60,1 puan** Galatasaray lehine.
3. **Beklenen skor:** E = 1 / (1 + 10^(−60,1 / 400)) = **0,586**. Yani Galatasaray hafif favori.
4. **Sonuç:** Galatasaray kazandı, S = 1. Bir farklı galibiyet: G = 1. Lig maçı: W = 1.
5. **Değişim:** Δ = 24 × 1 × 1 × (1 − 0,586) = **+9,9**. Galatasaray 1627,7'ye çıktı, Fenerbahçe 1612,7'ye indi.

Maç berabere bitseydi Galatasaray 24 × (0,5 − 0,586) = −2,1 puan kaybedecekti. Favori olduğu için beraberlik onun için küçük bir kayıptır.

## 4. Ev avantajı, gol farkı ve organizasyon ağırlıkları

**Ev avantajı (H):** Türkiye'de ev sahibi takımlar belirgin biçimde daha başarılı. Bu yüzden ev sahibine 65 puanlık bir avantaj eklenir. Süper Kupa, kupa finalleri ve play-off finalleri tarafsız sahada oynandığı için orada H = 0. Pandemide seyircisiz oynanan maçlarda ev avantajı azalmıştı: Verilerde ev sahibinin ortalama skoru seyirciyle 0,582, seyircisiz 0,566. Bu yüzden o dönemde H = 50.

**Gol farkı (G):** Farklı galibiyet daha çok şey söyler. 1 farkta G = 1, 2 farkta 1,5, 3 ve üzerinde (11 + fark) / 8. Yani 3 farkta 1,75, 5 farkta 2. Test, gol farkını hesaba katmanın tahmini belirgin biçimde iyileştirdiğini gösterdi.

**Uzatma ve penaltılar:** Uzatmaya giden maçta 120 dakikanın sonucu esas alınır. Penaltılarla biten maç beraberlik sayılır. Turu kim geçerse geçsin, penaltı atışları bir takımın gücü hakkında çok az şey söyler.

**Organizasyon ağırlığı (W):**

| Maç | W |
|---|---|
| Lig ve play-off | 1 |
| Ziraat Türkiye Kupası | 0,75 (final 1). Büyük takımlar erken turlarda rotasyon yapıyor |
| Süper Kupa | 0,75 |
| UEFA turnuvaları | 1 |
| Amatör bir takımla kupa maçı | Kupa ağırlığının 1,5 katı. Test, bu maçların bilgilendirici olduğunu gösterdi |

**Hükmen maçlar** puan hesabına girmez, çünkü sahada oynanmadılar. 212 hükmen maçın ~205'i ligden çekilen kulüplerin kalan maçları. Bunları saymak, fikstürde o takımla depremden veya çekilmeden sonra karşılaşanlara bedava puan verirdi. Resmi sonuç yine de geçerlidir: Puan cetvelinde, küme düşme/çıkma ve kupa bonuslarında kullanılır.

## 5. Sezonlar arasında ne oluyor?

Her yaz, yeni sezondan önce şu adımlar sırayla uygulanır:

1. **Yükselme/düşme düzeltmesi:** Üst lige çıkan takım puan alır, düşen takım puan kaybeder. Süper Lig ↔ 1. Lig sınırında 30, 1. Lig ↔ 2. Lig'de 25, 2. Lig ↔ 3. Lig'de 20 puan.
2. **Kupa bonusu** (sezon içinde, finalden hemen sonra): Ziraat Türkiye Kupası şampiyonuna +15, Süper Kupa şampiyonuna +5. Bonus, takımın puan geçmişinde ayrı bir satır olarak görünür.
3. **Ortalamaya çekme:** Her takımın puanı, ligin ortalamasına doğru farkın %30'u kadar çekilir. Bunun sebebi yaz aylarında kadroların değişmesi: Geçen sezonun çok iyi ve çok kötü takımları yeni sezona biraz daha ortalamaya yakın başlar. Bu adım ligin toplam puanını değiştirmez. Ortalamadan uzak takım çok puan kaybeder: ortalamanın 290 puan üstündeki Galatasaray 2025-26'ya 87 puan eksik başladı. Puanı ligin değil kulübün son üç sezonunun ortalamasına çekmek de denendi; büyük kulüplerin kaybı küçülüyor ama tahminler kötüleşiyor ([backtest.md](backtest.md)).
4. **Yeni gelen takımlar:** Amatör ligden 3. Lig'e çıkan bir takım, 3. Lig ortalamasının 50 puan üstünden başlar. Veriler bu takımların ilk sezonlarında 3. Lig ortalamasında ya da biraz üstünde oynadığını gösteriyor. Amatöre düşüp geri dönen takım da yeni gelen gibi başlar. Bu takımların ilk 10 maçında K 1,5 katıdır, böylece puanları hızlı oturur.
5. **Ölçeğin sabitlenmesi:** Bütün puanlara aynı sayı eklenir ya da çıkarılır, böylece 3. Lig ortalaması 1000 olur. Bu hiçbir sıralamayı ya da tahmini değiştirmez, sadece puanların zamanla kaymasını önler.

## 6. Avrupa maçları ve amatör takımlar

**Avrupa kupaları:** Sadece Türk takımının puanı değişir. Yabancı rakibin puanı o sezonki **UEFA kulüp katsayısından** türetilir:

```
Rakibin puanı = 1061 + 140 × ln(1 + UEFA kulüp katsayısı)
```

| UEFA katsayısı | 1 | 5 | 20 | 50 | 100 | 140 |
|---|---|---|---|---|---|---|
| Rakibin puanı | 1158 | 1312 | 1488 | 1612 | 1708 | 1755 |

Bu formüldeki iki sayı Türk takımlarının 2016-17'den bu yana oynadığı 446 Avrupa maçının sonuçlarından hesaplanır ve her hesaplamada yeniden bulunur. Böylece Avrupa maçları toplamda Türk takımlarına bedava puan vermez. Beklentinin üstünde oynayan kazanır, altında oynayan kaybeder. Avrupa'da ev avantajı da bu maçlardan ölçülür: 73 puan.

*Örnek:* Lille 2-4 Galatasaray (21 Ekim 2026, Şampiyonlar Ligi). Lille'nin katsayısı 68,75, yani puanı ~1656. Lille evinde oynadığı için Galatasaray'ın (1593) beklenen skoru 0,31. Galatasaray iki farkla kazandı (G = 1,5). Değişim: 24 × 1 × 1,5 × (1 − 0,31) = **+24,7**.

Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi için ayrı bir çarpan yok. Turnuvanın seviyesi rakibin katsayısında zaten var: Bayern'i yenmek, katsayısı düşük bir rakibi yenmekten çok daha fazla puan getirir. Test, ayrı bir turnuva teriminin bir şey eklemediğini gösterdi.

**Amatör takımlar (Türkiye Kupası):** Kupada karşılaşılan amatör (PGL/BAL) takımların puanı sabittir ve 3. Lig ortalamasına (1000) eşittir. Sadece profesyonel takımın puanı değişir.

## 7. Başlangıç puanları ve ısınma dönemi

Hesaplama **2016-17 sezonunda** başlar. O sezon her takım liginin seviyesine göre sabit bir puanla başlar: Süper Lig 1360, 1. Lig 1220, 2. Lig 1100, 3. Lig 1000. Sonra bütün maçlar tarih sırasıyla bugüne kadar işlenir.

İlk beş sezon (2016-17 → 2020-21) **ısınma dönemidir**. Puanların başlangıç değerlerinden kurtulup oturması zaman alır. Sitedeki tablolar ve grafikler **2021-22'den** itibaren gösterilir. Böylece pandeminin bozduğu sezonlar da gösterilmez, ama puanların oturmasına katkı verir.

## 8. Parametreler nasıl seçildi?

"Doğru" parametre, maç sonuçlarını en iyi tahmin eden parametredir. Her maç, sadece o maçtan önceki puanlarla tahmin edildi (ev sahibi kazanır / beraberlik / deplasman kazanır) ve tahminlerin ne kadar isabetli olduğu ölçüldü. Ölçü olarak **log-loss** kullanıldı: Kendinden emin ama yanlış tahminleri ağır cezalandıran bir hata puanı. Düşük olan daha iyidir.

Parametreler 2021-22 → 2023-24 sezonlarında ayarlandı. Sonra hiç görülmemiş 2024-25 → bugün sezonlarında kontrol edildi:

| Model | Kontrol sezonlarında log-loss |
|---|---|
| Her maç için aynı tahmin (ev sahibi %45, beraberlik %26, deplasman %28) | 1,074 |
| Sadece hangi ligde oynadığına bakmak | 1,069 |
| Elo, planlanan başlangıç değerleriyle | 0,990 |
| **Elo v1.0** | **0,980** |

Bir değer, sadece hem ayar hem kontrol sezonlarında açıkça daha iyi sonuç verdiyse plandaki başlangıç değerinden değiştirildi. Diğerleri yerinde bırakıldı. Ayrıntılı tablolar: [backtest.md](backtest.md).

Testte denenip **alınmayan** seçenekler:
- **Süper Lig şampiyonluğuna bonus:** Tahmine bir katkısı yok. Şampiyon, puanını zaten maçlarını kazanarak toplamış oluyor.
- **Avrupa maçlarını dışarıda bırakmak:** Yurt içi tahminleri ne iyileştiriyor ne kötüleştiriyor. Avrupa maçları gerçek maçlar olduğu için tam ağırlıkla sayılıyor.

## 9. Sınırlamalar

Elo sadece sonuçlara bakar. Şunları bilmez:
- sakatlıklar, cezalar, transferler, teknik direktör değişiklikleri;
- rotasyon (örneğin Avrupa maçından önce yedeklerle çıkmak);
- iki ayaklı eşleşmede ilk maç skorunun rövanşa etkisi (4-0 önde gelen takım ikinci maçta rahat oynar).

Bunların hepsi sonuçlara yansıdığı için puanlar zamanla düzelir. Ama tek bir maçın sonucu bazen takımın gerçek gücünden çok bu tür etkileri gösterir.

Avrupa'daki rakiplerin gücü 5 yıllık UEFA katsayısından gelir ve yavaş değişir. Yeni yükselen bir kulüp gerçekte göründüğünden güçlü olabilir.

## 10. Kendin hesapla

```bash
git clone <repo adresi>
cd turkish-leagues-elo/pipeline
uv sync
uv run tlelo elo          # puanları data/ratings/ klasörüne yazar
uv run tlelo backtest     # docs/backtest.md test raporunu yeniden üretir
```

Maç verisi repoda hazır olarak duruyor (`data/`). Ham sayfaları yeniden indirmek istersen bkz. [data/README.md](../data/README.md).

## 11. Sürüm geçmişi

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| v1.0 | 14 Kasım 2026 | İlk sürüm |

## 12. Veri kaynakları

- **Yurt içi maçlar:** [Türkiye Futbol Federasyonu](https://www.tff.org). Kaynak gösterilerek ve ticari olmayan amaçla kullanılır.
- **Avrupa maçları ve UEFA katsayıları:** İngilizce [Wikipedia](https://en.wikipedia.org)'nın UEFA turnuva sayfaları ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). [openfootball](https://github.com/openfootball/champions-league) (CC0) ile çapraz doğrulandı.
