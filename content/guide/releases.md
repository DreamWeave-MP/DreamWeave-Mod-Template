+++
title = "Releases"
description = "Versions, channels, locking, tagging, yanking, and what CI does with a tag."
weight = 30

[extra]
kind = "guide"
+++

A release is a version you promise not to change. The template makes that promise checkable: the
archive for a release is built from the committed tree, its SHA-256 is written into `mod.lock`
before the tag exists, and CI refuses to publish a tag whose archive comes out different.

## The short version

```sh
# 1. declare it
$EDITOR content/home/mod.toml    # add a [[releases]] entry for 1.1.0 with notes

# 2. commit everything, then lock it
git commit -am "Prepare My Mod 1.1.0"
./buildSite lock my_mod

# 3. commit the lock, tag that commit, push both
git add content/home/mod.lock
git commit -m "RELEASE: My Mod 1.1.0"
git tag my_mod-1.1.0
git push --atomic origin HEAD my_mod-1.1.0
```

CI then rebuilds `my_mod-1.1.0` from the tag, compares the bytes with `mod.lock`, uploads the
archive to a GitHub release named after the tag with the release's own notes as its description,
and rebuilds the site so the release appears on the page and in the manifest.

## Why lock first

A hash you cannot reproduce is a hash you have to trust. Most release pipelines record whatever
CI happened to produce, which means the published hash says only "this is what came out". Here the
hash is recorded in a reviewed commit before publication, CI has to reproduce it exactly, and
anyone with the repository can check it later.

That works because archives are byte-reproducible: stored, not compressed; sorted; dated
1980-01-01; permissions from git; built from committed blobs, so line-ending settings and untracked
files cannot leak in. [Packages](@/guide/packages.md#reproducible-archives) has the details.

`lock` refuses to run with uncommitted changes anywhere in the repository, because the archive
includes rendered documentation and templates affect it. It also refuses when the tag already
exists: a published release has whatever bytes it was published with, and rebuilding it now would
record a hash that does not match the file people downloaded.

If you tag and CI says the tag **does not reproduce its lock**, something committed between `lock`
and the tag changed the archive. Delete the tag, run `lock` again, commit, re-tag.

## What a release record holds

The two halves of a release live in different places, on purpose.

| Frozen in `mod.lock` | Editable in `mod.toml` |
|---|---|
| The archive's file name, size and SHA-256 | The date |
| Components, groups and their paths | The channel |
| OpenMW install data | The notes |
| Runtimes, platforms, relationships | Yanked or deprecated, and why |

The frozen half describes bytes that exist. If 2.0 renames a component, 1.0's record still
describes 1.0's archive. The editable half is what you say about a release, and you may need to
correct it. `mod.lock` is JSON and it is yours: amending a published release's compatibility by
hand is allowed, and git shows the edit.

## Versions

A version is dot-separated numbers with an optional pre-release and build suffix, as in SemVer:
`1`, `0.51`, `1.2.0`, `2.0.0-beta.3`. How the numbers compare is the project's choice, written in
`mod.toml` and published in its manifest so no client guesses:

| `versioning` | Every number after the first compares | So |
|---|---|---|
| `"numeric"` (default) | as an integer; missing numbers count as zero | `1.2 = 1.2.0 < 1.2.9 < 1.2.10`, and `0.9 < 0.82` |
| `"decimal"` | like digits after a decimal point; trailing zeros do not count | `0.5 = 0.50 < 0.54 < 0.6 < 0.82 < 0.9 < 0.963` |

Pre-releases sort before their release (`2.0.0-beta.1 < 2.0.0`) and build metadata is ignored.

Pick one and keep it. If you have ever released 0.82 and then 0.9 expecting 0.9 to be newer, you
are a `decimal` project. The validator notices when a newer release sorts below an older one and
says so; that check covers releases that are locked or not yet tagged, not tags from before the
lock existed, which are history nobody can rewrite.

## Channels

Every release has a channel. `stable` is the default; `beta` and `legacy` are conventional; any
lowercase name works. A channel's head is its highest-precedence release that is neither yanked nor
deprecated, and the manifest lists every head.

`development` is special: it is built from the default branch on every push, never declared, and
its version is generated to sort just after the newest tag: `1.2.0` becomes `1.2.1-dev.7`, and a
decimal `0.963` becomes `0.9631-dev.7`, where the last number counts commits to the project since
that tag. Turn it off with `[package] development = false`.

## Yanking and deprecating

A published release stays in the manifest forever. To take one back, say why:

```toml
[[releases]]
version = "1.1.0"
date = 2026-09-27
yanked = "Deletes your saves' light cache on load."
replacement = "1.1.1"
```

A yanked release leaves its channel's head, shows a warning on the page, and tells clients not to
install it. `deprecated` is the milder version: it still works, but use the replacement. The
archive stays downloadable, because pretending a release never existed breaks every mod list that
pinned it.

## What CI does with a tag

1. Validates the repository and runs the template's tests.
2. Checks out the tag, rebuilds the release, and fails unless the archive matches `mod.lock` byte
   for byte and the install and compatibility data still match the record.
3. Signs the archive with Sigstore if `[provenance] sigstore = true`.
4. Recreates the GitHub release for the tag and uploads the archive and signature.
5. Replaces GitHub's generated release notes with the release's own notes and the archive's digest.
6. Uploads to Nexus Mods if `[nexusmods] file_group_id` is set.
7. Rebuilds the site from the default branch and deploys it.

Tags pushed before V4, or without a lock, still show in the changelog, marked **unverified**. The
manifest leaves them out, because nothing records what their archives contained.
