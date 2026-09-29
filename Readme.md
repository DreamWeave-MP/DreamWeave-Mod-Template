# DreamWeave Mod Template

A mod page, its documentation, installable archives, and the metadata tools need to find, verify
and install the mod, all from one repository and servable from any static host.

You write two files per mod. The template validates them, packages byte-reproducible archives,
publishes releases, and builds a site that people read and DreamWeave clients (CHIMERA, St4sh,
anything that follows [the protocol](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/protocol/))
read without scraping it.

## Start

1. Click **Use this template** (not Fork) and create your repository. Set
   **Settings → Pages → Source** to **GitHub Actions**.
2. In `config.toml`, set `github_username` and `github_project` to your repository. For comments,
   enable Discussions on it and install the [giscus app](https://github.com/apps/giscus).
3. Give `content/home/mod.toml` a fresh random UUID as its `id` (`uuidgen` makes one; so does CI's
   error if you forget). Set `slug` to a short name like `my_mod`: it names your archive and your
   release tags.
4. Replace Candlelight's files in `content/home` with your mod, and rewrite `content/home/index.md`:
   `title` is the mod's name, `description` its summary, the body its page.
5. Preview with `zola serve`, then commit and push. The workflow validates everything and publishes
   the page and a development build.
6. Release: add a `[[releases]]` entry, then

   ```sh
   git commit -am "My Mod 1.0.0"
   git tag my_mod-1.0.0 && git push origin HEAD my_mod-1.0.0
   ```

   CI builds the archive from the tag, records its hash in `mod.lock` with a commit of its own, and
   publishes it.

[Start here](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/start-here/) walks
through it properly. You need git, plus [Zola](https://www.getzola.org/) to preview. Everything
else runs in GitHub Actions: no Python, no Node, no Rust, no accounts.

## What you get

- **A mod page** with compatibility, requirements, conflicts, components, screenshots with a
  keyboard-driven viewer, install instructions generated per package format including the exact
  `openmw.cfg` lines, a changelog, and credits. Sections with nothing to say do not appear.
- **Archives that ship their documentation**: the page and its docs rendered as offline HTML in
  `Documentation/`, next to your mod's files. Flat, BAIN, or BAIN with a generated FOMOD installer.
- **Modding tools too**: a Rust program in the same repository is built per platform by
  StroggForge, recorded and published like any release, with a download per platform on its page.
  A Rust library goes to crates.io, and its site becomes its API reference.
- **Releases you can verify**: CI records each release's SHA-256 in `mod.lock` when its tag is
  pushed, and from then on refuses to publish that version with any other bytes.
- **A place on the network**: `dreamweave.json` and a manifest per project, linked from every page,
  describing identity, releases, artifacts, sources, dependencies and install data. Mirrors serve
  bytes by hash; they never become the authority.
- **Documentation sections** with a recursive sidebar, breadcrumbs, a page table of contents,
  scoped search and copy buttons.
- **One mod or a catalog of them.** Delete one line and the front page becomes a paginated catalog;
  every project keeps its own id, releases and tags.
- **A discussion on every mod page**, backed by your repository's GitHub Discussions through giscus
  and styled to match. Enable Discussions and install the giscus app; there are no ids to paste.
- **Nothing phoning home.** No analytics, web fonts or CDN unless you configure them. Every page works
  without JavaScript, and comments are the only third-party embed.

## What CI runs

You never run `./buildSite`; CI does, through StroggForge's `modGlobalBuild` workflow, which
`.github/workflows/build_site.yml` calls. It is Python, and it lives in `tools/dreamweave/`.

| Command | When | Does |
|---|---|---|
| `./buildSite check` | every push | Validate every project, including its files against `mod.toml`; suggest a `mod.toml` for V4 pages |
| `./buildSite build` | every push | Package development builds and write the protocol files |
| `./buildSite links` | every push | Check the built site's local links, anchors and HTML structure |
| `./buildSite schemas` | every push | Validate the generated index and manifests against the published schemas |
| `./buildSite release <tag>` | release tags | Build a release from its tag |
| `./buildSite record` | release tags | Record that release in `mod.lock` on the default branch |

## Where things live

| Path | What |
|---|---|
| `content/<project>/index.md` | The mod's name, summary and page |
| `content/<project>/mod.toml` | Everything structured about the mod |
| `content/<project>/mod.lock` | What each published release contains (written by CI) |
| `content/<project>/…` | The mod itself and its docs; all of it ships |
| `config.toml` | The site: URL, title, repository, palette, header links |
| `sass/brand.sass` | Your branding; the template never touches it |
| `templates/`, `sass/`, `static/` | The template's presentation |
| `tools/dreamweave/` | The tooling CI runs through `./buildSite` |
| `static/schemas/` | JSON Schemas for everything the site publishes |
| `tools/tests/` | The template's own tests: `python3 -m unittest discover -s tools/tests` |

## Documentation

The [guide](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/) covers
[project pages](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/project-pages/),
[every mod.toml key](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/mod-toml/),
[releases](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/releases/),
[packages](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/packages/),
[dependencies](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/dependencies/),
[customizing](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/customizing/),
[migrating from V4](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/migration/),
and the [architecture](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/architecture/).
It is also in this repository under `content/guide/`; delete it from your copy if you like.

## License

The template is AGPL-3.0 (see `LICENSE`). The bundled fonts carry their own licenses, in the
`LICENSE-*Font.txt` and `README-GalBasicFont.txt` files. Your mod's license is yours: set `license`
in its `mod.toml`.

If this saves you time, consider sponsoring DreamWeave on [Ko-fi](https://ko-fi.com/magicaldave).
