# AGENTS.md

## Repository shape

- The DreamWeave Mod Template: a DreamWeave site built through jess. The build tool is the Jess
  package `org.dreamweave.mod-template` (source: `~/GitHub/rust-reimplementations/jess/jpk/dreamweave-mod-template`),
  which validates `content/<project>/mod.toml`, packages byte-reproducible archives, records
  releases, and writes the protocol documents (`static/dreamweave.json`,
  `static/dreamweave/projects/<id>.json`) and what only CI knows (`static/dreamweave/view.json`).
  Rendering is `org.dreamweave.site` with the theme `org.dreamweave.theme` (siblings under `jpk/`);
  `jess.lock` pins all three. This repository holds no Python, no Zola and no copy of the theme.
- Authors' tools are an editor, git and jess. `jess workspace run --trusted dreamweave-site -- public <url>`
  must render every page: the theme's templates build the project model from `mod.toml` and
  `mod.lock` themselves (`templates/macros/project.html` in the theme), and `view.json` only adds CI facts.
- Human intent: `content/<project>/index.md` (display name, summary, prose) and `mod.toml`
  (everything structured). Written by CI, committed by `github-actions[bot]`: `mod.lock`. Generated
  and gitignored: `static/dreamweave*`, `content/**/_changelog.md`, `dist/`, `public/`. Never edit
  generated files.
- The protocol is specified in `content/guide/protocol/` and `static/schemas/`. Code, schemas and
  spec change together or not at all.
- CI lives in StroggForge (`~/GitHub/rust-reimplementations/StroggForge`, sibling checkout):
  `build_site.yml` only calls its `modGlobalBuild`, and its Rust workflows call the same one with
  `mod_template: true`. The build tool's command targets (`dreamweave-check`, `-build`, `-site`,
  `-links`, `-release`, `-record`, `-record-crates`, `-record-releases`) and the `dist/` files that
  workflow uses are an interface; change them together with StroggForge, and move the pinned tag.
- StroggForge builds, signs and publishes Rust programs and crates; the template only records them.
  No Rust build inputs belong in `mod.toml` or the build tool.

## Invariants that are easy to break

- Archives must stay byte-reproducible: stored entries, sorted, 1980-01-01, permissions from git,
  bytes written by `archive.py`, not `zipfile`. Anything that makes the offline documentation render
  depend on `mod.lock`, git state or the clock breaks re-running a tag's job; offline mode reads only
  the committed tree.
- `release` reads the tag's committed blobs; `check` and `build` read the working tree; `record`
  runs on a checkout of the default branch.
- The Tera model (`templates/macros/project.html`) and `model.py` apply the same defaults; the tests
  compare the page with the manifest. mod.lock lists records in version order, which is how the
  templates find channel heads without comparing versions.
- `schema_version` "2" core fields are frozen. New data goes in extensions or waits for "3".
- Validation is structural (ids, references, paths, versions, order of publishable releases). Do not
  add editorial rules.
- Versions carry their project's scheme (`numeric` or `decimal`); never compare across schemes.
- Tera: `default(value=<variable>)` double-escapes, dict literals do not exist, tests only work on
  variables, function calls cannot be `if` conditions, and nothing may follow a filter in a `~`
  chain. Macro files are imported under a fixed name and call their siblings through it
  (`dw_macros::`, `project_model::`): with `extends`, `self::` only resolves in the first imported
  file. Use `| safe` only on URLs, trusted HTML and JSON the templates wrote.
- The docs shell (`templates/docs/`, `sass/docs.sass`, `static/docs/docs.js`) and the schematic
  shortcode are imported by StroggForge; keep class names and arguments stable.
- Nothing may default to DreamWeave's accounts. Analytics stay off until configured. Comments are on,
  but the build tool looks up giscus ids for the site's own repository at build time;
  never reintroduce pasted `repo_id`/`category_id`. No comment content is ever built into the site.

## Verification

```sh
jess workspace sync --locked                                   # the template, theme and generator jess.lock pins
jess workspace run --trusted dreamweave-check
jess workspace run --trusted dreamweave-build -- "$BASE_URL"
jess workspace run --trusted dreamweave-site -- public "$BASE_URL"
jess workspace run --trusted dreamweave-links -- public "$BASE_URL"
actionlint                                 # workflow, including embedded shellcheck
stylua --check $(git ls-files 'content/*.lua')
```

The build tool's own tests live with its source: `jess package test jpk/dreamweave-mod-template --package-path jpk`
in the jess checkout. The protocol schemas in `static/schemas/` are validated there and vendored by AsHyAmS.

## Style

Sass is indented syntax, never SCSS. Luau (the build tool, the generator and the theme): strict, full-word names, errors that say what
to fix, no comments that narrate code. Site prose follows DreamWeave's voice: direct, concrete, dry.
Commit atomically with `FEAT:`/`FIX:`/`BREAK:`/`UPDATE:`/`CLEANUP:`/`DOCS:`/`TEST:` subjects.
