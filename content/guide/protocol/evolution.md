+++
title = "Extensions and evolution"
description = "Namespaced extensions, unknown data, and what a client does with a newer schema."
weight = 60

[extra]
kind = "reference"
+++

## The core is frozen per major version

`schema_version` is a major version. Within `"4"`, the fields and meanings on these pages do not
change. A new core field or a changed meaning is `"5"`.

That makes validation strict without making evolution painful: an unknown field in the core is
always an error (a typo, a buggy generator, or a document from the future), never something to guess
about. New things go into extensions until they have earned a place in the next major version.

## Extensions

`extensions` on a release is an object keyed by namespace:

- Short names are defined by this specification. Currently: `openmw`.
- Anyone else uses a dotted name they plainly own: `org.tes3mp`, `io.github.someone.launcher`.
  Anything else is an error.

Each value is an object whose contents the namespace's owner defines. A client:

- MUST ignore a namespace it does not implement, unless it is listed in `critical_extensions`;
- MUST NOT claim to have installed a release with a critical extension it does not implement;
- MUST preserve extension data it passes along (an index, a mirror of the manifest) unchanged.

Publishers write third-party extensions in `mod.toml` under `[extensions."org.tes3mp"]`; the
template copies them into the manifest verbatim.

## A document a client did not expect

| The document has | A client MUST |
|---|---|
| a `schema_version` it supports | read it, and treat unknown core fields as an error |
| an older `schema_version` it still supports | read it under that version's rules |
| a newer or unknown `schema_version` | stop, and say that the site uses a newer protocol; never read it as its own version |
| no `schema_version` or `document` | treat it as not a DreamWeave document |

Clients never infer a version from which fields happen to be present.

## Deprecation

A field is deprecated by saying so on these pages for at least one major version before it is
removed. Its meaning does not change while it is deprecated. Versions `"3"` and `"2"` are superseded
by this version, and the V4 template's per-release `.modManifest` (`schema_version: "1"`) before
them; their schemas stay published at their original URLs for tools that read old sites and old release assets.

## What version 4 added

One thing: a release's artifact may be a Jess application, `format: "jsw"`, a packed Jess workspace
with a `jess_workspace` block saying which package names it, the Jess it runs on, the targets and
commands it exports, and every package it holds, pinned. Its executables are `binary` artifacts as
any program's are. Everything a version 3 document said, a version 4 document says the same way; a
version 3 reader that is taught the one addition reads version 4. A site writes every document at
the version it publishes under, so a reader that only knows version 3 stops at a version 4 site
and says so, as it must. See [Jess applications](@/guide/protocol/artifacts.md#jess-applications).

## What version 3 added

One thing: a release's artifact may be a Jess package, `format: "jpk"`, with a `jess` block saying
which package it is, its content digest, its API and its declared dependencies, and an index entry
may name the Jess package a project publishes. Everything a version 2 document said, a version 3
document says the same way; a version 2 reader that is taught the two additions reads version 3.
See [Jess packages](@/guide/protocol/artifacts.md#jess-packages).

## What a later version is likely to contain

Publisher keys and manifest signatures ([Provenance](@/guide/provenance.md)), a statement for moving
a project to a new origin, and anything from third-party extensions that several clients came to
rely on. Until then, they are extensions or they do not exist.
