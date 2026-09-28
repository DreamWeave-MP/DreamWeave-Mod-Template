# AGENTS.md

## Repository shape

- The DreamWeave Mod Template: a Zola site plus `./buildSite` (Python, `tools/dreamweave/`) that
  validates `content/<project>/mod.toml`, packages byte-reproducible archives, and writes the
  distribution protocol documents (`static/dreamweave.json`, `static/dreamweave/projects/<id>.json`)
  and the view the templates render (`static/dreamweave/view.json`).
- Human intent: `content/<project>/index.md` (display name, summary, prose) and `mod.toml`
  (everything structured). Machine-written but reviewed: `mod.lock`. Generated and gitignored:
  `static/dreamweave*`, `content/**/_changelog.md`, `dist/`, `public/`. Never edit generated files.
- The protocol is specified in `content/guide/protocol/` and `static/schemas/`. Code, schemas and
  spec change together or not at all.

## Invariants that are easy to break

- Archives must stay byte-reproducible: stored entries, sorted, 1980-01-01, permissions from git,
  bytes written by `archive.py`, not `zipfile`. Anything that makes the offline documentation render
  depend on `mod.lock`, git state or the clock breaks `lock`/`verify`; offline mode reads only the
  committed tree.
- `lock` and `verify` read committed blobs; `check`, `build` and `serve` read the working tree.
- `schema_version` "2" core fields are frozen. New data goes in extensions or waits for "3".
- Validation is structural (ids, references, paths, versions, order of publishable releases). Do not
  add editorial rules.
- Versions carry their project's scheme (`numeric` or `decimal`); never compare across schemes.
- Tera: `default(value=<variable>)` double-escapes, dict literals do not exist, tests only work on
  variables, function calls cannot be `if` conditions. Use `| safe` only on URLs and trusted HTML.
- The docs shell (`templates/docs/`, `sass/docs.sass`, `static/docs/docs.js`) and the schematic
  shortcode are imported by StroggForge; keep class names and arguments stable.
- Nothing may default to DreamWeave's accounts. Analytics stay off until configured. Comments are on,
  but `tools/dreamweave/comments.py` looks up giscus ids for the site's own repository at build time;
  never reintroduce pasted `repo_id`/`category_id`. No comment content is ever built into the site.

## Verification

```sh
python3 -m unittest discover -s tests      # protocol, validation and release lifecycle (needs zola)
./buildSite check
./buildSite build && ./buildSite schemas && zola build && ./buildSite links
actionlint                                 # workflow, including embedded shellcheck
stylua --check $(git ls-files 'content/*.lua')
```

The pinned Zola version is `./buildSite zola-version`; CI installs exactly that one.

## Style

Sass is indented syntax, never SCSS. Python: full-word names, explicit types, errors that say what
to fix, no comments that narrate code. Site prose follows DreamWeave's voice: direct, concrete, dry.
Commit atomically with `FEAT:`/`FIX:`/`BREAK:`/`UPDATE:`/`CLEANUP:`/`DOCS:`/`TEST:` subjects.
