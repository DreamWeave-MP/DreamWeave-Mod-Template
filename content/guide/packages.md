+++
title = "Packages"
description = "Flat, BAIN and FOMOD archives, programs built per platform, Rust libraries on crates.io, Jess packages, components, what ships, and why archives are not compressed."
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
| `jpk` | A Jess package, packed by jess from its Package Source | `jess workspace sync`, from a `jess.toml` or `jess-workspace.toml` that names it. See [Jess packages](#jess-packages) |

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
include = ["README.md", "LICENSE", "resources"]        # packed beside it, from where it is built

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
program instead of how to install data.

A repository holds at most one Rust program and one Rust library, and the two share its tags: a
tool and the crate it is built on, released together. A tag releases the program when the program
declares that version, and the library's version is recorded from crates.io beside it; a version
only the library declares is the library's alone. Each keeps its own project page and its own
entry in the manifest.

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
platform. Releases StroggForge published before the repository was a site are recorded from their
GitHub releases, with whichever of these archives each has. There are no components, no FOMOD and no rendered documentation in a program's archives:
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
repository has at most one, beside at most one program.

## Jess packages

A [Jess](https://github.com/DreamWeave-MP/jess) package is published as a project like any other:
a page, a `mod.toml`, releases tagged `<slug>-<version>`. What differs is that its archive is a JPK
jess packs from the package's source, not a zip the template writes.

```toml
[package]
format = "jpk"
jess = "org.example.words"
```

`jess` names the package the project publishes, the way a crate project names its crate: the id a
`jess.toml` in this repository declares. The template finds that `jess.toml` among the repository's
jess workspace members, the folders `jess-workspace.toml` lists, or the repository root itself when
it holds a `jess.toml` and no workspace file. One project publishes one package, and a repository
publishes as many packages as it has projects for: a single package at its root, a tool and the
library it uses as two members, or a dozen under `jpk/`, each with its own page, tags and releases.
Two projects naming one package is an error, as is a `jpk` project naming none.

A release tag `<slug>-<version>` packs the member at that commit, and its `jess.toml` must say that
version: the template refuses a tag whose package manifest disagrees, before anything is packed.
Every push to the default branch packs a development build too, at the version past the newest
release with a `-dev.<build>` pre-release, by revising the manifest's version line and nothing else;
jess picks a pre-release only when a requirement names it exactly, so a development build is used
by whoever asks for it and nobody else. The release's `jpk` artifact carries a `jess` block: the
package id, its API, its content digest, the one `jess.lock` pins, and the dependencies its
manifest declares. See [Jess packages](@/guide/protocol/artifacts.md#jess-packages) in the protocol.

A JPK has no documentation inside: a package's docs are its page. It is not game data and not a
program; nothing but jess installs it.

### Applications

A package with targets to run can ship as an application too: the same release carries a packed
workspace, the package and everything it runs frozen into one `.jsw`, and an executable per
platform, each one a jess carrying that `.jsw`, which runs without jess installed.

```toml
[package]
format = "jpk"
jess = "org.example.tool"
application = "tool"

[[platforms]]
os = "windows"
arch = "x86_64"

[[platforms]]
os = "linux"
arch = "x86_64"
```

`application` is the name the files go by. The template doesn't pack them: as with a Rust program,
CI builds and the template records. The site's workflow names the application to StroggForge too:

```yaml
    uses: DreamWeave-MP/StroggForge/.github/workflows/modGlobalBuild.yml@v66
    with:
      jess_application: tool
```

and before a tag's release is built, CI runs jess from the jess image over the repository's
workspace:

```sh
jess workspace pack --output dist/application/tool.jsw --runtimes /opt/jess/runtimes
```

which leaves `tool.jsw` and an executable for every platform jess is released for. The tag's
release takes `tool.jsw` as its `jsw` artifact, `tool-<version>.jsw`, with a `jess_workspace` block
read from the file's own index: the package it is named for, the jess it was packed for, its
targets, the commands they declare, and every package it pins. Each `[[platforms]]` entry's
executable, `tool-Windows-X64.exe`, `tool-Linux-X64` and so on, ships zipped as
`tool-Windows-X64.zip` with the program inside named `tool.exe`, a `binary` artifact like any
program's. A file missing from `dist/application/` fails the release and says which. Only the
platforms jess itself is released for can carry an application: Windows, macOS and Linux, and
Linux ARM64 for PortMaster.

`jess install org.example.tool` installs the `.jsw`, packed into the installer's own jess; the
zips are for people without jess. Development builds stay JPKs. See
[Jess applications](@/guide/protocol/artifacts.md#jess-applications) in the protocol.

On Nexus Mods an application is a program, as a Rust project's binary is: each platform's zip goes
to a file group of its own, not to the one `[nexusmods] file_group_id` names for a mod, which an
application can't set. The repository's `NEXUS_GROUP_IDS` secret maps each platform to its group,
under the keys StroggForge's Rust workflow uses, beside the `NEXUS_API_KEY` secret:

```json
{ "windows-x64-stable": "123", "macos-arm64-stable": "124", "macos-x64-stable": "125", "linux-x64-stable": "126" }
```

A tag's release uploads each zip whose platform has a group, and leaves the rest on GitHub.

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

Everything committed under the project directory ships, except `mod.lock`, which records the
archive's own hash, and the Markdown the documentation is rendered from: every page's `index.md`,
the project's own and any page bundle's beneath it, and every docs section (a directory with an
`_index.md`). Other Markdown, such as files in hidden directories, ships as it is. Documentation
belongs with the mod, so it travels rendered. `mod.toml` ships as `<slug>-dwmod.toml`. The documentation folder carries
the slug too, so mods extracted into one folder keep their own.

For a project with the slug `my_mod`:

{% tree() %}
my_mod.zip/
  00 Core/  your components, or your one data directory
  my_mod-dwmod.toml  mod.toml
  my_mod-Documentation/  this page and its docs, rendered, readable offline
  fomod/  the generated installer, format = "fomod" only
  dreamweave.release.json  what this archive is, for tools
{% end %}

`<slug>-Documentation/` is the project's page, changelog and docs, rendered as they are on the site,
with every link inside the project turned into a relative file path and every stylesheet, font and
image they use copied next to them. Open its `index.html` from a zip on a plane and it works. Links
to other parts of the site stay absolute and work when you are online. Turn it off with
`[package] documentation = false`, and the Markdown sources ship instead.

`dreamweave.release.json` is the release's install and compatibility data plus the project id, so a
loose archive can say what it is. The manifest is authoritative if they ever disagree.

The payload check refuses what would break installs: symlinks, submodules, files whose paths differ
only by case (one file on Windows and in OpenMW's VFS), Windows-reserved names, names ending in a
dot or space, and your own files at `<slug>-Documentation/`, `<slug>-dwmod.toml`, `fomod/` or
`dreamweave.release.json`.

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

Documentation is rendered by the site generator `jess.lock` pins, `org.dreamweave.site`, the same
version on every machine. A local preview never builds an archive.
