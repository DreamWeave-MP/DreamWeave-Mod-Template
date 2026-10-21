# AGENTS.md

## Repository shape

- The DreamWeave Mod Template: the build tool, a Jess package `org.dreamweave.mod-template` whose
  Package Source is this repository root (`jess.toml`, `src/`, `tests/`, `bench/`), and the
  DreamWeave site it builds for itself: `content/template` is the package's own project page
  (`format = "jpk"`, `jess = "org.dreamweave.mod-template"`); `content/home` is Candlelight and
  `content/simplified` Tallow, the example mods, at home because a copy of this repository is a
  mod site: StroggForge's scaffold step strips the tool's source and `content/template` from a
  copy on its first push. The tool validates `content/<project>/mod.toml`,
  packages byte-reproducible archives and JPKs, records releases, and writes the protocol documents
  (`static/dreamweave.json`, `static/dreamweave/projects/<id>.json`) and what only CI knows
  (`static/dreamweave/view.json`). Rendering is `org.dreamweave.site` with the theme
  `org.dreamweave.theme` (`~/GitHub/rust-reimplementations/jess/jpk/dreamweave-site`, `-theme`);
  `jess.lock` pins both. `jess-workspace.toml` lists the root as its one member; a site made from
  the template lists none and names the template in `[dev-dependencies]`. No Python, no Zola.
- A `format = "jpk"` project names its Package Source by package id (`jess = "<id>"`), one of the
  jess workspace's members; a repository publishes as many Jess packages as it has projects for.
  The template packs them itself through `@jess/package`: at the tag's version for a release, and
  past the newest release as `-dev.<build>` on every push. There is no external pack step.
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
  bytes written by `src/archive.jsl`, not a zip library. Anything that makes the offline documentation render
  depend on `mod.lock`, git state or the clock breaks re-running a tag's job; offline mode reads only
  the committed tree.
- `release` reads the tag's committed blobs; `check` and `build` read the working tree; `record`
  runs on a checkout of the default branch.
- The Tera model (`templates/macros/project.html`) and `src/model.jsl` apply the same defaults; the tests
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

The build tool's tests: `jess workspace test` here, or `jess package test . --package-path ~/GitHub/rust-reimplementations/jess/jpk`
before the lock exists. Pinned outputs under `tests/fixtures/expected` are rewritten with
`DREAMWEAVE_UPDATE_PINS=1` after a deliberate change, and the diff read. The protocol schemas in
`static/schemas/` are vendored by AsHyAmS.

## Style

Sass is indented syntax, never SCSS. Luau (the build tool, the generator and the theme): strict, full-word names, errors that say what
to fix, no comments that narrate code. Site prose follows DreamWeave's voice: direct, concrete, dry.
Commit atomically with `FEAT:`/`FIX:`/`BREAK:`/`UPDATE:`/`CLEANUP:`/`DOCS:`/`TEST:` subjects.
