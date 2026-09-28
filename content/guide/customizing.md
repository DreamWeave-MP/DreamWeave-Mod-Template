+++
title = "Customizing"
description = "Palettes, brand tokens, fonts, templates, comments and analytics."
weight = 100

[extra]
kind = "guide"
+++

The template owns presentation, navigation and the machine-readable output. You own identity,
content and branding. Branding is meant to be possible without forking a single template.

## Color

```toml
[extra]
palette = "teal"        # purple (default), teal, gold, ember or moss
accent = "#7fded0"      # optional: any #rrggbb, overriding the palette's accent
```

The accent's strong, soft and line shades are derived from it, so one value recolors buttons,
borders, status bars, focus rings and diagrams consistently.

## Tokens

For anything more, `sass/brand.sass` is yours. It loads last and the template never changes it:

```sass
:root
  --dw-accent: #d6a7ff
  --dw-bg-0: #0d0a12
  --dw-font-display: "Oxanium", var(--dw-font-mono)
  --dw-width-page: 1800px
```

Every token is in `sass/_tokens.sass`: surfaces (`--dw-bg-0` to `--dw-bg-3`), text, lines, accent,
status colors (`--dw-ok`, `--dw-warn`, `--dw-danger`, `--dw-info`), fonts, sizes, widths and code
colors. Change tokens before writing selectors; tokens keep the pages, the docs and the diagrams
consistent with each other.

## Fonts

No web font loads by default: body text uses the system sans stack and structure uses the system
monospace stack. The bundled display fonts are available with:

```toml
[extra]
font_override = "oxanium"         # avqest, gal-basic, mystic-cards, deja-vu-sans-mono, demonic-letters, oxanium
font_override_titles_only = true  # only headings and titles
```

## Navigation

```toml
[extra]
logo_text = "Ashlands Lighting"
menu_items = [
    { name = "Candlelight", url = "@/home/index.md" },
    { name = "Guide", url = "@/guide/_index.md" },
    { name = "Discord", url = "https://discord.gg/…" },
]
footer_text = "Made in the Ashlands"
favicon = "img/favicon.png"
```

## Templates

Everything under `templates/` can be overridden by editing it; Zola has no theme layer in between.
`base.html` defines the blocks every page fills: `title`, `extra_head`, `discovery`, `header`,
`search`, `offline_banner`, `content`, `footer` and `extra_body`. Comments are
`templates/comments.html`, included at the end of each page's body column. The project page is
`templates/mod/`, split into `landing.html`, `install.html`, `compatibility.html` and `rail.html`.

The docs shell (`templates/docs/`, `sass/docs.sass`, `static/docs/docs.js`) is shared with other
DreamWeave sites that import it. Restyle it through tokens rather than editing it, and upgrades stay
a copy.

## Comments

Project pages end in a **Discussion** section: a thread in your repository's GitHub Discussions,
embedded with [giscus](https://giscus.app) and loaded live in the reader's browser. Nothing about the
comments is part of the built site; a new comment appears immediately, without a rebuild.

```toml
[extra.comments]
enabled = true
category = "General"      # a Discussions category of your repository
# reactions = true        # emoji reactions on each thread's first post
# theme = "dark_dimmed"   # any giscus theme; the default is DreamWeave's, in your palette
# mapping = "pathname"    # how a page finds its thread: pathname, title or og:title
```

It needs Discussions enabled on the repository and the [giscus app](https://github.com/apps/giscus)
installed. The build asks giscus for your repository's and category's ids, for the repository named
by `github_username` and `github_project`, which CI checks is the one it runs in. That is why there
are no ids to paste, and why a copied `config.toml` cannot post into someone else's Discussions. If
giscus is not installed yet, or unreachable, the build warns and leaves comments out; a category
name that does not exist is an error.

Threads are matched by page path, as in V3, so existing threads keep their pages. Changelogs and the
network page have no thread. Docs pages have none unless their docs root sets
`docs_comments = true`, and any page can opt out with `comments = false` in its `[extra]`. The
offline documentation inside archives never loads comments.

The DreamWeave giscus theme is served from your site (`giscus/<palette>.css`) and applies on the
published site. A local preview cannot show it: giscus's iframe lives on a public origin, and browsers
block public pages from fetching files on your machine, so previews use GitHub's dark theme and say
so above the thread.

## Analytics

Page-view counts use [GoatCounter](https://www.goatcounter.com) with your own site code, and are off
until you set it:

```toml
[extra]
goatcounter = "your-code"
```

A site built from the template never reports to DreamWeave's analytics, and the offline
documentation never loads them.

## Search

Search runs in the browser over Zola's index, without a library. On docs pages it only searches that
project's docs. Press `/` to focus it. Turn it off with `build_search_index = false`.
