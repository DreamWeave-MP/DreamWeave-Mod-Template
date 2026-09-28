+++
title = "Artifacts"
description = "Digests, sources, verification, signatures, and what is inside an archive."
weight = 40

[extra]
kind = "reference"
+++

## Fields

| Field | Meaning |
|---|---|
| `id` | Token, unique within the release. |
| `format` | `flat`, `bain` or `fomod`: game data, laid out as [Installation](@/guide/protocol/installation.md) describes. `binary`: a program built for one platform. |
| `filename` | A suggested file name. Not identity. |
| `media_type` | `application/zip` for every current format. |
| `size` | Bytes. |
| `digests` | `{ "sha256": "<64 lowercase hex>" }`. Further algorithms MAY be added; `sha256` is always present. |
| `platform` | `{ os, arch }`, required when `format` is `binary`: the one platform the program runs on. |
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
issuer and `identity` the certificate identity to require, typically the GitHub Actions workflow
that built the artifact, at the tag's ref. A client that verifies it learns that this workflow in
this repository produced these bytes. It learns nothing about whether to trust that repository.

A client MAY require signatures by policy. A missing signature MUST NOT be treated as a failed
digest: the digest already establishes integrity against the manifest.

## Archive contents

Every archive is a zip. Archives built by the DreamWeave Mod Template are stored (not compressed),
sorted, dated 1980-01-01 and byte-reproducible from their source commit; the protocol does not
require any of that, only that the digest match.

At the root of a `flat`, `bain` or `fomod` archive:

- the project's files, laid out per `format`;
- `dreamweave.release.json`, the [release payload](@/guide/protocol/manifest.md#release-payload);
- `Documentation/`, optionally: the project's pages rendered as self-contained HTML;
- `fomod/`, for `format: "fomod"`: a ModConfig 5.0 installer generated from the components.

## Programs

A release of a tool built from source has one `binary` artifact per platform, each with its
`platform`. The release's `platforms` lists them all. A client offers the artifact whose `platform`
matches the machine it runs on, and none if nothing matches: a Windows build is not a fallback for
Linux.

A binary archive holds the program and the files its publisher ships beside it, and nothing
DreamWeave adds; there is no release payload inside. It is not game data. A client MUST NOT install it
into a game's data directories, and MUST NOT run anything from it as part of installing. Unpacking
it where the user asks, verified, is the whole job.

The DreamWeave Mod Template publishes these from StroggForge's Rust workflow: it builds, signs and
scans a program per platform, and the template hashes those exact archives into the release record
before publishing them.
