+++
title = "Customizing"
description = "Palettes, brand tokens, fonts, the logo and hero art, templates, comments and analytics."
weight = 100

[extra]
kind = "guide"
+++

The template owns presentation, navigation and the machine-readable output. You own identity,
content and branding. Branding is meant to be possible without forking a single template.

## Color

```toml
[extra]
palette = "teal"        # purple (default), teal, gold, ember, moss, umber, grove, prism, slate,
                        # crimson, indigo, azure or frost
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
status colors (`--dw-ok`, `--dw-warn`, `--dw-danger`, `--dw-info`), fonts, the type scale
(`--dw-step--2` to `--dw-step-5`), spacing (`--dw-space-1` to `--dw-space-8`), radii, shadows,
widths and code colors. Change tokens before writing selectors; tokens keep the pages, the docs and
the diagrams consistent with each other.

The palettes share one lightness ladder, so a surface, a line or muted text is the same step from
the page in every palette, and all of them pass WCAG AA for text. If you replace the surfaces,
keep them in that order, darkest first, and check the text against them.

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

On a phone the header keeps the logo and folds the rest: search behind a button, and four menu
items or more behind a **Menu** button. Three or fewer stay a row of links that scrolls sideways
if it has to. Without JavaScript nothing folds.

To spell the logo with markup, say with one letter in the accent, set `logo_html` as well. It is
used as written, so keep it to a few inline elements; `logo_text` stays the plain name everywhere
else:

```toml
[extra]
logo_text = "Ashlands Lighting"
logo_html = '<span>Ash<span class="accent">lands</span> Lighting</span>'
```

```sass
// sass/brand.sass
.accent
  color: var(--dw-accent)
```

A project page, or the catalog's `content/_index.md`, can do the same for its hero title with
`title_html` under `[extra]`. The page's `title` is still what the browser tab, search and the
catalog show.

## Hero art

The catalog and every project page open on a hero: the title, the summary, the downloads and the
facts. A site can draw its own art behind it, a canvas, a WebGL scene or an SVG, without forking a
template:

```toml
[extra.hero]
script = "js/hero.js"                    # an ES module in static/, or an https:// URL
preload = ["js/vendor/scene.module.js"]  # optional: modules it imports, fetched in parallel
home = true                              # on the catalog (default true)
projects = true                          # on project pages (default true)
```

Each hero it applies to gets the class `dw-hero--art` and an empty element for the script to fill:

```html
<div class="dw-hero__art" data-dw-hero-art data-hero-page="project" data-hero-project="candlelight" aria-hidden="true"></div>
```

It covers the whole hero, behind the text. `data-hero-page` is `catalog` or `project`, and a project
page names its slug, so one script can draw each page differently. The script loads as a module
after the page, so the page never waits for it. A project page leaves the art out with
`hero = false` under `[extra]` in its `index.md`, and the offline documentation in archives never
loads it.

The art is decoration: without JavaScript, or when the script fails, the hero is the template's
own, so style a still for it in `sass/brand.sass` under `.dw-hero--art` if the plain one does not
suit. Read colors from the tokens (`getComputedStyle(document.documentElement).getPropertyValue("--dw-accent")`)
rather than hard-coding them, and draw one still frame under `prefers-reduced-motion: reduce`.

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

Threads are matched by page path, as in V4, so existing threads keep their pages. Changelogs and the
network page have no thread. Docs pages have none unless their docs root sets
`docs_comments = true`, and any page can opt out with `comments = false` in its `[extra]`. The
offline documentation inside archives never loads comments.

The DreamWeave giscus theme is served from your site (`giscus/<palette>.css`) and applies on the
published site. A plain `zola serve` has no thread at all, because the ids come from CI's lookup. A
CI build served from your own machine does, but cannot show the theme: giscus's iframe lives on a
public origin, and browsers block public pages from fetching files on your machine, so it uses
GitHub's dark theme and says so above the thread.

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
