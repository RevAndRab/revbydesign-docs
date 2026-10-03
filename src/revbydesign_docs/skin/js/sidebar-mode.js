// Sidebar mode toggle.
//
// Cycles the reading width: normal (left nav + table of contents) -> wide
// (table of contents only) -> focus (neither) -> normal. The choice persists
// per reader in localStorage.
//
// WHY THIS IS IN THE SHARED PACKAGE
//
// It used to be `docs/js/focus-toggle.js`, copied into RevFramework and
// RevLearning. The two copies drifted and RevFramework ended up with the
// broken one, in two ways that both went unnoticed because the button still
// appeared on first load:
//
//   * It created the button without an id, while the stylesheet styled the
//     engaged state as `.md-header__button#rf-sidebar-toggle`. That rule had
//     therefore never matched anything, so the control never showed whether
//     it was on.
//   * It bound DOMContentLoaded. With `navigation.instant` enabled -- which
//     RevFramework has -- Material swaps pages by XHR and DOMContentLoaded
//     never fires again, so the button vanished after the first in-site
//     navigation and did not come back until a hard reload.
//
// Both are fixed below. `document$` is Material's documented hook for work
// that must survive instant navigation, and init is idempotent because
// document$ also fires on the first load.
//
// The `rf-` prefix on the id and the storage key is kept rather than renamed.
// It is load-bearing for readers who already have a mode saved, and renaming
// it would silently reset everyone's choice to buy nothing.

(function () {
  const KEY = "rf_sidebar_mode";
  const MODES = ["normal", "wide", "focus"];
  const BTN_ID = "rf-sidebar-toggle";

  function applyMode(mode) {
    document.body.classList.remove("sidebar-wide", "sidebar-focus");

    if (mode === "wide") document.body.classList.add("sidebar-wide");
    if (mode === "focus") document.body.classList.add("sidebar-focus");

    try { localStorage.setItem(KEY, mode); } catch {}
  }

  function getMode() {
    try {
      const saved = localStorage.getItem(KEY);
      if (saved && MODES.includes(saved)) return saved;
    } catch {}
    return "normal";
  }

  function nextMode(current) {
    const i = MODES.indexOf(current);
    return MODES[(i + 1) % MODES.length];
  }

  function iconFor(mode) {
    // 3 simple icons via inline SVG paths:
    // normal: both sidebars
    // wide: right sidebar only
    // focus: no sidebars (full width)
    const paths = {
      normal: "M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm6 2H5v10h5V7zm2 0v10h7V7h-7z",
      wide:   "M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm2 2v10h11V7H6z",
      focus:  "M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm2 2h12v10H6V7z"
    };
    return paths[mode] || paths.normal;
  }

  function titleFor(mode) {
    if (mode === "normal") return "Sidebar mode: Normal (left + TOC)";
    if (mode === "wide")   return "Sidebar mode: Wide (TOC only)";
    return "Sidebar mode: Focus (no sidebars)";
  }

  function createButton() {
    const btn = document.createElement("button");
    btn.className = "md-header__button md-icon";
    btn.type = "button";

    // The stylesheet styles the active state as
    // `.md-header__button#rf-sidebar-toggle`. Without an id that rule matches
    // nothing, so the button never showed it was engaged.
    btn.id = BTN_ID;

    btn.setAttribute("aria-label", "Toggle sidebar mode");
    btn.setAttribute("aria-pressed", "false");

    btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d=""></path></svg>';
    return btn;
  }

  function setButton(btn, mode) {
    const path = btn.querySelector("path");
    if (path) path.setAttribute("d", iconFor(mode));
    btn.setAttribute("title", titleFor(mode));
    btn.setAttribute("aria-pressed", mode === "normal" ? "false" : "true");
  }

  function init() {
    const headerInner = document.querySelector(".md-header__inner");
    if (!headerInner) return;

    // Idempotent. document$ fires on every instant navigation as well as the
    // first load, and the header may or may not have been replaced in between,
    // so re-running must not add a second button.
    if (headerInner.querySelector("#" + BTN_ID)) {
      applyMode(getMode());
      return;
    }

    const btn = createButton();

    let mode = getMode();
    applyMode(mode);
    setButton(btn, mode);

    btn.addEventListener("click", () => {
      mode = nextMode(mode);
      applyMode(mode);
      setButton(btn, mode);
    });

    // Insert next to palette (light/dark toggle)
    const paletteToggle =
      headerInner.querySelector('button[aria-label*="Switch to"]') ||
      headerInner.querySelector("button.md-header__button.md-icon");

    if (paletteToggle && paletteToggle.parentNode) {
      paletteToggle.parentNode.insertBefore(btn, paletteToggle.nextSibling);
      return;
    }

    // Fallback: insert before search
    const search = headerInner.querySelector(".md-search");
    if (search) headerInner.insertBefore(btn, search);
    else headerInner.appendChild(btn);
  }

  // navigation.instant swaps pages via XHR, so DOMContentLoaded does not fire
  // again after the first load. document$ emits on both, which is the pattern
  // Material documents for exactly this.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
