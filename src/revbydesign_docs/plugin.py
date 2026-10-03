"""The MkDocs plugin that delivers the RevByDesign documentation skin.

WHY A PLUGIN AND NOT A THEME

The obvious shape for a shared skin is a theme that declares
``extends: material``. It is the wrong one here. ``mkdocs-material`` inspects
``config.theme.name`` in its own code -- its search, tags and social plugins
among others -- and a site whose theme is no longer literally ``material``
stops being Material as far as those are concerned. Changing the theme name to
share a stylesheet would be trading a real feature for a cosmetic one.

The second obvious shape is ``theme.custom_dir``. Also wrong: ``custom_dir``
takes one path, Snap Studio Pro already uses its own for a commercial notice
that must appear on every page, and there is no portable way to point it at a
path inside site-packages.

So: a plugin. It leaves ``theme.name: material`` exactly as it was, adds its
stylesheet to the build, and inserts its template directory *below* whatever
the site already has -- so a product override always beats the shared layer,
which is the precedence you want and the opposite of what ``custom_dir`` would
have given.

WHAT IT DOES

1. Copies ``skin/css/revbydesign.css`` into the built site and registers it in
   ``extra_css``.
2. Supplies a footer line naming the studio and linking home, unless the site
   has set its own ``copyright``.

That is the whole plugin. It owns no templates, so it has no coupling to
Material's HTML and nothing to re-check when Material is upgraded. The
stylesheet speaks to Material only through the documented ``--md-*`` custom
properties.

VERSIONING

Sites pin this package by tag::

    revbydesign-docs @ git+https://github.com/RevAndRab/revbydesign-docs@v1.0.0

Nothing moves until a site moves it. That is the point: a change to the shared
layer should be a deliberate one-line commit in each repository, not something
that lands on three published sites the next time one of them happens to build.
"""

from __future__ import annotations

import os

from mkdocs.config import config_options as c
from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

__all__ = ["RevByDesignPlugin", "SkinConfig"]

_HERE = os.path.dirname(os.path.abspath(__file__))

SKIN_DIR = os.path.join(_HERE, "skin")
CSS_SOURCE = os.path.join(SKIN_DIR, "css", "revbydesign.css")

#: Where the stylesheet lands in the built site. Under ``assets/`` so it cannot
#: collide with a site's own ``docs/css/``, which is the directory the two
#: generated sites protect from their doc mirror and therefore the one place a
#: product is expected to keep its own CSS.
CSS_URI = "assets/revbydesign/revbydesign.css"

JS_SOURCE = os.path.join(SKIN_DIR, "js", "sidebar-mode.js")
JS_URI = "assets/revbydesign/sidebar-mode.js"

FONT_DIR = os.path.join(SKIN_DIR, "fonts")

#: Served beside the stylesheet, because the @font-face rules reference them
#: relative to it -- `url("fonts/plex-sans-400.woff2")` resolves against the CSS
#: file, not the page, so it works at any page depth without knowing the site's
#: base URL.
FONT_FILES = (
    "plex-sans-400.woff2",
    "plex-sans-500.woff2",
    "plex-sans-600.woff2",
    "plex-mono-400.woff2",
)


class SkinConfig(Config):
    """Options, all of which have a working default.

    A site should normally write ``- revbydesign`` and nothing else.
    """

    #: Ship the stylesheet. Off is for a site that wants only the footer line,
    #: or for bisecting a regression against the un-skinned build.
    css = c.Type(bool, default=True)

    #: Supply a footer line naming the studio and linking home. Skipped
    #: silently when the site already sets ``copyright``, so this can never
    #: overwrite something a human wrote.
    footer = c.Type(bool, default=True)

    #: Where the footer line points.
    home = c.Type(str, default="https://revbydesign.studio/")

    #: Ship the self-hosted IBM Plex files. Off only for a site that provides
    #: the faces itself; turning it off without doing that leaves the
    #: @font-face rules pointing at nothing and the site falls back to the
    #: system stack.
    fonts = c.Type(bool, default=True)

    #: Add the sidebar mode control to the header: normal -> wide -> focus.
    #: On by default because two of the three sites already shipped it and the
    #: third had its stylesheet but not its script. Off for a site that does
    #: not want a third button in its header.
    sidebar_toggle = c.Type(bool, default=True)

    #: The name in the footer line. Overridable because the studio's own name
    #: is the one thing in here a product might legitimately want to phrase
    #: differently.
    studio = c.Type(str, default="RevByDesign")


class RevByDesignPlugin(BasePlugin[SkinConfig]):
    """Adds the shared stylesheet and the footer line."""

    def on_config(self, config):
        """Register the stylesheet and, if wanted, the footer line."""
        if self.config.css:
            # Inserted at the front rather than appended. ``extra_css`` is
            # emitted in order and later wins, so a site's own
            # ``docs/css/product.css`` -- which is where it declares its accent
            # -- must come after the shared layer. Appending would have made
            # the shared layer override every product's identity, which is
            # exactly backwards.
            if CSS_URI not in config.extra_css:
                config.extra_css.insert(0, CSS_URI)

        if self.config.sidebar_toggle and JS_URI not in config.extra_javascript:
            # Appended rather than inserted. Nothing here depends on load
            # order, and a site's own scripts are more likely to want to run
            # first than last.
            config.extra_javascript.append(JS_URI)

        if self.config.footer and not config.copyright:
            # MkDocs renders templates with autoescape off and Material emits
            # ``{{ config.copyright }}`` directly, so this reaches the page as
            # markup. Checked against Material 9.6 and 9.7.
            config.copyright = (
                f'<span class="rbd-by">Documentation by </span>'
                f'<a class="rbd-home" href="{self.config.home}">'
                f"{self.config.studio}</a>"
            )

        return config

    def on_files(self, files, config):
        """Copy the stylesheet into the build.

        ``File.generated`` is the supported route for a file a plugin brings
        from outside ``docs_dir``; building a ``File`` by hand works too but
        has to be told four things about the build that this already knows.
        """
        if self.config.css:
            files.append(
                File.generated(config, CSS_URI, abs_src_path=CSS_SOURCE)
            )

        if self.config.sidebar_toggle:
            files.append(
                File.generated(config, JS_URI, abs_src_path=JS_SOURCE)
            )

        if self.config.css and self.config.fonts:
            for name in FONT_FILES:
                files.append(
                    File.generated(
                        config,
                        f"assets/revbydesign/fonts/{name}",
                        abs_src_path=os.path.join(FONT_DIR, name),
                    )
                )

        return files
