import type { Lang } from "@/lib/i18n";

import { en } from "./en";
import { type Messages, tr } from "./tr";

const MESSAGES: Record<Lang, Messages> = { tr, en };

/** Every short text of the site in one language (see tr.ts). */
export const msg = (lang: Lang): Messages => MESSAGES[lang];

export type { Messages };
