import styles from "./not-found.module.css";

export default function NotFound() {
  return (
    <section className={styles.band}>
      <div className="wrap">
        <h1>Bu sayfa yok</h1>
        <p>
          Adres yanlış yazılmış ya da kulüp artık listede olmayabilir.{" "}
          <a href="/">Genel sıralamaya dön</a>
        </p>
      </div>
    </section>
  );
}
