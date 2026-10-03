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
