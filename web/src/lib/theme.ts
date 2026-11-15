/**
 * Runs in <head> before the first paint: the stored choice, else the system's, as
 * data-theme on <html>; follows the system while no choice is stored. Kept in sync with
 * components/ThemeToggle.tsx. The choice lives in this browser only (localStorage, no cookie).
 * English pages (/en/) also get lang="en" on <html>: the static HTML says tr, while their
 * whole content already carries lang="en" (components/Frame.tsx).
 */
export const THEME_SCRIPT = `(() => {
  const m = matchMedia("(prefers-color-scheme: dark)");
  const stored = () => { try { return localStorage.getItem("theme"); } catch { return null; } };
  const apply = () => { document.documentElement.dataset.theme = stored() || (m.matches ? "dark" : "light"); };
  apply();
  if (location.pathname.startsWith("/en/")) document.documentElement.lang = "en";
  m.addEventListener("change", apply);
})();`;
