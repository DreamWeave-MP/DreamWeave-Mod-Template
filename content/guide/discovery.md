+++
title = "Discovery"
description = "How a tool starting from your page's address finds everything else."
weight = 70

[extra]
kind = "guide"
+++

Give a DreamWeave client your mod page's address and it finds the rest without reading the page's
HTML beyond one `<link>`, without JavaScript, without an API, and without asking anyone else.

## What the site publishes

| Path | What |
|---|---|
| `dreamweave.json` | The site index: every project's id, name, manifest URL, manifest SHA-256, last release date and channel heads |
| `dreamweave/projects/<id>.json` | One manifest per project: identity, releases, artifacts, install data |
| `schemas/*.schema.json` | The JSON Schemas for the above |

Paths are relative to the site's base URL, so a GitHub Pages project site publishes
`https://you.github.io/your-repo/dreamweave.json`. Manifest paths use the project id, not the page
path, so renaming a project's directory does not move its manifest.

## How it is advertised

Every page carries:

```html
<link rel="alternate" type="application/vnd.dreamweave.index+json" href="https://you.github.io/your-repo/dreamweave.json">
```

and every project page also carries its own manifest:

```html
<link rel="alternate" type="application/vnd.dreamweave.project+json" href="https://you.github.io/your-repo/dreamweave/projects/4d0c9f6e-….json">
```

A client that cannot or will not parse HTML tries `dreamweave.json` next to the address it was
given, then in each parent directory up to the origin's root. The
[protocol](@/guide/protocol/discovery.md) spells out the algorithm.

## Why not `/.well-known/`

`.well-known` URIs are defined at the root of an origin. A GitHub Pages project site does not own
`https://you.github.io/.well-known/`; the account's user site does, if it exists at all. A discovery
scheme that only works for sites at the root of a domain would leave out most mods. A relative path
plus a `<link>` works on every host, at every depth.

## Indexes

An index (St4sh, a community list, a search engine) needs only `dreamweave.json` to notice changes:
when a project's `manifest_sha256` is unchanged, its manifest is unchanged, and there is nothing to
fetch. An index may cache, mirror, categorize and rank what it finds. It is never where a project's
identity or release data lives; that stays on the project's own site, where the author publishes it.
