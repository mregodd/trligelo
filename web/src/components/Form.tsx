import { delta, RESULT_WORD, result } from "@/lib/format";
import type { FormEntry } from "@/lib/types";

import styles from "./Form.module.css";

/** Last matches, oldest first: G (galibiyet), B (beraberlik), M (mağlubiyet). Letter + colour. */
export function Form({ form }: { form: FormEntry[] }) {
  if (form.length === 0) return null;
  const words = form.map((f) => RESULT_WORD[result(f.s)]).join(", ");
  return (
    <span className={styles.form} aria-label={`Son ${form.length} maç: ${words}`}>
      {form.map((f, i) => {
        const r = result(f.s);
        return (
          <span key={i} className={styles.cell} data-r={r} title={`${RESULT_WORD[r]}, ${delta(f.d)}`}>
            {r}
          </span>
        );
      })}
    </span>
  );
}
