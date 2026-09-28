+++
title = "Releases"
description = "Versions, channels, tagging, yanking, and what CI does with a tag."
weight = 30

[extra]
kind = "guide"
+++

A release is a version you promise not to change. The template makes that promise checkable: CI
builds the archive from the tag, records its SHA-256 in `mod.lock`, and from then on refuses to
publish that version with any other bytes.

## The short version

```sh
# 1. declare it: add a [[releases]] entry for 1.1.0, with its date and notes
$EDITOR content/home/mod.toml

# 2. commit, tag that commit, push both
git commit -am "My Mod 1.1.0"
git tag my_mod-1.1.0
git push origin HEAD my_mod-1.1.0
```

That is all you run. The tag's workflow run builds `my_mod-1.1.0` from the tag, adds its record to
`content/home/mod.lock` in a commit on your default branch, publishes the archive as a GitHub
release with the release's own notes, and rebuilds the site so the release appears on the page and
in the manifest. The record is a commit you did not make, so `git pull` before you next push.

## Nobody edits mod.lock

`mod.lock` is written by CI and only by CI: `github-actions[bot]` adds a record when a release tag
is pushed, and that commit is the only one the workflow ever makes. It is JSON in your repository,
so git shows every record and when it arrived, but you never need to touch it.

A record says what the tag's archive contains, down to the byte. Archives are byte-reproducible:
stored, not compressed; sorted; dated 1980-01-01; permissions from git; built from committed blobs,
so line-ending settings and untracked files cannot leak in. [Packages](@/guide/packages.md#reproducible-archives)
has the details. Re-running a tag's job rebuilds the archive and checks it against the record, and
anyone with the repository and the template's tooling can do the same.

**A published release never changes.** If a tag is moved, or deleted and pushed again at different
content, its run refuses: the version is already recorded with other bytes, and players and mirrors
already have those. Declare the next version and tag that instead.

**Until it is recorded, a tag is just a tag.** If the run fails before the record step, say because
you tagged a commit that does not declare the version, nothing was published. Fix it and move the
tag:

```sh
git tag -f my_mod-1.1.0
git push -f origin my_mod-1.1.0
```

**Protected branches.** The record is pushed to your default branch. If a branch protection rule
or ruleset there requires pull requests, let GitHub Actions bypass it, or tag runs fail at the
record step and publish nothing.

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
correct it: fix a typo in 1.0's notes on the default branch and the page and manifest follow.

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
says so; that check covers releases that are recorded or not yet tagged, not tags from before
this template recorded releases, which are history nobody can rewrite.

## Channels

Every release has a channel. `stable` is the default; `beta` and `legacy` are conventional; any
lowercase name works. A channel's head is its highest-precedence release that is neither yanked nor
deprecated, and the manifest lists every head.

`development` is special: it is built from the default branch on every push, never declared, and
its version is generated to sort just after the newest tag: `1.2.0` becomes `1.2.1-dev.7`, and a
decimal `0.963` becomes `0.9631-dev.7`, where the last number counts commits to the project since
that tag. Its archives are on a GitHub release called `development`, replaced on every push. Turn
it off with `[package] development = false`.

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

Only tags shaped like releases start a run: `<slug>-<version>`, with the version starting with a
digit. Anything else, like a `V5` tag, is ignored.

1. Validates the repository and runs the template's tests.
2. Checks out the tag and builds the release: the archive, its offline documentation, and the
   release notes.
3. Signs the archive with Sigstore if `[provenance] sigstore = true`.
4. Checks out the default branch and records the release in `mod.lock`. If it is already recorded,
   the rebuilt archive and its install and compatibility data must match the record, or the run
   stops here.
5. Creates the GitHub release for the tag as a draft, attaches the archive and signature, and
   publishes it, with the release's own notes and the archive's digest as its description.
6. Uploads to Nexus Mods if `[nexusmods] file_group_id` is set.
7. Starts a run on the default branch, which rebuilds the development build and the site from a
   commit that includes the record, and deploys them.

Tags pushed before V5 still show in the changelog, marked **unverified**. The manifest leaves them
out, because nothing records what their archives contained.
