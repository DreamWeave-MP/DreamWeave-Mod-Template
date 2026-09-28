+++
title = "Start here"
description = "From Use this template to a published mod page in about fifteen minutes."
weight = 10

[extra]
kind = "guide"
+++

You need a GitHub account and git. To preview locally you also need
[Zola](https://www.getzola.org/documentation/getting-started/installation/) 0.22 or newer, which is
one binary.
That is the whole list. Validating, packaging, hashing and publishing all happen in GitHub Actions,
so there is no Python, Node or Rust to install, and no DreamWeave account.

## 1. Make your repository

Click **Use this template** on the template's GitHub page, not **Fork**. A fork drags the
template's history and upstream relationship along with it; a template copy is yours from the
first commit.

In the new repository, set **Settings → Pages → Source** to **GitHub Actions**.

## 2. Tell it who you are

Open `config.toml` and change the two values marked REQUIRED:

```toml
[extra]
github_username = "your-name"
github_project = "your-repository"
```

Release downloads are served from that repository's GitHub Releases, and CI refuses to build if
these do not name the repository it runs in. While you are there, set `title`, `description`,
`logo_text` and `base_url`. On GitHub Pages the workflow uses the real Pages URL anyway, so
`base_url` mostly matters for local previews and for the links inside offline documentation.

## 3. Turn on comments

Every project page ends in a discussion thread, backed by your repository's GitHub Discussions
through [giscus](https://giscus.app). It is the fastest way players will tell you what broke. To
switch it on:

1. **Settings → General → Features → Discussions**: tick it.
2. Install the [giscus app](https://github.com/apps/giscus) on the repository.

That is all. `config.toml` already asks for comments in the `General` category, and the build looks
up your repository's ids itself; there is nothing to paste. Until both steps are done, the build
prints a warning and pages simply have no thread.

Analytics are off, and stay off until you set up your own GoatCounter code.

## 4. Make the project yours

The template ships two example projects. `content/home` is Candlelight, the complete example.
`content/simplified` is Tallow, the minimal one. Turn `content/home` into your mod, and delete
Tallow once you no longer need to crib from it.

**Replace the id.** Every project has a permanent identity that no other project may share: a
random UUID, like `4d0c9f6e-2b1a-4c8e-9f3a-7e5d1b2c6a90`. Anything that makes them will do:
`uuidgen` on Linux and macOS, `[guid]::NewGuid()` in PowerShell, or any online generator. Or don't
bother: CI refuses the template's example ids, and its error hands you a fresh one to paste.

Put it in `content/home/mod.toml` as `id`, and set `slug` to a short lowercase name with
underscores. The slug becomes your archive's name (`my_mod.zip`) and your release tags
(`my_mod-1.0.0`).

**Rewrite the page.** In `content/home/index.md`, `title` is your mod's display name and
`description` is its one-line summary. The body is the overview: what the mod does and why.

**Replace the files.** Delete Candlelight's `00 Core`, `10 Tamriel Rebuilt`, `20 Flames 2K`,
`21 Flames 4K`, `docs` and `media`, and put your mod in `content/home`. For a mod that is one data
directory, your `scripts/`, `textures/` and content files go straight into `content/home`.

Then cut `mod.toml` down to what is true:

```toml
id = "your fresh UUID"
slug = "my_mod"

[runtimes]
openmw = ">=0.49"

[openmw]
content_files = ["MyMod.omwscripts"]

[[releases]]
version = "1.0.0"
date = 2026-10-01
summary = "First release."
```

That is a complete, network-ready project. [Project pages](@/guide/project-pages.md) covers the
rest of what you can say about it, and [mod.toml reference](@/guide/mod-toml.md) lists every key.

## 5. Preview

```sh
zola serve
```

Your site is on <http://127.0.0.1:1111>, and it reloads when you save. The project page is built
from `mod.toml` and `mod.lock`, the same files CI reads, so what you see is what gets published.
Three things only exist once CI has built the site: the development build, the comment thread, and
the checks on the network page.

## 6. Push

Commit and push to your default branch. The workflow validates every project, packages a
development build, builds the site and deploys it. Your page appears at
`https://your-name.github.io/your-repository/home/`, and the development archive is on a GitHub
release called `development`.

If something is wrong, the run fails and says which file, which key, and what to do about it. Every
push and pull request gets the same check, so a mistake never reaches the published site.

## 7. Release

When you have a version worth calling one, [Releases](@/guide/releases.md) walks through it. The
short version: declare it in `mod.toml`, then push a tag.

```sh
git commit -am "My Mod 1.0.0"
git tag my_mod-1.0.0
git push origin HEAD my_mod-1.0.0
```

CI builds the archive from the tag, records its hash in `mod.lock` with a commit of its own,
publishes it, and updates the site. Run `git pull` before you next push, to pick up that commit.

## One mod or several

The template opens straight onto `content/home` because most repositories hold one mod. To host
several, give each its own directory under `content/` with its own `index.md` and `mod.toml`, and
delete `redirect_to = "home"` from `content/_index.md`. The front page becomes a paginated catalog,
`paginate_by` projects at a time. Nothing else changes: every project keeps its own id, slug,
releases and tags.
