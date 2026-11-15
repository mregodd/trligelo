import { Frame } from "@/components/Frame";
import { msg } from "@/messages";

import styles from "./not-found.module.css";

// One 404 page for both languages (a static host serves a single 404.html).
export default function NotFound() {
  const tr = msg("tr").notFound;
  const en = msg("en").notFound;
  return (
    <Frame lang="tr">
      <section className={styles.band}>
        <div className="wrap">
          <h1>{tr.title}</h1>
          <p>
            {tr.text} <a href="/">{tr.home}</a>
          </p>
          <p lang="en">
            {en.text} <a href="/en/">{en.home}</a>
          </p>
        </div>
      </section>
    </Frame>
  );
}
