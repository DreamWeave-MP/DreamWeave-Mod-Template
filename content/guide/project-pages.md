+++
title = "Project pages"
description = "Which file owns which fact, and every section a project page can show."
weight = 20

[extra]
kind = "guide"
+++

A project is a directory under `content/` with two files in it.

| File | Owns | Read by |
|---|---|---|
| `index.md` | The display name (`title`), the one-line summary (`description`), tags, and the prose | Zola, and the tooling for name and summary |
| `mod.toml` | Everything structured: identity, compatibility, relationships, components, install data, media, credits, releases | Zola, which renders the page from it, and CI, which validates it and writes the manifest |
| `mod.lock` | What each published release contains, including its archive's hash | Written by CI when a release tag is pushed; you never edit it |

Nothing is written twice. Renaming the mod means changing `title`; the id, the slug and the
release history do not move.

Everything else in the directory is the mod: its data directories, content files and
documentation. All of it ships in the archive. [Packages](@/guide/packages.md) says exactly what
goes in.

## The landing page

A project page is generated from `mod.toml`, `mod.lock` and the page's Markdown, by Zola alone, so
`zola serve` shows it as it will be published. It shows, in this order:

| Section | Appears when | Built from |
|---|---|---|
| Header and status strip | always | `title`, `description`, `type`, `status`, runtimes, Lua API, package format, license, channel heads |
| `overview` | always | the Markdown body of `index.md` |
| `media` | there is more than the header image | `[[media]]` |
| `install` | always | the package format, `[openmw]` or `[[components]]`, `[install]` notes |
| `compatibility` | anything is declared | runtimes, required content files, and the five relationship lists |
| `components` | there are explicit `[[components]]` | `[[components]]` and `[[groups]]` |
| `releases` | any release is declared | the three newest `[[releases]]` |
| `credits` | there are maintainers or credits | `[[maintainers]]` and `[[credits]]` |

Empty sections are not rendered, so a one-file library does not get a hollow components table.
To reorder or hide sections, list the ones you want in the page's frontmatter:

```toml
[extra]
sections = ["overview", "install", "compatibility", "releases"]
```

The rail beside the page shows the project's record, per-channel downloads with their digests,
links, the projects that depend on this one, and the machine-readable endpoints.

## Screenshots and video

```toml
[[media]]
file = "media/dusk.webp"
alt = "Warm lantern light across dark hills at dusk."
caption = "Dusk, with every lantern following the time of day."
category = "Gameplay"
featured = true
```

`file` is relative to the project directory. `alt` is required, because it is what a screen reader
says and nothing can invent it for you. One item may be `featured`; it becomes the header image,
and without one the first image is used. Thumbnails are resized at build time, so commit the
full-size file. With JavaScript, clicking a screenshot opens a viewer with arrow-key navigation;
without it, the link opens the image.

Videos are links, not embeds:

```toml
[[media]]
video = "https://www.youtube.com/watch?v=..."
alt = "A storm rolling over Balmora at night."
thumbnail = "media/storm-thumbnail.webp"
```

Nothing from the video host loads until someone clicks, and then it opens on the host's own site.
An embedded player would hand every visitor to a third party the moment the page loaded.

## Writing the body

The body is ordinary Markdown, plus these shortcodes:

| Shortcode | Renders |
|---|---|
| `{%/* callout(kind="note", title="...") */%}...{%/* end */%}` | A `note`, `tip`, `warning` or `danger` box |
| `{%/* features() */%}` a Markdown list `{%/* end */%}` | A grid; each item's leading **bold phrase** becomes its heading |
| `{%/* tree() */%}` an indented listing `{%/* end */%}` | A directory tree: two spaces per level, a trailing `/` marks a directory, two spaces before a note |
| `{{/* schematic(data_path="data/schematics/x.json") */}}` | A flow diagram drawn from data |
| `{{/* pipeline(data_path="data/pipeline/x.json") */}}` | Stages in a row joined by arrows, with pieces hanging off them; see the header of `templates/shortcodes/pipeline.html` for the file |
| `{{/* requires(name="...", url="@/lib/index.md", note="...") */}}` | A badge for something the project needs: a page of this site or any address, with an `icon` if you like and a `note` on what it is for |
| `{{/* requires_openmw() */}}` | A badge for the OpenMW it needs, linking to OpenMW's downloads. It reads `openmw` under `[runtimes]` in the page's `mod.toml`, so it follows it; `version="0.51"` names one instead |
| `{{/* api_signature(value="...") */}}` | A highlighted signature line |
| `{{/* image(src="/img/x.png", alt="...") */}}` and `{{/* figure(...) */}}` | An image, with or without a caption |

A pipeline, drawn from `data/pipeline/release.json`:

{{ pipeline(data_path="data/pipeline/release.json") }}

Requirement badges, on consecutive lines so they share a row. On a project page, leave out
`version` and `requires_openmw` shows the `openmw` requirement from its `mod.toml`:

```md
{{/* requires(name="Tallow", url="@/simplified/index.md", note="Scheduling") */}}
{{/* requires_openmw(version="0.49+") */}}
```

{{ requires(name="Tallow", url="@/simplified/index.md", note="Scheduling") }}
{{ requires_openmw(version="0.49+") }}

`<!-- more -->` ends the summary used on the catalog.

The V4 shortcodes `install_instructions`, `credits` and `usage_note` still work, so existing pages
keep rendering. `install_instructions` now points at the generated Install section rather than
drawing a second one.

## Documentation

Put a docs section inside the project directory, the way Candlelight does in `content/home/docs/`:

```toml
+++
title = "My Mod documentation"
sort_by = "weight"
template = "docs/section.html"
page_template = "docs/page.html"

[extra]
docs_root = true
docs_project_name = "My Mod"
docs_project_path = "@/home/index.md"
+++
```

Child pages and subsections inherit the docs layout: a recursive sidebar, breadcrumbs, a table of
contents, search scoped to the docs, and copy buttons on code. Link the docs from `mod.toml` with
`[links] documentation = "@/home/docs/_index.md"` and they get a header button. They also ship
inside the archive, rendered, under `<slug>-Documentation/`. Set `kind = "guide"` or `kind = "api"` in a
page's `[extra]` to label it.

A docs section lists its pages and subsections as cards under its own text. When that text already
links them, in an order and with context the cards cannot give, set `hide_child_cards = true` in the
section's `[extra]`. The sidebar still lists everything.
