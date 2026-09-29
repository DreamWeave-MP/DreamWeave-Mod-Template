+++
title = "Manifest"
description = "Every field of a project manifest and the site index."
weight = 20

[extra]
kind = "reference"
+++

The JSON Schemas are normative for structure; this page is normative for meaning. Fields marked
*optional* MAY be absent; every other field MUST be present. Absent means unknown, never false.

## Project manifest

```json
{
  "schema_version": "2",
  "document": "project",
  "generator": "DreamWeave Mod Template 5.0.0",
  "project": { ... },
  "channels": { "stable": { "version": "1.1.0" }, "development": { "version": "1.1.1-dev.3" } },
  "releases": [ ... ]
}
```

`generator` is informational. Clients MUST NOT change behavior based on it.

### `project`

| Field | Meaning |
|---|---|
| `id` | UUID, canonical lowercase. The project's identity. |
| `name` | Display name. May change at any time. |
| `summary` | *Optional.* One line. |
| `type` | `mod`, `library`, `framework`, `tool`, `assets`, `total-conversion` or `documentation`. Presentation only. |
| `status` | `active`, `maintenance`, `experimental`, `deprecated` or `archived`. |
| `versioning` | `numeric` or `decimal`: how this project's versions compare. See [Versions](@/guide/protocol/versions.md). |
| `game` | Lowercase token, e.g. `morrowind`. |
| `license` | *Optional.* SPDX expression. |
| `tags` | Free-form strings. |
| `maintainers` | `[{ name, url? }]`. |
| `links` | Object of URLs. Always `page`, `source`, `issues`; optionally `documentation`, `support`, `donate`, `homepage`, `nexusmods`, and `crate` for a Rust crate: its crates.io page. |
| `integrations` | Locations on other services, e.g. `{ "nexusmods": { "game": "morrowind", "mod_id": 57511 } }`. Never identity. |
| `media` | `[{ kind: image\|video, url, alt, thumbnail?, caption?, category?, featured? }]`. |
| `credits` | `[{ name, role?, url? }]`. |

### `channels`

Each channel's head, the highest-precedence release in that channel whose `status` is
`available`. A channel with no available release is absent. Clients MAY recompute heads from
`releases` and MUST get the same answer.

### `releases`

Every published release, newest first by precedence, including yanked and deprecated ones.

| Field | Meaning |
|---|---|
| `version` | The release's version under the project's scheme. Unique by precedence within the project. |
| `channel` | Lowercase token. `development` is the rolling build of the default branch. |
| `date` | *Optional.* ISO date the author gives the release. |
| `status` | `available`, `yanked` or `deprecated`. |
| `yanked`, `deprecated` | *Optional.* `{ reason, replacement? }`, present exactly when `status` says so. |
| `source` | `{ repository, tag?, release?, revision? }`. `revision` is the full commit hash when known. |
| `notes` | *Optional.* `{ summary?, highlights?, added?, changed?, fixed?, breaking?, migration?, known_issues?, notes? }`. Strings are CommonMark; a consumer MUST treat embedded HTML as untrusted. |
| `runtimes` | Object of runtime id to [constraint](@/guide/protocol/versions.md#constraints). The release runs on any listed runtime. Empty means runtime-independent. |
| `platforms` | `[{ os, arch }]`, desktop systems only: `windows`, `macos`, `linux`. Empty means platform-independent. A program's Android and handheld builds are described on their [artifacts](@/guide/protocol/artifacts.md#programs). |
| `provides` | Capability strings. |
| `relationships` | See below. |
| `components`, `groups` | See [Installation](@/guide/protocol/installation.md). |
| `extensions` | Namespaced extension data. See [Evolution](@/guide/protocol/evolution.md). |
| `critical_extensions` | Extensions a client MUST implement to install this release. |
| `artifacts` | See [Artifacts](@/guide/protocol/artifacts.md). At least one. |

Everything from `runtimes` down describes the release's bytes and does not change after
publication, except by a deliberate amendment from the publisher. `date`, `channel`, `status` and
`notes` may be corrected.

### `relationships`

```json
{ "kind": "requires", "project": "9b7e3f21-…", "name": "Tallow", "version": ">=1.0", "url": "https://…" }
```

| Field | Meaning |
|---|---|
| `kind` | `requires`: the release does not work without the target. `recommends`: works better with it. `conflicts`: MUST NOT be active together. `compatible`: tested together. `replaces`: supersedes the target. |
| `project` | *Optional.* The target's id. |
| `capability` | *Optional.* Instead of `project`: any project whose release `provides` it satisfies the relationship. Only for `requires`, `recommends`, `conflicts`. |
| `name` | *Optional.* For display. A relationship with neither `project` nor `capability` is informational and cannot be resolved. |
| `version` | *Optional.* Constraint, only with `project`, evaluated with the target project's versioning scheme. Absent means any version. |
| `url` | *Optional.* Where to discover the target. |
| `reason` | *Optional.* For display. |

A `requires` or `conflicts` on a project satisfies or violates only when the target is installed at
a version the constraint allows. Resolution order, how far to follow chains, and what to do with
unresolvable targets are client policy.

## Site index

```json
{
  "schema_version": "2",
  "document": "index",
  "generator": "…",
  "site": { "name": "Cool Mods", "url": "https://you.github.io/cool-mods/" },
  "projects": [
    {
      "id": "…", "name": "…", "summary": "…", "type": "mod", "status": "active",
      "page": "https://…/home/", "manifest": "https://…/dreamweave/projects/….json",
      "manifest_sha256": "…", "updated": "2026-09-27", "channels": { "stable": "1.1.0" }
    }
  ]
}
```

`projects` is sorted by `id`. An index entry is a pointer and a change detector; everything it says
is repeated, authoritatively, in the manifest.

## Release payload

`dreamweave.release.json` at an archive's root has `document: "release-payload"`, the project's
`id`, `name`, `slug` and `versioning`, the release `version`, the package `format`, and the same
`runtimes` through `critical_extensions` fields as the manifest's release. It lets a loose archive
identify itself. It cannot contain its archive's own digest, so it is never proof of anything; when
it and the manifest disagree, the manifest wins.
