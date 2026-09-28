+++
title = "Start here"
description = "From Use this template to a published mod page in about fifteen minutes."
weight = 10

[extra]
kind = "guide"
+++

You need a GitHub account, git, and Python 3.11 or newer with PyYAML
(`python3 -m pip install -r tools/requirements.txt`). To preview locally you also need
[Zola](https://www.getzola.org/documentation/getting-started/installation/). You do not need Node,
Rust, a DreamWeave account, or any editor in particular.

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

**Replace the id.** Every project has a permanent identity that no other project may share:

```sh
./buildSite new-id
```

Put the result in `content/home/mod.toml` as `id`, and set `slug` to a short lowercase name with
underscores. The slug becomes your archive's name (`my_mod.zip`) and your release tags
(`my_mod-1.0.0`). The build refuses the template's example ids, so you cannot forget this one.

**Rewrite the page.** In `content/home/index.md`, `title` is your mod's display name and
`description` is its one-line summary. The body is the overview: what the mod does and why.

**Replace the files.** Delete Candlelight's `00 Core`, `10 Tamriel Rebuilt`, `20 Flames 2K`,
`21 Flames 4K`, `docs` and `media`, and put your mod in `content/home`. For a mod that is one data
directory, your `scripts/`, `textures/` and content files go straight into `content/home`.

Then cut `mod.toml` down to what is true:

```toml
id = "your id from ./buildSite new-id"
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
./buildSite serve
```

This validates everything, writes the preview data and starts Zola on <http://127.0.0.1:1111>.
It regenerates when you save `mod.toml`. Mistakes show up in the terminal with the file, the key
and what to do about them. `./buildSite check` runs the same validation without serving anything.

## 6. Push

Commit and push to `main`. The workflow validates, packages a development build, builds the site
and deploys it. Your page appears at `https://your-name.github.io/your-repository/home/`, and the
development archive is on a GitHub release called `development`.

## 7. Release

When you have a version worth calling one, [Releases](@/guide/releases.md) walks through it. The
short version:

```sh
./buildSite lock my_mod
git add content/home/mod.lock
git commit -m "RELEASE: My Mod 1.0.0"
git tag my_mod-1.0.0
git push --atomic origin HEAD my_mod-1.0.0
```

## One mod or several

The template opens straight onto `content/home` because most repositories hold one mod. To host
several, give each its own directory under `content/` with its own `index.md` and `mod.toml`, and
delete `redirect_to = "home"` from `content/_index.md`. The front page becomes a paginated catalog,
`paginate_by` projects at a time. Nothing else changes: every project keeps its own id, slug,
releases and tags.
