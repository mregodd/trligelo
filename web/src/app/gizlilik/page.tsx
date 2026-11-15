import type { Metadata } from "next";

import { TextPage } from "@/components/TextPage";
import { CONTACT, SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Gizlilik",
  description: `${SITE} ziyaretçiler hakkında ne topluyor, ne toplamıyor.`,
};

// shortcut: describes the launch setup (Cloudflare Pages + Cloudflare Web Analytics, decided
// for Faz 4); update this page if the hosting or the statistics tool changes.
export default function PrivacyPage() {
  return (
    <TextPage title="Gizlilik" lead="Bu site ziyaretçiler hakkında ne topluyor, ne toplamıyor.">
      <h2>Kısaca</h2>
      <p>
        Bu site çerez kullanmaz. Üyelik, form ya da yorum yoktur; ad, e-posta gibi kişisel bilgi
        istenmez ve toplanmaz.
      </p>

      <h2>Ziyaret istatistikleri</h2>
      <p>
        Sitenin ne kadar kullanıldığını görmek için Cloudflare Web Analytics kullanılır. Bu araç
        çerez ya da cihazda saklanan bir kimlik kullanmaz. Sayfa görüntülemelerini, ziyaretçilerin
        hangi siteden geldiğini, ülkeyi ve cihaz türünü toplu sayılar olarak gösterir; tek tek
        ziyaretçileri tanımaz ve siteler arasında izlemez. Ayrıntılar için{" "}
        <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener">
          Cloudflare'in gizlilik politikası
        </a>
        .
      </p>

      <h2>Barındırma</h2>
      <p>
        Site Cloudflare Pages üzerinde yayınlanır. Her web sunucusu gibi Cloudflare da sayfaları
        gönderirken isteklerin teknik kayıtlarını tutabilir.
      </p>

      <h2>Tema tercihi</h2>
      <p>
        Açık ya da koyu tema seçimi yalnızca kullandığınız tarayıcıda saklanır (localStorage); siteye
        gönderilmez.
      </p>

      <h2>İletişim</h2>
      <p>
        Sorular için: <a href={`mailto:${CONTACT}`}>{CONTACT}</a>. Son güncelleme: 15 Kasım 2026.
      </p>
    </TextPage>
  );
}
