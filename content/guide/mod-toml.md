+++
title = "mod.toml reference"
description = "Every key, its type, its default, and what it means."
weight = 25

[extra]
kind = "reference"
+++

`mod.toml` is read strictly. A key this page does not list is an error, with a suggestion when it
looks like a typo, because a misspelled `runtime` silently doing nothing is how a mod ships with no
compatibility data. Content files, component paths and media files are checked against what is
actually in the directory.

Only `id`, `slug`, and each release's `version` and `date` are required. Candlelight's
[mod.toml](https://github.com/DreamWeave-MP/DreamWeave-Mod-Template/blob/main/content/home/mod.toml)
uses every key once, with comments.

## Identity

| Key | Type | Default | Meaning |
|---|---|---|---|
| `id` | UUID | required | The project's permanent identity: a random UUID, from `uuidgen` or anything else that makes them (CI's error suggests one if it is missing). Never derived from the name, host or URL, and never changed. |
| `slug` | `[a-z0-9_]+` | required | Archive name and release-tag prefix: `slug.zip`, tagged `slug-1.2.0`. No hyphens, because the tag's first hyphen separates slug from version. Changing it breaks old links, not the project. |
| `type` | string | `"mod"` | `mod`, `library`, `framework`, `tool`, `assets`, `total-conversion` or `documentation`. |
| `status` | string | `"active"` | `active`, `maintenance`, `experimental`, `deprecated` or `archived`. |
| `versioning` | string | `"numeric"` | How release numbers compare. See [Releases](@/guide/releases.md#versions). |
| `game` | token | `"morrowind"` | The game the project targets. |
| `license` | string | none | An SPDX expression, like `GPL-3.0-or-later`. |
| `provides` | list of capabilities | `[]` | Names other projects may depend on without naming this one, like `dreamweave:dynamic-lights`. |

The display name and summary are `title` and `description` in `index.md`'s frontmatter.

## `[[maintainers]]` and `[[credits]]`

| Key | Type | Meaning |
|---|---|---|
| `name` | string | Required. |
| `url` | URL | Optional. |
| `role` | string | Credits only: `Scripts`, `Textures`, `Testing`, whatever is true. |

## `[links]`

| Key | Default | Meaning |
|---|---|---|
| `source` | the site's repository | Where the source lives. |
| `issues` | the repository's issues | Where to report problems. |
| `documentation` | none | A URL or a Zola `@/` path to the docs. |
| `support`, `donate`, `homepage`, `nexusmods` | none | URLs. |

## `[runtimes]`

A table of runtime id to version constraint: the engines this runs on. Any one of them is enough.

```toml
[runtimes]
openmw = ">=0.49"
```

Known ids are `openmw`, `morrowind` (the original engine), `mwse` and `tes3mp`. An empty table means
the project does not care, which is true of an asset pack and false of almost everything else.

## `[[platforms]]`

For tools with native binaries: `os` is `windows`, `macos`, `linux` or `android`; `arch` is
`x86_64` or `aarch64`; `variant`, optional, is `portmaster` or `muos` for a handheld build. No
entries means platform-independent. A `binary` package needs at least one desktop entry: each entry
is one archive the Rust workflow builds, and one artifact in every release. Android and variants are
for `binary` packages only. See [Programs](@/guide/packages.md#programs).

## Relationships

Five lists, all with the same keys: `[[requires]]`, `[[recommends]]`, `[[conflicts]]`,
`[[compatible]]` and `[[replaces]]`. [Dependencies](@/guide/dependencies.md) explains what each
promises.

| Key | Type | Meaning |
|---|---|---|
| `id` | UUID | The other project's id. The only thing a client can resolve. |
| `capability` | string | Instead of `id`: anything that `provides` it. `requires`, `recommends` and `conflicts` only. |
| `name` | string | For people. Required when there is neither `id` nor `capability`. |
| `version` | constraint | Needs `id`. Evaluated with the other project's versioning scheme. |
| `url` | URL | Where to find the other project. |
| `reason` | string | Why. Shown on the page. |

## `[openmw]`

What OpenMW needs to know that is true of the whole project.

| Key | Type | Meaning |
|---|---|---|
| `lua_api` | constraint | Required `core.API_REVISION`, like `">=60"`. |
| `requires_content` | list | Content files that must be active, like `["Morrowind.esm", "Tribunal.esm"]`. |
| `[[openmw.settings]]` | `category`, `key`, `value` | Settings the mod needs in `settings.cfg`. |

When there are no `[[components]]`, the install keys below go directly in `[openmw]` and describe
the whole directory.

## `[[components]]`

The pieces a player can choose. For a `flat` package there are none: the directory is one
component.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `id` | token | required | Unique within the project. |
| `name` | string | the id | Shown to players. |
| `path` | directory | required | A top-level directory, like `"00 Core"`. |
| `description` | string | none | Shown on the page and in the FOMOD installer. |
| `required` | bool | `false` | Always installed. |
| `default` | bool | `required` | Selected unless the player says otherwise. |
| `group` | token | none | A `[[groups]]` id this component is one choice in. |
| `requires`, `conflicts` | component ids | `[]` | Other components of this project. |
| `suggested_with` | project ids | `[]` | Recommend this component when those projects are installed. |

Each component has an `[components.openmw]` table with the install keys:

| Key | Type | Default | Becomes |
|---|---|---|---|
| `data_directories` | paths | `["."]` | `data=` lines, relative to the component |
| `content_files` | file names | `[]` | `content=` lines, in load order |
| `groundcover_files` | file names | `[]` | `groundcover=` lines |
| `fallback_archives` | `.bsa` names | `[]` | `fallback-archive=` lines |
| `fallback_entries` | table | `{}` | `fallback=Key,Value` lines |
| `config` | bool | `false` | a `config=` line for an `openmw.cfg` in the component |
| `requires_content` | file names | `[]` | content this component needs, like `TR_Mainland.esm` |

## `[[groups]]`

| Key | Meaning |
|---|---|
| `id`, `name`, `description` | As for components. |
| `select` | `exactly-one`, `at-most-one`, `at-least-one` or `any`. An `exactly-one` group needs exactly one `default = true` member. |

## `[package]`

| Key | Default | Meaning |
|---|---|---|
| `format` | `"flat"` | `flat`, `bain` or `fomod` for game data; `binary` for a program built from Rust source; `crate` for a Rust library on crates.io. See [Packages](@/guide/packages.md). |
| `documentation` | `true` | Render the page and its docs into `Documentation/` inside the archive. Not for `binary`, whose archives the Rust workflow builds, or `crate`, which has none. |
| `development` | `true` | Publish a rolling build of the default branch on the `development` channel. Not for `crate`. |
| `binary` | | `binary` only: the Cargo binary. Its archives are `<binary>-<OS>-<ARCH>.zip`, one per `[[platforms]]` entry. |
| `include` | `[]` | `binary` only: files and directories packed beside the program: `["README.md", "LICENSE", "resources"]`. Paths start where StroggForge builds it: the directory named after the binary when the repository has one, as a workspace member, else the repository root. A name matches in any case. |
| `crate` | | `crate` and `binary`: the package's name on crates.io, as in its `Cargo.toml`. Required for a `crate`; for a `binary`, it adds `cargo install` to the page. |

A Rust project's build settings, such as dependents to notify, benchmarks or extra targets, are
inputs of StroggForge's workflow in the repository, not keys here.

## `[install]`

Markdown shown in the Install section: `notes`, `post_install`, `upgrade`, `uninstall`.

## `[[media]]`

| Key | Meaning |
|---|---|
| `file` | An image in the project directory. Or `video`, a URL. Exactly one of the two. |
| `alt` | Required. What a screen reader says. |
| `caption`, `category` | Optional. |
| `featured` | At most one: the header image. |
| `thumbnail` | For a video: an image in the project directory. |

## `[nexusmods]`, `[[mirrors]]` and `[provenance]`

| Key | Meaning |
|---|---|
| `nexusmods.mod_id` | The Nexus Mods page. A location, not an identity. |
| `nexusmods.file_group_id` | Enables the workflow's Nexus upload on tagged releases. |
| `mirrors.url` | An extra download location with `{slug}`, `{version}`, `{tag}`, `{filename}` or `{sha256}`. See [Distribution](@/guide/distribution.md). |
| `mirrors.name` | Optional. |
| `provenance.sigstore` | `true` signs each archive in CI. See [Provenance](@/guide/provenance.md). |

## `[[releases]]`

| Key | Type | Default | Meaning |
|---|---|---|---|
| `version` | version | required | Unique by precedence. No `+build` suffix. |
| `date` | TOML date | required | `2026-10-01`, unquoted. |
| `channel` | token | `"stable"` | `stable`, `beta`, `legacy` or your own. `development` is reserved. |
| `summary`, `highlights`, `migration`, `notes` | Markdown | none | Shown on the page, the changelog and the GitHub release. |
| `added`, `changed`, `fixed`, `breaking`, `known_issues` | lists | `[]` | One Markdown line each. |
| `yanked`, `deprecated` | string | none | The reason. At most one of the two. |
| `replacement` | version | none | What to use instead of a yanked or deprecated release. |

## `[extensions."your.namespace"]`

Data for tools this template does not know about, under a dotted namespace you own
(`org.tes3mp`, `io.github.someone.tool`). It is copied into the manifest untouched. See
[Extensions and evolution](@/guide/protocol/evolution.md).
