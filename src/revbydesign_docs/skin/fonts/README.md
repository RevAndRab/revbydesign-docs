# Fonts

**IBM Plex Sans** and **IBM Plex Mono**, copyright © 2017 IBM Corp.

Licensed under the **SIL Open Font License, Version 1.1**.
<https://github.com/IBM/plex>

Latin subsets only, `woff2`, 14–24 KB each. These are the same four files
revbydesign.studio serves from `public/fonts/`, so the site, the RevLearning
Tools and all three documentation sites share one set of faces.

| File | Used for |
|---|---|
| `plex-sans-400.woff2` | body text |
| `plex-sans-500.woff2` | the current item in navigation |
| `plex-sans-600.woff2` | headings and strong text, covering 600–700 |
| `plex-mono-400.woff2` | code, and the semantic pills |

## Why these are here rather than fetched

Material's `theme.font` option does not host anything — it emits a stylesheet
link to `fonts.googleapis.com`. Every documentation page was making that request
on every load, on a site that self-hosts specifically to avoid a third-party
font request and the consent question that comes with it (see
revbydesign.studio `docs/decisions.md` D006 and D029).

They are served from each documentation site's own origin rather than from
revbydesign.studio, so there is no cross-origin request either. Pointing the
docs at the marketing site would have traded one extra connection for another
and made the documentation stop setting type correctly whenever that site was
unavailable.

## Licence, and what is already satisfied

Checked rather than assumed. Every one of these four files carries, in its own
OpenType name table:

```
Copyright     Copyright 2017 / 2019 IBM Corp. All rights reserved.
License URL   http://scripts.sil.org/OFL
```

The OFL explicitly accepts machine-readable metadata inside the binary as a way
of carrying the copyright notice, so that obligation is met by the files
themselves, wherever they end up being served from. The root `LICENSE` and
`README.md` say the same thing in prose, so the MIT licence on the rest of the
package does not appear to claim them.

**Optional, and deliberately not done:** the full OFL 1.1 *text* is not here —
only the URL pointing at it. A strict reading of clause 2 wants the text
alongside. It is one file, `OFL.txt` from the IBM Plex repository, if anyone
ever wants the belt-and-braces version. The same is true of
revbydesign.studio's own `public/fonts/`.
