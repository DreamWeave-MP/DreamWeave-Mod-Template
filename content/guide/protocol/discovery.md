+++
title = "Discovery"
description = "From any URL on a site to its index and manifests."
weight = 10

[extra]
kind = "reference"
+++

## Advertising

A site MUST serve its index at `dreamweave.json` relative to the site's base URL, which MAY be a
path below the origin (`https://you.github.io/cool-mods/dreamweave.json`).

Every HTML page of the site SHOULD include, in `<head>`:

```html
<link rel="alternate" type="application/vnd.dreamweave.index+json" href="ABSOLUTE-INDEX-URL">
```

A project's page SHOULD also include:

```html
<link rel="alternate" type="application/vnd.dreamweave.project+json" href="ABSOLUTE-MANIFEST-URL">
```

## Finding the index from a URL

Given a URL `U` supplied by a user:

1. GET `U`. If the response is JSON with `schema_version` and a `document` of `index` or `project`,
   use it and stop.
2. If the response is HTML, look for `<link>` elements whose `rel` contains `alternate` and whose
   `type` is one of the two media types above. Resolve `href` against `U`. Prefer the project
   manifest when both are present and the user asked for a project. Stop.
3. Otherwise, let `D` be `U` with its query and fragment removed and, unless its path ends in `/`,
   its last path segment removed. Try `D + "dreamweave.json"`. If that fails, remove the last path
   segment of `D` and try again, until the origin's root has been tried.

A client MUST NOT scrape anything else from the HTML. A client MAY skip step 2 entirely.

## From the index to a manifest

Each entry of `projects` names a project's `id` and `manifest` URL. A client MUST treat a manifest
whose `project.id` differs from the index entry's `id` as an error.

`manifest_sha256` is the SHA-256 of the manifest's bytes as served. An index or client MAY use it
to skip re-fetching an unchanged manifest; it MUST NOT treat a mismatch as anything more than "the
manifest changed since the index was built".

`updated` is the newest release date, or null. `channels` repeats each channel's head version for
change detection; the manifest remains authoritative.

## Which site is authoritative

A project's id does not say which site speaks for it: ids are chosen, not allocated, so nothing
stops two sites from publishing the same one. A client SHOULD remember where it first discovered a
project and treat a manifest for the same id from anywhere else as a separate claim that needs the
user's confirmation, until publisher keys ([Provenance](@/guide/provenance.md)) give it a better
basis. An index SHOULD show which origin each manifest came from.

A project that moves hosts keeps its id. Players whose client remembers the old origin need to be
told, by the old site's page, a redirect, or the author.
