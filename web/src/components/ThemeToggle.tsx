"use client";

import { useEffect, useState } from "react";

import type { Lang } from "@/lib/i18n";
import { msg } from "@/messages";

import styles from "./ThemeToggle.module.css";

type Choice = "system" | "light" | "dark";

const NEXT: Record<Choice, Choice> = { system: "light", light: "dark", dark: "system" };

/** One button that cycles the colour theme: system, light, dark. */
export function ThemeToggle({ lang }: { lang: Lang }) {
  const [choice, setChoice] = useState<Choice>("system");

  useEffect(() => {
    try {
      const stored = localStorage.getItem("theme");
      if (stored === "light" || stored === "dark") setChoice(stored);
    } catch {
      // storage blocked (private mode): the theme simply follows the system
    }
  }, []);

  function change() {
    const next = NEXT[choice];
    setChoice(next);
    try {
      if (next === "system") localStorage.removeItem("theme");
      else localStorage.setItem("theme", next);
    } catch {
      // not stored: the choice lasts until the page is left
    }
    const dark = next === "dark" || (next === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }

  return (
    <button
      type="button"
      className={styles.toggle}
      onClick={change}
      aria-label={msg(lang).theme.aria(msg(lang).theme[choice])}
    >
      <svg viewBox="0 0 16 16" aria-hidden="true">
        {choice === "light" ? (
          <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <circle cx="8" cy="8" r="3" />
            <path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1" />
          </g>
        ) : choice === "dark" ? (
          <path d="M13.5 10.2A6 6 0 0 1 5.8 2.5a6 6 0 1 0 7.7 7.7Z" fill="currentColor" />
        ) : (
          <g>
            <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" strokeWidth="1.5" />
            <path d="M8 2a6 6 0 0 1 0 12Z" fill="currentColor" />
          </g>
        )}
      </svg>
      {msg(lang).theme[choice]}
    </button>
  );
}
