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
