# revbydesign-docs

The shared RevByDesign design layer for MkDocs Material documentation sites.

One stylesheet and a thirty-line plugin, consumed by every RevByDesign
documentation site. It replaces about 690 lines of CSS that had been copied by
hand into three repositories and had already drifted in three directions — one
of them carrying a stylesheet header that instructed the reader to *"keep edits
in sync"*, which is the sort of instruction that only exists because it does not
work.

**RevByDesign supplies the structure. The product supplies the colour.**

---

## What a site has to do

Two lines, plus its accent.

```yaml
# mkdocs.yml
theme:
  name: material          # unchanged — this is a plugin, not a theme
  palette:
    - scheme: rbd-light
      toggle: { icon: material/brightness-6, name: Switch to dark mode }
    - scheme: rbd-dark
      toggle: { icon: material/brightness-4, name: Switch to light mode }

plugins:
  - search
  - revbydesign

extra_css:
  - css/product.css       # the site's own accent, loaded after the skin
```

```txt
# requirements.txt
revbydesign-docs @ git+https://github.com/RevAndRab/revbydesign-docs@v1.1.5
```

```css
/* docs/css/product.css — the whole of a site's visual identity */
:root {
  --rbd-accent-light: #2f6ba4;
  --rbd-accent-dark: #6e9fd4;
  --rbd-accent-ink-light: #ffffff;
  --rbd-accent-ink-dark: #07111c;
}
```

Declaring no accent is a supported configuration. The site falls back to the
parent brand's own near-black / near-white, which is what revbydesign.studio
uses on pages belonging to the studio rather than to a product, and reads as
deliberate rather than broken.

## What it is

A plugin, not a theme, and not a `custom_dir`. Both of those were tried on
paper and rejected for reasons worth knowing before anyone changes it back:

- **A theme that `extends: material`** means `theme.name` is no longer
  `material`, and `mkdocs-material` checks that in its own plugins. Trading a
  real feature for a shared stylesheet is a bad trade.
- **`theme.custom_dir`** takes one path. Snap Studio Pro already uses its own
  for a commercial notice that must appear on every page, and there is no
  portable way to point `custom_dir` at a directory inside site-packages.

So the plugin adds its stylesheet to the build and gets out of the way. It owns
no templates, which means it has no coupling to Material's HTML and nothing to
re-verify when Material is upgraded.

The stylesheet talks to Material **only through the documented `--md-*` custom
properties**, and uses `!important` nowhere. That is the whole design. The layer
this replaces reached into internal class names — `.md-nav__item--active >
.md-nav__link::before` and about forty others — which is not a public API and
does change between minor versions. With three unpinned Material versions
across the estate, that was a live risk rather than an untidy one.

## Semantic pills

The one place documentation is allowed more colour than the main site, and the
only place colour carries meaning.

```html
<span class="pill pill--runtime">Runtime</span>        <!-- ships into a player build -->
<span class="pill pill--editor">Editor</span>          <!-- editor-only, never in a build -->
<span class="pill pill--sku">Complete only</span>      <!-- not in a single-system SKU -->
```

A raw span, not `attr_list`. Python-Markdown's attr_list does not support bare
bracketed spans — `[Runtime]{.pill}` reaches the page as that literal text,
because `[Runtime]` is not an inline element for the attributes to attach to.
It works on strong, emphasis and code spans, and a status badge is none of
those.

Raw HTML also needs no markdown extension, so it behaves the same on all three
sites whatever each enables, and it degrades to the plain word on GitHub —
which matters, because RevFramework's pages are generated from source READMEs
that are read there too.

Three categories, because three are what the estate actually distinguishes.
**Add a fourth only when something has asked for it twice.**

Every pill states its meaning in words, so colour is reinforcement and never
the carrier — a reader who cannot distinguish the hues loses nothing. The pills
do not borrow a product accent: an accent says *whose* something is, a pill says
*what* it is, and sharing a hue between them makes both weaker. `Complete only`
is a constraint rather than a category, so it takes the brand's inverted
neutral rather than a third hue.

## Verification

```bash
python checks/contrast.py
```

50 checks, parsed out of the stylesheet rather than copied from it — change a
hex and it re-measures the new one. Covers body, dimmed and faint text on both
the page and the sunken surface, the focus ring, each pill's label over its own
wash and its border against the page, and the link colour for **all ten**
product accents in both schemes, so a site added later is already known to pass.

Text is held to 4.5:1 and meaningful non-text to 3:1. Hairlines are measured
and reported but never failed: a 1px rule that divides regions without
conveying information is outside the requirement, and raising it to 3:1 would
make the whole brand louder.

## Upgrading a site

Change the tag in that site's `requirements.txt`, and nothing else moves.

That is deliberate. A shared layer that updates everywhere at once is a shared
layer that can break three published sites from one commit, and these three
sites publish by three different mechanisms with three different people-shaped
gates in front of them. Three small deliberate commits is the feature.

## Licence

MIT — the stylesheet, the plugin and the checks.

**Except the fonts.** `skin/fonts/*.woff2` are IBM Plex Sans and IBM Plex Mono,
copyright © 2017, 2019 IBM Corp., under the [SIL Open Font License
1.1](https://scripts.sil.org/OFL). Redistributed unmodified as Latin subsets.
Their name tables carry the IBM copyright and the licence URL, so attribution
travels with the files themselves rather than depending on anyone reading this.
