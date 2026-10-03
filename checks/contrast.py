"""Verifies the skin's contrast ratios by reading the stylesheet.

Run with ``python checks/contrast.py``. Exits non-zero on a failure.

This parses ``revbydesign.css`` rather than carrying its own copy of the
values. A check with the hexes typed into it a second time verifies that
someone can type, and goes stale the first time the stylesheet changes without
it -- which is the same copy-and-drift failure this whole package exists to
end. Change a colour in the stylesheet and this re-measures the new one.

What it checks, and why each bar:

  4.5:1  text against the surface it sits on (WCAG AA, normal text). Covers
         body text, dimmed text, faint text, link colour for every product
         accent, and each pill's label over its own wash.
  3.0:1  the focus ring and the pill borders against the page (WCAG AA for
         non-text that carries meaning). The focus ring is an accessibility
         feature; a pill border is what survives when the wash does not, on a
         monochrome printer or in forced-colors mode.

Hairlines are measured and reported but not failed: a 1px rule that divides
regions without conveying information is outside the non-text contrast
requirement, and raising it to 3:1 would make the whole brand louder.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CSS = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "revbydesign_docs"
    / "skin"
    / "css"
    / "revbydesign.css"
)

# Every product accent that currently exists, read off revbydesign.studio's
# src/styles/products.css. Only three have documentation sites today; the rest
# are here so that a site added later is already known to pass.
PRODUCT_ACCENTS = {
    "revframework": ("#2f6ba4", "#6e9fd4"),
    "snap-studio-pro": ("#8a5a06", "#e8a33d"),
    "loggerpro": ("#257145", "#6fbf8f"),
    "revdiagnostics": ("#0d6f7c", "#4fc4d4"),
    "skint": ("#6f4493", "#b98ed6"),
    "revlearning": ("#434fa3", "#7c8ce0"),
    "revlearning-tools": ("#4e6e25", "#8fb85c"),
    "moniker": ("#8f4621", "#d4845c"),
    "orda": ("#962f1d", "#d25c45"),
    "dizzy": ("#7d5f04", "#e0b63d"),
}


# --- colour ----------------------------------------------------------------


def _channel(value: float) -> float:
    value /= 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = (_channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def parse_hex(value: str):
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def contrast(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg, alpha: float, bg):
    """Flatten a translucent fill onto an opaque surface."""
    return tuple(alpha * f + (1 - alpha) * b for f, b in zip(fg, bg))


# --- reading the stylesheet ------------------------------------------------


def scheme_block(css: str, scheme: str) -> str:
    """The body of the `[data-md-color-scheme='<scheme>'] { ... }` rule."""
    start = css.index(f"[data-md-color-scheme='{scheme}'] {{")
    end = css.index("\n}", start)
    return css[start:end]


def tokens(css: str, scheme: str) -> dict:
    """The `--rbd-*` literal colours declared by one scheme."""
    found = {}
    for name, value in re.findall(
        r"(--rbd-[a-z-]+):\s*(#[0-9a-fA-F]{3,6});", scheme_block(css, scheme)
    ):
        found[name] = parse_hex(value)
    return found


def pill(css: str, scheme: str, modifier: str):
    """A pill's label colour and the wash it sits on, as written."""
    rule = re.search(
        r"\[data-md-color-scheme='"
        + re.escape(scheme)
        + r"'\] \.md-typeset \.pill--"
        + re.escape(modifier)
        + r"\s*\{(.*?)\}",
        css,
        re.S,
    )
    if rule is None:
        raise AssertionError(f"no .pill--{modifier} rule for {scheme}")
    body = rule.group(1)

    colour = re.search(r"color:\s*(#[0-9a-fA-F]{3,6});", body)
    wash = re.search(
        r"background:\s*rgba\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)[,\s/]+([\d.]+)\s*\)", body
    )
    if colour is None or wash is None:
        return None
    r, g, b, a = wash.groups()
    return parse_hex(colour.group(1)), ((int(r), int(g), int(b)), float(a))


# --- font weights -----------------------------------------------------------

def shipped_weights(css: str) -> set:
    """Every weight an @font-face in this stylesheet can actually serve."""
    served = set()
    for value in re.findall(r"@font-face\s*\{[^}]*?font-weight:\s*([^;]+);", css, re.S):
        parts = value.strip().split()
        if len(parts) == 2:                      # a range, e.g. "600 700"
            served.update(range(int(parts[0]), int(parts[1]) + 1, 100))
        else:
            served.add(int(parts[0]))
    return served


def declared_weights(css: str) -> dict:
    """Numeric font-weights this stylesheet asks for, outside @font-face."""
    without_faces = re.sub(r"@font-face\s*\{[^}]*\}", "", css, flags=re.S)
    asked = {}
    for m in re.finditer(r"font-weight:\s*(\d{3})\s*;", without_faces):
        line = without_faces[: m.start()].count("\n") + 1
        asked.setdefault(int(m.group(1)), []).append(line)
    return asked


# --- code highlighting ------------------------------------------------------

#: The six Material defines on `:root` in terms of properties a scheme overrides.
#: A var() inside a custom property is substituted where it is DECLARED, so these
#: resolve against `:root`'s light-mode values and inherit down as literals --
#: overriding what they point at does nothing. Every scheme must restate them.
#: Leaving them out made code unreadable in dark mode on three published sites:
#: identifiers at #36464e and comments at rgba(0,0,0,0.54) on a near-black block.
DERIVED_HL = (
    "--md-code-hl-name-color",
    "--md-code-hl-operator-color",
    "--md-code-hl-punctuation-color",
    "--md-code-hl-comment-color",
    "--md-code-hl-generic-color",
    "--md-code-hl-variable-color",
)


def declarations(css: str, scheme: str) -> dict:
    """Every `--name: value;` in one scheme block, values unresolved."""
    found = {}
    for name, value in re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", scheme_block(css, scheme)):
        found[name] = value.strip()
    return found


def resolve(decls: dict, value: str):
    """Follow `var(--x)` through the block until a hex falls out.

    Two hops is all this palette ever needs -- `--md-code-hl-name-color` ->
    `--md-code-fg-color` -> `--rbd-text` -> a hex. Resolving it rather than
    hardcoding the destination means renaming a token cannot leave this check
    quietly measuring the old one.
    """
    for _ in range(6):
        value = value.strip()
        if value.startswith("#"):
            return parse_hex(value)
        m = re.match(r"var\(\s*(--[a-z0-9-]+)", value)
        if not m or m.group(1) not in decls:
            return None
        value = decls[m.group(1)]
    return None


def code_tokens(css: str, scheme: str):
    """(code background, {property: rgb}) for every highlight colour declared."""
    decls = declarations(css, scheme)

    missing = [d for d in DERIVED_HL if d not in decls]
    if missing:
        raise AssertionError(
            f"{scheme} does not restate {missing}. Material declares these on :root in terms of "
            "properties this scheme overrides, so they will resolve against its light defaults "
            "and inherit as literals. This is the bug that made code blocks unreadable."
        )

    background = resolve(decls, decls["--md-code-bg-color"])
    tokens = {}
    for name, value in decls.items():
        # `--md-code-hl-color` and its --light variant are the *background* of a
        # highlighted line, not a token colour, so the 4.5:1 text bar does not
        # apply to them. Everything else under this prefix is text.
        if name == "--md-code-hl-color" or name.endswith("--light"):
            continue
        if name.startswith("--md-code-hl-"):
            rgb = resolve(decls, value)
            if rgb is not None:
                tokens[name] = rgb
    return background, tokens


# --- the audit -------------------------------------------------------------


def main() -> int:
    css = CSS.read_text(encoding="utf8")

    results = []

    def check(label, fg, bg, need=4.5, fail=True):
        results.append((label, contrast(fg, bg), need, fail))

    for scheme in ("rbd-light", "rbd-dark"):
        t = tokens(css, scheme)
        missing = {
            "--rbd-bg",
            "--rbd-bg-sunken",
            "--rbd-text",
            "--rbd-text-dim",
            "--rbd-text-faint",
            "--rbd-focus",
        } - t.keys()
        if missing:
            raise AssertionError(f"{scheme} is missing {sorted(missing)}")

        bg, sunken = t["--rbd-bg"], t["--rbd-bg-sunken"]
        tag = scheme.replace("rbd-", "")

        # Body, dimmed and faint text, on both the page and the sunken surface
        # the footer and code blocks use.
        for name in ("--rbd-text", "--rbd-text-dim", "--rbd-text-faint"):
            check(f"{tag:<5} {name:<18} on bg", t[name], bg)
            check(f"{tag:<5} {name:<18} on sunken", t[name], sunken)

        # The focus ring carries meaning, so 3:1 as non-text.
        check(f"{tag:<5} focus ring         on bg", t["--rbd-focus"], bg, 3.0)

        # Hairlines: measured, never failed. See the module docstring.
        for name in ("--rbd-line", "--rbd-line-strong"):
            check(f"{tag:<5} {name:<18} on bg", t[name], bg, 1.0, fail=False)

        # Links take the product accent, so every accent has to clear AA as
        # text -- including the achromatic fallback a site with none gets.
        index = 0 if scheme == "rbd-light" else 1
        for product, pair in PRODUCT_ACCENTS.items():
            check(f"{tag:<5} link accent {product:<18}", parse_hex(pair[index]), bg)
        check(
            f"{tag:<5} link accent {'(no accent set)':<18}",
            t["--rbd-text"],
            bg,
        )

        # Pills: the label over its own wash, and the border against the page.
        for modifier in ("runtime", "editor"):
            got = pill(css, scheme, modifier)
            if got is None:
                raise AssertionError(f"could not read .pill--{modifier} for {scheme}")
            label, (wash, alpha) = got
            check(
                f"{tag:<5} pill--{modifier:<12} label on wash",
                label,
                composite(wash, alpha, bg),
            )
            check(f"{tag:<5} pill--{modifier:<12} border on bg", label, bg, 3.0)

        # The SKU pill is the inverted neutral: page colour on text colour.
        check(f"{tag:<5} pill--sku          inverted", bg, t["--rbd-text"])

        # Syntax highlighting is text on the code surface, so it is held to the
        # same 4.5:1 as prose. `code_tokens` raises outright if a scheme has
        # stopped restating the derived six.
        code_bg, highlights = code_tokens(css, scheme)
        for name in sorted(highlights):
            label = name.replace("--md-code-hl-", "").replace("-color", "")
            check(f"{tag:<5} code {label:<14} on code bg", highlights[name], code_bg)

    failures = 0
    for label, ratio, need, fail in results:
        ok = ratio >= need
        if not ok and fail:
            failures += 1
            flag = "FAIL"
        elif not ok:
            flag = "note"
        else:
            flag = "ok  "
        print(f"{flag} {ratio:6.2f}:1  (needs {need:4.1f})  {label}")

    # A weight we ask for but cannot serve is silently rounded by the browser,
    # which is how h1 and h2 came to render identically for two releases. Not a
    # contrast question, so it is reported on its own rather than squeezed into
    # a ratio column where a failure would have read as a statement of fact.
    served = shipped_weights(css)
    weights = declared_weights(css)
    print()
    for weight, lines in sorted(weights.items()):
        where = ", ".join(str(l) for l in lines[:4])
        if weight in served:
            print(f"ok    font-weight {weight}  servable  (line {where})")
        else:
            failures += 1
            print(f"FAIL  font-weight {weight}  NO @font-face can serve it  (line {where})")
            print(f"      The browser rounds it silently. Ship the face, or ask for "
                  f"one of {sorted(served)}.")

    print()
    print(f"{len(results) + len(weights)} checks, {failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
