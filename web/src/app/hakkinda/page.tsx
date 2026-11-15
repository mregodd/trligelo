import type { Metadata } from "next";

import { TextPage } from "@/components/TextPage";
import { getMeta } from "@/lib/data";
import { dateLong } from "@/lib/format";
import { CONTACT, REPO, SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Hakkında",
  description: `${SITE}: ne olduğu, kimin geliştirdiği, nasıl ulaşılacağı.`,
};

export default function AboutPage() {
  const meta = getMeta();
  return (
    <TextPage title="Hakkında" lead={`${SITE} nedir, kim geliştiriyor, nasıl ulaşılır.`}>
      <p>
        {SITE}, Süper Lig'den 3. Lig'e Türkiye'deki bütün profesyonel futbol kulüplerini tek bir Elo
        ölçeğinde sıralar. Her maçtan sonra puanın neden ve ne kadar değiştiği, kulüp sayfalarında
        maç maç anlatılır. Yöntemin tamamı <a href="/metodoloji/">Puanlar nasıl hesaplanıyor?</a>{" "}
        sayfasında.
      </p>
      <p>
        Puanlar son olarak {dateLong(meta.lastMatch)} tarihli maçlara göre hesaplandı (model{" "}
        {meta.model}).
      </p>

      <h2>Kim geliştiriyor?</h2>
      <p>
        Siteyi Egemen Derbedek geliştiriyor. Ticari olmayan, kişisel bir projedir: reklam, üyelik ya
        da ücretli içerik yoktur. Türkiye Futbol Federasyonu, UEFA ya da herhangi bir kulüple bağı
        yoktur; buradaki sıralama resmi puan durumu değildir.
      </p>

      <h2>Kod ve veri</h2>
      <p>
        Verileri toplayan ve puanları hesaplayan kod, ham veriler ve bu sitenin kodu{" "}
        <a href={REPO}>GitHub'da</a> herkese açık. Verilerin nereden geldiği{" "}
        <a href="/kaynaklar/">Kaynaklar</a> sayfasında.
      </p>

      <h2>İletişim</h2>
      <p>
        Hata bildirimi, öneri ve sorular için: <a href={`mailto:${CONTACT}`}>{CONTACT}</a>. Hatalar
        GitHub'daki proje sayfasında da bildirilebilir.
      </p>
    </TextPage>
  );
}
