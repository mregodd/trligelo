import styles from "./TextPage.module.css";

/** A reading page: the band with a title and a lead line, then one column of prose. */
export function TextPage({
  title,
  lead,
  children,
}: {
  title: string;
  lead: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <>
      <section className={styles.band}>
        <div className="wrap">
          <h1>{title}</h1>
          <p>{lead}</p>
        </div>
      </section>
      <div className="wrap">
        <div className={styles.prose}>{children}</div>
      </div>
    </>
  );
}
