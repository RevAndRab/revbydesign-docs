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

## Outstanding

**The full OFL 1.1 licence text is not in this repository.** The licence
requires it to accompany redistributed fonts, and these files are redistributed
both from here and from revbydesign.studio's `public/fonts/`, where it is also
missing. One file, `OFL.txt`, copied from the IBM Plex repository, in both
places.
