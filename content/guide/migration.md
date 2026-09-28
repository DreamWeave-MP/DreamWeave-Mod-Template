+++
title = "Migrating from V3"
description = "Move a V3 site, St4sh-sized or not, onto mod.toml without losing its history."
weight = 110

[extra]
kind = "guide"
+++

V4 is a breaking version, and it is tagged as one. A site that is not ready to move keeps building
from the V3 tag, unchanged. When you move, CI tells you what is left: every page that still carries
V3 project frontmatter without a `mod.toml` is an error that names the page, and the same run
writes you a suggested `mod.toml` for it. There is nothing to install or run yourself.

## What changed

| V3 | V4 |
|---|---|
| Project metadata in `index.md`'s `[extra]` | `mod.toml` next to `index.md` |
| Identity: the title's slug | `id`, a UUID you choose once; `slug` names archives and tags |
| `extra.version` | `[[releases]]`, published by pushing a tag; CI records each in `mod.lock` |
| `install_info` | `[openmw]` or `[[components]]`, checked against the files |
| Every directory under `content/` packaged, minus `excluded_dirs` | Every directory with a `mod.toml` |
| Zip with deflate, built by walking the file system | Stored, byte-reproducible zip from committed files, with rendered docs |
| `<repo>-<tag>.modManifest` release asset, `schema_version: "1"` | `dreamweave.json` and `dreamweave/projects/<id>.json` on the site, `schema_version: "2"` |
| Commit-log changelog | Release notes in `mod.toml`, one changelog for the page, the manifest and the GitHub release |
| `./buildSite --build --changelog --tag …` | Nothing to run: CI validates, packages and records releases, and `zola serve` previews |
| terminimal theme, `accent_color`, `background_color` | The template's own layout, `palette` and `accent`, tokens in `sass/brand.sass` |
| `giscus = { repo_id, category_id, … }` with pasted ids | `[extra.comments]`; the build looks the ids up for your own repository |
| GoatCounter pointing at DreamWeave's account by default | Off until you set your own code |
| `segment_versions`, `excluded_dirs`, `button_style`, `use_custom_titles`, `enable_post_view_navigation` | Gone |

The shortcodes existing pages call, `install_instructions`, `credits`, `usage_note`, `image` and
`figure`, keep their names and arguments.

## Step by step

**1. Bring in the template.** Copy V4's `templates/`, `sass/`, `static/js/`, `static/docs/`,
`static/schemas/`, `static/img/mark.svg`, `tools/`, `buildSite` and `.github/workflows/build_site.yml`
into your repository, delete `themes/terminimal`, and merge `config.toml` by hand: keep your
`base_url`, `title`, `github_username`, `github_project` and `ignored_content`; replace
`accent_color` with `palette`; delete what the table above says is gone. Keep your own shortcodes
and `data/`.

**2. Push, and let CI suggest a mod.toml per project.** The check fails on every V3 page, and the
same run writes a suggestion for each: in the run's summary, and in its `mod-toml-suggestions`
artifact, laid out like your repository. Download the artifact and unzip it at the repository root,
and every page gets its `mod.toml`. The comments at the top of each file say what the converter
could not decide. It reads the page's V3 frontmatter and the repository's tags, and:

- picks a fresh `id`;
- sets `slug` to whichever of the title's slug or the directory's name already owns
  `<slug>-<version>` tags, so existing tags stay this project's history (St4sh's `birr` is tagged
  `birr-*`, while its title would slug to `beta_icons_restored_and_reimagined`);
- turns those tags into `[[releases]]` with their dates, and sets `versioning = "decimal"` when the
  history only sorts that way (S3maphore: 0.54, 0.6, 0.63, 0.9, 0.963);
- keeps every V3 data directory installed, so the archive installs exactly as before, and carries
  content files, fallback entries and Nexus ids across;
- skips placeholder versions like `UNRELEASED`, and a frontmatter version that was never bumped past
  the last tag.

**Comments.** Replace the V3 `giscus = {…}` line with `[extra.comments]` (see
[Customizing](@/guide/customizing.md#comments)); the build refuses the old one. Pasted ids are how a
copied config sends comments to the wrong repository: St4sh's config carried the Mod Template's
`repo_id`, so the one St4sh page thread that exists was created in the Mod Template's Discussions.
Threads are still matched by page path, so threads created in the right repository keep their pages.

**3. Review it.** Narrow `openmw = "*"` to what you have tested. Split data directories into
`[[components]]` with `format = "bain"` or `"fomod"` if players should choose. Add notes to the
newest release.

**4. Clean the page.** Delete the V3 keys the notes list from `index.md`'s `[extra]`.

**5. Push again.** Expect CI to find real problems. Moving St4sh found a content file declared with the wrong case
(`Baldurwind.omwaddon` against a committed `baldurwind.omwaddon`), content files that are gitignored
build output and so were never in the V3 archives either, and docs linking to sibling pages as
`page.md`, which Zola never resolves. The link check after the site build finds the last kind.

## What happens to old releases

Tags from before V4 stay, and the changelog shows them marked **unverified**. The manifest leaves
them out: nothing recorded what their archives contained, and a client that cannot verify an archive
should not be offered it. Development builds count from the newest tag, so players already on 0.963
see 0.9631-dev.N, not something older. Tag the next release and it is on the network.

## Coming from somewhere else

If a mod is on Nexus or a forum today, you do not have to move it. Put the page on the template,
add `[nexusmods] mod_id`, and publish releases from the repository; the Nexus page becomes a link and,
with `file_group_id`, an upload target. If you already publish archives elsewhere and want to keep
doing so, list that host in `[[mirrors]]`.
