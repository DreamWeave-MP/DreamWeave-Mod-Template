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
| `format` | `flat`, `bain` or `fomod`: how the archive is laid out. See [Installation](@/guide/protocol/installation.md). |
| `filename` | A suggested file name. Not identity. |
| `media_type` | `application/zip` for every current format. |
| `size` | Bytes. |
| `digests` | `{ "sha256": "<64 lowercase hex>" }`. Further algorithms MAY be added; `sha256` is always present. |
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

At the root:

- the project's files, laid out per `format`;
- `dreamweave.release.json`, the [release payload](@/guide/protocol/manifest.md#release-payload);
- `Documentation/`, optionally: the project's pages rendered as self-contained HTML;
- `fomod/`, for `format: "fomod"`: a ModConfig 5.0 installer generated from the components.
