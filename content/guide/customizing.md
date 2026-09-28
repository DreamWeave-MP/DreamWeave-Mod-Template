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
`search`, `offline_banner`, `content`, `comments`, `footer` and `extra_body`. The project page is
`templates/mod/`, split into `landing.html`, `install.html`, `compatibility.html` and `rail.html`.

The docs shell (`templates/docs/`, `sass/docs.sass`, `static/docs/docs.js`) is shared with other
DreamWeave sites that import it. Restyle it through tokens rather than editing it, and upgrades stay
a copy.

## Comments and analytics

Both are off, and a site built from the template never talks to DreamWeave's accounts.

Comments use [giscus](https://giscus.app), which stores them in your repository's Discussions.
Enable Discussions, install the giscus app on your repository, and copy the values it gives you:

```toml
[extra]
giscus = { repo = "you/your-repo", repo_id = "R_…", category = "General", category_id = "DIC_…", theme = "dark_dimmed" }
```

Page-view counts use [GoatCounter](https://www.goatcounter.com) with your own site code:

```toml
[extra]
goatcounter = "your-code"
```

Neither loads in the offline documentation inside archives.

## Search

Search runs in the browser over Zola's index, without a library. On docs pages it only searches that
project's docs. Press `/` to focus it. Turn it off with `build_search_index = false`.
