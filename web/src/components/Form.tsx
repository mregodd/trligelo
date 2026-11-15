import { fmt, result } from "@/lib/format";
import type { Lang } from "@/lib/i18n";
import type { FormEntry } from "@/lib/types";
import { msg } from "@/messages";

import styles from "./Form.module.css";

/** Last matches, oldest first: G/B/M (W/D/L in English). Letter and colour. */
export function Form({ form, lang }: { form: FormEntry[]; lang: Lang }) {
  if (form.length === 0) return null;
  const m = msg(lang);
  const words = form.map((e) => m.result.word[result(e.s)]).join(", ");
  const { delta } = fmt(lang);
  return (
    <span className={styles.form} aria-label={m.form.label(form.length, words)}>
      {form.map((e, i) => {
        const r = result(e.s);
        return (
          <span key={i} className={styles.cell} data-r={r} title={`${m.result.word[r]}, ${delta(e.d)}`}>
            {m.result.letter[r]}
          </span>
        );
      })}
    </span>
  );
}
