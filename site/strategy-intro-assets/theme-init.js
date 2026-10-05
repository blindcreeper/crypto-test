(() => {
  let saved;
  try { saved = localStorage.getItem("strategy-docs-theme"); } catch {}
  const prefersDark = window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme =
    saved === "light" || saved === "dark" ? saved : (prefersDark ? "dark" : "light");
})();
