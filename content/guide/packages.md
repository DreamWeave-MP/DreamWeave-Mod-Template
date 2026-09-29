+++
title = "Packages"
description = "Flat, BAIN and FOMOD archives, programs built per platform, Rust libraries on crates.io, components, what ships, and why archives are not compressed."
weight = 40

[extra]
kind = "guide"
+++

A mod is packaged as one zip, named after its slug. What differs between mods is how the inside is
laid out and how much of that layout a player gets to choose from. A modding tool written in Rust is
a program instead: one zip per platform, built from source. [Programs](#programs) covers those, and
[Libraries](#libraries) covers Rust crates, which crates.io distributes and this site documents.

## Formats

| `format` | Inside the archive | Who installs it how |
|---|---|---|
| `flat` (default) | One data directory at the root | Extract and point `data=` at it; any mod manager |
| `bain` | Numbered top-level directories, one per component | Wrye Bash picks sub-packages; OpenMW gets a `data=` line per directory you want |
| `fomod` | The `bain` tree plus a generated `fomod/` installer | MO2 and Vortex run the installer; Wrye Bash and hand installs still see the tree |
| `binary` | A program for one platform, and the files it ships with | Nobody installs it: unzip and run. See [Programs](#programs) |
| `crate` | No archive: a Rust library on crates.io | `cargo add`. See [Libraries](#libraries) |

Most mods are `flat`. S3maphore, with a core and seventeen optional playlist packs, is `bain`.
Choose `fomod` when players install through MO2 or Vortex and there are real choices to make: the
installer is generated from your components, so it cannot disagree with the page.

OMOD is not offered. It is an Oblivion Mod Manager format with a binary config record and
imperative install scripts, and a DreamWeave package does not run scripts.

## Programs

A project can be a program: a compiler, a converter, a patcher. Its archives are not zipped from
`content/<project>`; [StroggForge](https://github.com/DreamWeave-MP/StroggForge)'s Rust workflow
builds them from the repository's Rust source, one per platform, and tests, signs, virus-scans and
publishes them. The site records what it published.

```toml
type = "tool"

[package]
format = "binary"
binary = "morrobroom"                                  # the Cargo binary
include = ["README.md", "LICENSE", "resources"]        # packed beside it, from the repository root

[[platforms]]
os = "windows"
arch = "x86_64"

[[platforms]]
os = "linux"
arch = "x86_64"
```

The repository's own workflow calls StroggForge's `rustGlobalBuild` with `mod_template: true`.
Once the archives are built and published, the same run hands them to the Mod Template stage,
which hashes those exact files into the release record, then builds and deploys the site. The
program's build settings, from `binary_names` to `enable_portmaster`, live in that workflow, not in
`mod.toml`.

A Rust project releases under the bare version tags StroggForge uses: declare the version, push
`1.0.0`, and the program is built, published and recorded, with one artifact per platform. The
project page offers a download per platform, marks the visitor's own, and says how to run the
program instead of how to install data. A repository has at most one Rust project, so the version
alone says which.

`[[platforms]]` lists what the Rust workflow builds and the release records: Windows and Linux on
x86_64, macOS on Intel and Apple silicon, and, when the workflow builds them, Android and handheld
builds:

```toml
[[platforms]]
os = "android"
arch = "aarch64"

[[platforms]]
os = "linux"
arch = "aarch64"
variant = "portmaster"      # PortMaster's framebuffer build

[[platforms]]
os = "linux"
arch = "aarch64"
variant = "muos"            # the same build as a muOS .muxapp
```

Each entry must come back from the build, or the release is refused. At least one is a desktop
platform. There are no components, no FOMOD and no `Documentation/` in a program's archives:
`include` is how its documentation travels with it. A program that is also published to crates.io
names it with `crate`, and the page offers `cargo install` beside the downloads.

## Libraries

A Rust library is published to crates.io, and Cargo is its installer. The site is what docs.rs
would otherwise be: the project page, the guides, and an API reference you write as pages, with
the same search, callouts and schematics as any other documentation here.

```toml
type = "library"

[package]
format = "crate"
crate = "openmw-config"                  # the name on crates.io
```

The repository's own workflow calls StroggForge's `libGlobalBuild` with `mod_template: true`. It
tests the crate on Windows, macOS and Linux, runs Clippy and `cargo audit`, dry-runs the publish on
every push, and on a bare version tag, `2.0.1`, publishes that version to crates.io.

The site records each version from crates.io itself: the `.crate` crates.io serves, checked against
the checksum in its index. crates.io never changes a published version, so every run on the default
branch records whatever declared versions it has and `mod.lock` lacks, including crates published
before the repository used this template. The manifest lists them like any release, with crates.io
as the source. The page offers `cargo add` rather than a download, and each release links to its
version on crates.io.

A crate has no components, no `[openmw]` data, no development channel and no mirrors, and a
repository has at most one Rust project.

## Components

A `bain` or `fomod` project declares its components:

```toml
[package]
format = "fomod"

[[components]]
id = "core"
name = "Core"
path = "00 Core"
required = true

[components.openmw]
content_files = ["Candlelight.omwscripts"]

[[groups]]
id = "flames"
name = "Flame textures"
select = "exactly-one"

[[components]]
id = "flames-2k"
name = "Flames, 2K"
path = "20 Flames 2K"
group = "flames"
default = true

[[components]]
id = "flames-4k"
name = "Flames, 4K"
path = "21 Flames 4K"
group = "flames"
```

`path` is a top-level directory. Number them (`00 Core`, `10 Optional`) the way BAIN packages
always have; it keeps the order obvious in every tool. A component's `data_directories` default to
the component itself.

Relationships between components are declarative and small: `required`, `default`, `group` with a
`select` rule, `requires` and `conflicts` between components, and `suggested_with` to recommend a
component when another project is installed. There is no scripting and there will not be. A
package describes what to install; it does not run code on your machine to decide.

The validator refuses combinations that cannot be installed: a required component inside a group,
two required components that conflict, an `exactly-one` group without exactly one default, a
component that requires one that does not exist.

## What ships

Everything committed under the project directory ships, including `index.md`, `mod.toml` and the
docs sources. Documentation belongs with the mod. Only `mod.lock` stays out, because it records the
archive's own hash.

The tooling adds three things:

{% tree() %}
my_mod.zip/
  00 Core/  your components, or your one data directory
  docs/  your documentation sources
  index.md
  mod.toml
  Documentation/  this page and its docs, rendered, readable offline
  fomod/  the generated installer, format = "fomod" only
  dreamweave.release.json  what this archive is, for tools
{% end %}

`Documentation/` is the project's page, changelog and docs, rendered as they are on the site, with
every link inside the project turned into a relative file path and every stylesheet, font and image
they use copied next to them. Open `Documentation/index.html` from a zip on a plane and it works.
Links to other parts of the site stay absolute and work when you are online. Turn it off with
`[package] documentation = false`.

`dreamweave.release.json` is the release's install and compatibility data plus the project id, so a
loose archive can say what it is. The manifest is authoritative if they ever disagree.

The payload check refuses what would break installs: symlinks, submodules, files whose paths differ
only by case (one file on Windows and in OpenMW's VFS), Windows-reserved names, names ending in a
dot or space, and your own files at `Documentation/`, `fomod/` or `dreamweave.release.json`.

## Reproducible archives

The same commit always produces the same bytes, on any machine, which is what lets a release's hash
be written down before the release exists.

- Files come from git blobs, not the working tree: no line-ending conversion, no untracked junk.
- Entries are sorted by path and dated 1980-01-01.
- Permissions come from git's executable bit, recorded as Unix 0644 or 0755.
- Names are UTF-8, and every header byte is written by the template, not by whichever `zipfile`
  version is installed.
- Nothing is compressed.

That last one is a trade. Deflate output differs between zlib and zlib-ng, and Fedora, among others,
ships zlib-ng, so a compressed archive would only rebuild byte for byte on a machine with the same
zlib: not on yours, and not necessarily on next year's CI runner. On S3maphore, whose weight is
audio, deflate saved 5%. Texture packs lose more; if that ever matters more than reproducibility,
the protocol does not care either way: a client unzips what it verified.

Documentation is rendered by Zola, so CI pins the Zola version archives are built with
(`ZOLA_VERSION` in `tools/dreamweave/offline.py`). Your own `zola serve` never builds an archive, so
any recent Zola previews the site.
