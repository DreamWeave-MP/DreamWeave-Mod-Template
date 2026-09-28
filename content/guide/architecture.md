+++
title = "Architecture"
description = "What each part owns, what gets generated, how the protocol evolves, and the designs we rejected."
weight = 120

[extra]
kind = "reference"
+++

The template is the publishing edge of the DreamWeave mod network: publish once, read by people,
consumed deterministically by machines, hosted anywhere. This page says how, and why it is this
shape and not another.

## Data ownership

| Information | Lives in | Written by |
|---|---|---|
| A project's display name, summary, prose | `content/<p>/index.md` | the author |
| A project's identity and structured facts | `content/<p>/mod.toml` | the author |
| What a published release contains, including digests | `content/<p>/mod.lock` | CI, when a release tag is pushed, as a `github-actions[bot]` commit |
| The site's URL, title, repository, palette | `config.toml` | the author |
| Presentation | `templates/`, `sass/`, `static/` | the template; `sass/brand.sass` belongs to the author |
| Protocol documents | `static/dreamweave.json`, `static/dreamweave/` | generated, gitignored |
| Archives | `dist/` | generated, gitignored |
| The protocol's structure | `static/schemas/` | the template |

Every structured fact is written once. Pages and manifests are built from the same files: Zola's
templates read `mod.toml` and `mod.lock` to render a page, CI's tooling reads them to write the
manifest, and the tests check that the two say the same thing. That is also why an author's plain
`zola serve` shows the page as it will be published.

## What `modManifest` represents

A project manifest is one project's claim about itself: who it is, what it has released, what each
release contains and needs, and where to get it. It is written by the project's own tooling and
served from the project's own site, and it is the only authority for those claims.

- **Project identity** is `id`, a UUID chosen once. It does not come from a name, a GitHub account, a
  host, a URL, a Nexus id, a domain or a key, so it survives changes to all of them.
- **Release identity** is the project id plus a version, compared under the project's declared scheme.
- **Artifact identity** is a SHA-256. File names and URLs are locations.
- **Channels** are labels on releases; a channel's head is its newest available release. Nothing is
  intrinsically "latest".
- **Dependencies** name project ids or capabilities, with AND-only constraints evaluated under the
  target's scheme; `requires`, `recommends`, `conflicts`, `compatible` and `replaces` stay distinct.
- **Components** are declarative: required, default, grouped with a selection rule, requiring or
  conflicting with each other. No scripts.
- **Discovery** is a `<link>` on every page to `dreamweave.json` at the site's base URL, with a
  path-walking fallback that needs no HTML at all.
- **Mirrors** serve bytes by digest and are never trusted; clients verify against the manifest.
- **Provenance** is the digest recorded before publication, the source revision, and optionally a
  keyless Sigstore signature tying the archive to the workflow that built it. Trust is the client's
  decision.

## What each part owns

| Part | Owns |
|---|---|
| `./buildSite` | Validation, packaging, recording releases, the protocol documents. It runs only in CI; authors never need Python |
| Zola | Rendering pages from `mod.toml` and `mod.lock`, the search index, resizing images, the offline documentation render |
| StroggForge's Rust workflows | Testing, building, signing and scanning programs, once per platform, when a project is `format = "binary"`; testing a `format = "crate"` library and publishing it to crates.io |
| The workflow | Running the above on every push and tag, publishing releases, deploying Pages |
| Client software (CHIMERA and others) | Discovery, trust policy, dependency resolution, choosing releases, downloading, verifying, installing |
| St4sh and other indexes | Crawling, caching, search, curation, mirroring. Not identity, not release data |

## How it evolves

`schema_version` is a major version; within it the core is frozen and unknown core fields are
errors. New data goes into namespaced extensions, which clients ignore unless the release marks them
critical, and graduates into the core at the next major version. A client that meets a newer major
version stops and says so. The V4 template's per-release manifest schema stays at its published URL.

## Rejected designs

**A central registry.** It would be simpler to allocate ids and host manifests in one place, and it
would make DreamWeave the thing every mod depends on staying online, funded and fair. Ids are UUIDs
because they need no allocator; manifests live on project sites because that is where authors
already publish.

**URLs as identity.** Go does this with import paths. A mod that moves from GitHub Pages to St4sh to
its own domain would become three mods.

**Scraping HTML.** The page is for people and changes whenever the design does. Tools read JSON with
a schema.

**A DreamWeave certificate authority.** A signature proves who signed, not whether to trust them.
A central trust root would be a central registry with extra steps.

**Install scripts.** FOMOD's C# installers and OMOD's scripts show where that ends. A manifest
describes directories, content files and settings; a client performs them. Code execution needs its
own protocol and security model, not a field.

**A required St4sh, CHIMERA or Nexus.** Each is a reader or an integration. A mod published with
the template stays readable, installable and verifiable if every one of them is gone.

**`.well-known` discovery.** It only exists at an origin's root, which GitHub Pages project sites do
not own.

**Compressed archives.** Deflate differs between zlib builds, so a compressed archive only
reproduces on a machine with the same one. Stored archives cost 5% on an audio-heavy mod, and any
machine rebuilds them byte for byte.

**Hashes taken from the host.** Recording whatever digest GitHub reports would make the manifest's
hash a property of the download location, which is exactly what a hash is supposed to be independent
of. CI records the digest of the archive it built from the tag, before publishing it, and re-running
the tag's job reproduces it.

**An initializer.** A setup script that rewrites the template drifts from the files it rewrites and
becomes the first thing to break. The files are the configuration; validation says what is missing.
