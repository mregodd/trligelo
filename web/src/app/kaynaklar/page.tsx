import type { Metadata } from "next";

import { TextPage } from "@/components/TextPage";
import { REPO, SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Kaynaklar",
  description: `${SITE} verilerinin kaynakları ve kullanım koşulları.`,
};

export default function SourcesPage() {
  return (
    <TextPage title="Kaynaklar" lead="Verilerin nereden geldiği ve hangi koşullarla kullanıldığı.">
      <h2>Yurt içi maçlar ve kulüpler</h2>
      <p>
        Süper Lig, 1. Lig, 2. Lig, 3. Lig, play-off, Ziraat Türkiye Kupası ve Süper Kupa maç
        sonuçları, puan durumları, kulüp adları ve kulüp logoları{" "}
        <a href="https://www.tff.org" rel="noopener">
          Türkiye Futbol Federasyonu
        </a>{" "}
        (tff.org) sayfalarından alınır. TFF'nin kullanım şartları gereği kaynak gösterilerek ve
        ticari olmayan amaçla kullanılır. Kulüp logoları ilgili kulüplerin markalarıdır.
      </p>

      <h2>Avrupa maçları ve UEFA katsayıları</h2>
      <p>
        Türk kulüplerinin Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi maçları ile rakiplerin
        UEFA kulüp katsayıları, İngilizce{" "}
        <a href="https://en.wikipedia.org" rel="noopener">
          Wikipedia
        </a>{" "}
        turnuva sayfalarından alınır. Bu içerik{" "}
        <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.tr" rel="noopener">
          CC BY-SA 4.0
        </a>{" "}
        lisanslıdır; ondan türetilen veriler de aynı koşullara tabidir.
      </p>
      <p>
        Avrupa maçları ayrıca{" "}
        <a href="https://github.com/openfootball" rel="noopener">
          openfootball
        </a>{" "}
        (kamu malı, CC0) verileriyle karşılaştırılarak doğrulanır.
      </p>

      <h2>Hesaplanan puanlar</h2>
      <p>
        Puanlar bu verilerden <a href="/metodoloji/">Elo yöntemiyle</a> hesaplanır. Ham veriler,
        hesaplanan puanlar ve kod <a href={REPO}>GitHub'da</a>.
      </p>
    </TextPage>
  );
}
