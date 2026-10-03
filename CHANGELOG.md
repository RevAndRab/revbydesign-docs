# Changelog

## v1.0.0 — 2026-10-03

First release. Replaces the hand-copied CSS layer in RevFramework, RevLearning
and Snap Studio Pro.

- Two custom Material colour schemes, `rbd-light` and `rbd-dark`, built from
  revbydesign.studio's own `tokens.css` and wired through Material's public
  `--md-*` properties. No `!important`, and no dependency on Material's
  internal class names for colour.
- Light is the landing scheme. Kept from the three sites' existing decision:
  documentation is read on work machines in daylight, and a reader moving
  between sites should not get a different scheme on each.
- Structure: 2px radius, hairlines in place of decorative shadow, the header
  and sidebar divided by a line rather than a fill, nav density preserved,
  section headings carrying a construction rule.
- Semantic pills: `Runtime`, `Editor`, `Complete only`.
- A footer line naming the studio and linking to revbydesign.studio, supplied
  only when a site has not set its own `copyright`.
- `checks/contrast.py`: 50 checks parsed out of the stylesheet.

One deliberate divergence from the main site's palette: `--rbd-text-faint` is
`#676b73` in light mode rather than `#6b6f77`. At the site's value it measures
4.498:1 against the sunken surface the footer uses — a fail by two thousandths.
Measured, not adjusted by eye.

## v1.0.1 — 2026-10-03

Three things browser verification found that review had not. All of them are
cases where configuring Material through its own properties had a consequence
further down that only showed up on a real page.

- **The content shell came back.** v1.0.0 dropped the full-width layout the
  hand-copied layer had, leaving Material's centred 61rem grid — which squeezes
  a reference table into two thirds of a 1440px screen. That was a density
  decision, not a decorative one, and density is what the brief protects. The
  content column keeps a 1050px measure and sits left, with the desktop gutters
  dropped on narrow viewports.
- **The search field was invisible.** Material derives the field's fill from
  the primary colour, and primary is now the page surface — which is what makes
  the header a neutral band instead of a coloured bar. The field came out
  exactly the colour of the header behind it, with no edge at all. It was there
  and focusable, and simply could not be seen. It now takes a sunken fill and a
  hairline, and the accent when focused. The results panel gets the surface and
  hairline that replaced Material's drop shadow.
- **The pill syntax in v1.0.0 did not work.** `[Runtime]{.pill .pill--runtime}`
  reached the page as that literal text: Python-Markdown's attr_list has no
  support for bare bracketed spans, because `[Runtime]` is not an inline
  element for attributes to attach to. Pills are now written as a raw
  `<span class="pill pill--runtime">`, which needs no markdown extension — so
  it behaves identically on all three sites whatever each enables — and
  degrades to the plain word on GitHub, where the generated sites' source
  READMEs are also read.

## v1.1.0 — 2026-10-03

**The documentation no longer fetches anything from Google.**

`theme.font` does not host fonts — it emits a stylesheet link to
`fonts.googleapis.com`. All three documentation sites were making that request
on every page load, on an estate that self-hosts IBM Plex specifically so there
is no third-party font request and no consent question (revbydesign.studio
D006, D029). The documentation had been quietly undoing that decision.

- IBM Plex Sans 400/500/600 and IBM Plex Mono 400 now ship with this package,
  Latin subsets, the same four `woff2` files revbydesign.studio serves. Each
  site serves them from its own origin, so there is no cross-origin request
  either — pointing the docs at revbydesign.studio would have swapped one extra
  connection for another and made them depend on the marketing site staying up.
- Sites set `theme.font: false` and this package supplies `--md-text-font` and
  `--md-code-font`.
- **Code is now IBM Plex Mono, not JetBrains Mono.** This reverses what the
  docs audit recommended. The audit was right that JetBrains is a better code
  face and that changing it touches every code block on three sites — but that
  was reasoning about a change with no benefit. Self-hosting gives it one:
  keeping JetBrains means obtaining and redistributing a second font family for
  a face difference nobody asked for, when the parent brand already runs Plex
  Mono and typography is explicitly something that should carry across.
- The 600 face covers weights 600–700, so Material's bold headings get a real
  semibold rather than a synthesised one.
- There is no italic face, so `<em>` is synthesised — which is already how
  revbydesign.studio behaves, so this matches the house rather than degrading
  from it.

Not done: the full SIL OFL 1.1 licence text is not in this repository. The
licence requires it to accompany redistributed fonts, and it is also missing
from revbydesign.studio's `public/fonts/`. See `skin/fonts/README.md`.
