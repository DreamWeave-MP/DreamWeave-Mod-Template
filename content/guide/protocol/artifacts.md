+++
title = "Artifacts"
description = "Digests, sources, verification, signatures, what is inside an archive, and Jess packages and applications."
weight = 40

[extra]
kind = "reference"
+++

## Fields

| Field | Meaning |
|---|---|
| `id` | Token, unique within the release. |
| `format` | `flat`, `bain` or `fomod`: game data, laid out as [Installation](@/guide/protocol/installation.md) describes. `binary`: a program built for one platform. `crate`: a Rust crate, as crates.io serves it. `jpk`: a Jess package archive. See [Jess packages](#jess-packages). `jsw`: a packed Jess workspace, an application. See [Jess applications](#jess-applications). |
| `filename` | A suggested file name. Not identity. |
| `media_type` | `application/zip`; `application/gzip` for `crate`; `application/vnd.jess.jpk` for `jpk`; `application/vnd.jess.jsw` for `jsw`. |
| `size` | Bytes. |
| `digests` | `{ "sha256": "<64 lowercase hex>" }`. Further algorithms MAY be added; `sha256` is always present. |
| `platform` | `{ os, arch, variant? }`, required when `format` is `binary`: the one platform the program runs on. See [Programs](#programs). |
| `jess` | `{ package, jess_api, content_digest, dependencies }`, required when `format` is `jpk` and not allowed otherwise: what the Jess package inside is. See [Jess packages](#jess-packages). |
| `jess_workspace` | `{ package, builtin, default?, targets, commands, packages }`, required when `format` is `jsw` and not allowed otherwise: what the application inside runs and holds. See [Jess applications](#jess-applications). |
| `layout` | *Optional.* Paths inside the archive: `release_document`, `documentation` (the offline docs' entry page), `installer` (`fomod/ModuleConfig.xml`). |
| `sources` | At least one `{ url, kind, name? }`. `kind` is `publisher` for locations the project operates, `mirror` otherwise. |
| `signatures` | `[{ format, url, issuer?, identity? }]`. May be empty. |

## Identity

Two artifacts with the same SHA-256 are the same artifact, whatever their file names, URLs or the
releases that list them. A cache or mirror MAY key storage by digest alone.

## Downloading

1. Choose sources in any order. A client MAY prefer `publisher` sources, remembered-fast mirrors, or
   a local cache; the order in the list carries no meaning.
2. Download one.
3. Reject the bytes unless their length equals `size` and their SHA-256 equals `digests.sha256`.
   Do not open, extract or execute rejected bytes.
4. On rejection or failure, try the next source. When none are left, fail.

A client MUST NOT extract an archive before step 3 succeeds. Extraction MUST refuse entries with
absolute paths, `..` segments, or symlinks, whatever the manifest says.

## Signatures

`format: "sigstore-bundle"`: `url` is a Sigstore bundle for the artifact; `issuer` is the OIDC
issuer and `identity` the certificate identity to require: the GitHub Actions workflow that signed
the artifact, at its ref. That is often a reusable workflow that many repositories call, such as
StroggForge's `modGlobalBuild`, so the identity alone does not name the repository. A client MUST
also require the certificate's workflow repository to be the one the release's `source.repository`
names, and SHOULD require its workflow ref to be `refs/tags/` and the release's `source.tag`. A client that verifies all of that learns
that this workflow, run for this repository, produced these bytes. It learns nothing about whether
to trust that repository.

A client MAY require signatures by policy. A missing signature MUST NOT be treated as a failed
digest: the digest already establishes integrity against the manifest.

## Archive contents

Every archive is a zip. Archives built by the DreamWeave Mod Template are stored (not compressed),
sorted, dated 1980-01-01 and byte-reproducible from their source commit; the protocol does not
require any of that, only that the digest match.

At the root of a `flat`, `bain` or `fomod` archive:

- the project's files, laid out per `format`;
- `dreamweave.release.json`, the [release payload](@/guide/protocol/manifest.md#release-payload);
- `<slug>-Documentation/`, optionally: the project's pages rendered as self-contained HTML, named
  by the artifact's `layout.documentation`;
- `<slug>-dwmod.toml`, optionally: the project's `mod.toml` as its site had it;
- `fomod/`, for `format: "fomod"`: a ModConfig 5.0 installer generated from the components.

## Programs

A release of a tool built from source has one `binary` artifact per platform, each with its
`platform`:

| Field | Values |
|---|---|
| `os` | `windows`, `macos`, `linux`, `android` |
| `arch` | `x86_64`, `aarch64` |
| `variant` | *Optional.* `portmaster`: a build for PortMaster's handheld ports, drawn to the framebuffer. `muos`: that build packaged as a muOS app. |

A client offers the artifact whose `os` and `arch` match the machine it runs on and that has no
`variant`, unless it knows it runs in that variant's environment, and offers none if nothing
matches: a Windows build is not a fallback for Linux, and a handheld build is not a desktop one. A
client MUST skip variants it does not know.

The release's `platforms` lists its desktop builds: `windows`, `macos` and `linux` without a
variant. Android and handheld builds appear only on their artifacts.

A binary archive holds the program and the files its publisher ships beside it, and nothing
DreamWeave adds; there is no release payload inside. It is not game data. A client MUST NOT install it
into a game's data directories, and MUST NOT run anything from it as part of installing. Unpacking
it where the user asks, verified, is the whole job.

The DreamWeave Mod Template records these from StroggForge's Rust workflow, which builds, signs,
scans and publishes a program per platform: in the same run, the template hashes those exact
archives into the release record.

## Crates

A Rust library's release has one `crate` artifact: the `.crate` file crates.io serves for that
version, with its publisher source on `static.crates.io`. Its SHA-256 is the checksum the crates.io
index lists, which Cargo verifies on every download. A crate is not installed by DreamWeave
clients; the artifact exists so an index can track the release and verify what crates.io serves.

## Jess packages

A Jess package's release has one `jpk` artifact: the JPK jess packed from the release's commit,
served from the project's own sources like any archive. A `development` release of the package is
the same kind of artifact at a pre-release version, `0.3.1-dev.57`: the package's files at the
default branch with the manifest's version revised, which Jess chooses only when a requirement names
that version exactly. The artifact's `jess` block says what is inside:

| Field | Meaning |
|---|---|
| `package` | The Jess package id, reverse-DNS, as the package's `jess.toml` declares it. One project publishes one package; the project's index entry repeats the id as `jess_package`. |
| `jess_api` | The package API the package declares. |
| `content_digest` | The digest of the package's content, the one `jess.lock` pins and Jess checks after opening the archive. It is not the archive's digest: `digests.sha256` is, and a client checks that first, before opening anything. |
| `dependencies` | The package's `[dependencies]` as declared, by package id: `"org.example.words": "^1.2"`. |

A JPK is not game data and not a program. A DreamWeave client MUST NOT install or run it; Jess
does, from a workspace that pins the package by `content_digest` and its publisher by the manifest
that listed it. An index tracks the release like any other, keyed by `(package, origin)` as it keys
projects by `(project.id, origin)`: the package id proves nothing about who publishes it, and two
sites listing one id is a disagreement to show, never a choice to make. The `dependencies` are
stated so an index can show them; resolving them, across publishers, is Jess's job and no
manifest's.

Everything else about the release is as for any project: its date, channel, notes, `yanked` and
`deprecated` state, sources, mirrors and signatures mean what they mean on the other pages.

## Jess applications

A Jess application's release has one `jsw` artifact: a packed Jess workspace, the application's
targets and every package they run, each pinned to its content digest, in one file that runs
offline wherever Jess does. It is packed from the release's commit and is byte-reproducible: the
same workspace packs to the same bytes, so anyone can repack the tag and compare digests. The
artifact's `jess_workspace` block says what is inside, as the file's own `jsw.toml` does:

| Field | Meaning |
|---|---|
| `package` | The package that names the application: the one holding its default target, or the one package whose targets it exports. The project's index entry repeats it as `jess_package`, and a release may carry this package's `jpk` beside the `jsw`. |
| `builtin` | The version of Jess's built-in package it was packed against. A Jess whose built-in package is compatible runs it; a client installing it picks the newest release its Jess can run. |
| `default` | *Optional.* The target it runs when none is named, `<package>:<target>`. |
| `targets` | Every target it exports, `<package>:<target>`. |
| `commands` | The command names those targets declare, each with the target it runs: what installing it puts on a PATH, `"greet": "org.example.greeter:greet"`. |
| `packages` | Every package it holds, by id, with the exact `version` and `content_digest` it pins: `"org.example.words": { "version": "1.2.0", "content_digest": "…" }`. |

A client checks `digests.sha256` before opening the file, and Jess then holds every package inside
to the digest `jsw.toml` pins; the block must say the same as `jsw.toml`, or the artifact is
refused. `packages` is a frozen set, not requirements: an index shows it, and resolves nothing from
it. A `jsw` is not game data, and a DreamWeave client MUST NOT install or run it; `jess install`
does.

The same release usually carries the application as programs too: one `binary` artifact per
platform, each the Jess runtime for that platform carrying this exact `jsw`, zipped like any other
program's archive and chosen as [Programs](#programs) describes. They are for people without Jess;
a client that has Jess installs the `jsw`, which its own Jess then carries.
