import styles from "./ClubLogo.module.css";

/**
 * The club's logo (from its TFF page). Decorative: the name always stands beside it.
 * `keepSpace` leaves an empty square when there is none, so names in a column line up.
 */
export function ClubLogo({
  src,
  size = 20,
  keepSpace = false,
}: {
  src: string | null;
  size?: number;
  keepSpace?: boolean;
}) {
  if (!src) {
    return keepSpace ? <span className={styles.logo} style={{ width: size, height: size }} /> : null;
  }
  return (
    <img
      className={styles.logo}
      src={src}
      alt=""
      width={size}
      height={size}
      loading="lazy"
      decoding="async"
    />
  );
}
