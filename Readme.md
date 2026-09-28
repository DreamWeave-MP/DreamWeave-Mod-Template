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
2. In `config.toml`, set `github_username` and `github_project` to your repository.
3. Run `./buildSite new-id` and put the result in `content/home/mod.toml` as `id`. Set `slug` to a
   short name like `my_mod`: it names your archive and your release tags.
4. Replace Candlelight's files in `content/home` with your mod, and rewrite `content/home/index.md`:
   `title` is the mod's name, `description` its summary, the body its page.
5. Preview with `./buildSite serve`, then commit and push. The workflow publishes the page and a
   development build.
6. Release: add a `[[releases]]` entry, then

   ```sh
   ./buildSite lock my_mod
   git add content/home/mod.lock && git commit -m "RELEASE: My Mod 1.0.0"
   git tag my_mod-1.0.0 && git push --atomic origin HEAD my_mod-1.0.0
   ```

[Start here](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/start-here/) walks
through it properly. You need git and Python 3.11+ with PyYAML (`pip install -r tools/requirements.txt`),
plus [Zola](https://www.getzola.org/) to preview. No Node, no Rust, no accounts.

## What you get

- **A mod page** with compatibility, requirements, conflicts, components, screenshots with a
  keyboard-driven viewer, install instructions generated per package format including the exact
  `openmw.cfg` lines, a changelog, and credits. Sections with nothing to say do not appear.
- **Archives that ship their documentation**: the page and its docs rendered as offline HTML in
  `Documentation/`, next to your mod's files. Flat, BAIN, or BAIN with a generated FOMOD installer.
- **Releases you can verify**: an archive's SHA-256 is recorded in `mod.lock` before its tag exists,
  and CI refuses to publish a tag whose archive comes out different.
- **A place on the network**: `dreamweave.json` and a manifest per project, linked from every page,
  describing identity, releases, artifacts, sources, dependencies and install data. Mirrors serve
  bytes by hash; they never become the authority.
- **Documentation sections** with a recursive sidebar, breadcrumbs, a page table of contents,
  scoped search and copy buttons.
- **One mod or a catalog of them.** Delete one line and the front page becomes a paginated catalog;
  every project keeps its own id, releases and tags.
- **Nothing phoning home.** No analytics, comments, web fonts or CDN unless you configure them.
  Every page works without JavaScript.

## Commands

| Command | Does |
|---|---|
| `./buildSite check` | Validate every project, including its files against `mod.toml` |
| `./buildSite serve` | Write preview data, run `zola serve`, regenerate when `mod.toml` changes |
| `./buildSite build` | Package development builds and write the protocol files, as CI does |
| `./buildSite lock <slug>` | Record the next release's archive hash before tagging it |
| `./buildSite verify <tag>` | Rebuild a tagged release and fail unless it matches `mod.lock` (CI) |
| `./buildSite links` | Check the built site's local links, anchors and HTML structure |
| `./buildSite schemas` | Validate the generated index and manifests against the published schemas |
| `./buildSite migrate <dir>` | Print a `mod.toml` for a V3 page |
| `./buildSite new-id` | Print a fresh project id |

## Where things live

| Path | What |
|---|---|
| `content/<project>/index.md` | The mod's name, summary and page |
| `content/<project>/mod.toml` | Everything structured about the mod |
| `content/<project>/mod.lock` | What each published release contains (written by `lock`) |
| `content/<project>/…` | The mod itself and its docs; all of it ships |
| `config.toml` | The site: URL, title, repository, palette, header links |
| `sass/brand.sass` | Your branding; the template never touches it |
| `templates/`, `sass/`, `static/` | The template's presentation |
| `tools/dreamweave/` | The build tool `./buildSite` runs |
| `static/schemas/` | JSON Schemas for everything the site publishes |
| `tests/` | The template's own tests: `python3 -m unittest discover -s tests` |

## Documentation

The [guide](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/) covers
[project pages](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/project-pages/),
[every mod.toml key](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/mod-toml/),
[releases](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/releases/),
[packages](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/packages/),
[dependencies](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/dependencies/),
[customizing](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/customizing/),
[migrating from V3](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/migration/),
and the [architecture](https://dreamweave-mp.github.io/DreamWeave-Mod-Template/guide/architecture/).
It is also in this repository under `content/guide/`; delete it from your copy if you like.

## License

The template is AGPL-3.0 (see `LICENSE`). The bundled fonts carry their own licenses, in the
`LICENSE-*Font.txt` and `README-GalBasicFont.txt` files. Your mod's license is yours: set `license`
in its `mod.toml`.

If this saves you time, consider sponsoring DreamWeave on [Ko-fi](https://ko-fi.com/magicaldave).
