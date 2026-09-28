+++
title = "Distribution"
description = "Artifacts, digests, sources, mirrors, and where Nexus and GitHub fit."
weight = 60

[extra]
kind = "guide"
+++

A URL says where something is. A hash says what it is. The manifest keeps them apart, which is
the whole trick behind mirrors, caches and moving hosts.

## An artifact

Each release in the manifest lists its artifacts:

```json
{
  "id": "fomod",
  "format": "fomod",
  "filename": "candlelight.zip",
  "media_type": "application/zip",
  "size": 248145,
  "digests": { "sha256": "11b91e6dd20f196f8d2efc9b7fb4c6b6e3de732447f490584709a2ab8aa83fa6" },
  "sources": [
    { "url": "https://github.com/OWNER/REPO/releases/download/candlelight-1.1.0/candlelight.zip", "kind": "publisher" },
    { "url": "https://cache.example.org/sha256/11b91e6d…", "kind": "mirror", "name": "Example cache" }
  ],
  "signatures": []
}
```

The digest is the artifact's identity. The file name is a convenience, and the sources are places to
try. A client picks any source, downloads, checks size and SHA-256, and throws the bytes away if
either is wrong, then tries the next source. The first source is not special; `kind` only says
whether the publisher operates it.

## Sources

Every artifact has at least one publisher source: the GitHub release of the repository in
`config.toml`, under the release's tag (`candlelight-1.1.0`) or `development`.

Add mirrors in `mod.toml`:

```toml
[[mirrors]]
name = "Ashlands archive"
url = "https://archive.example.org/{slug}/{version}/{filename}"

[[mirrors]]
name = "Content-addressed cache"
url = "https://cache.example.org/sha256/{sha256}"
```

The placeholders are `{slug}`, `{version}`, `{tag}`, `{filename}` and `{sha256}`, and a mirror must
use `{filename}` or `{sha256}`, or every artifact would share one URL. Listing a mirror costs you
nothing: a client verifies whatever it downloads, so a mirror that serves the wrong bytes wastes a
download and nothing else.

A mirror does not need to be listed to be useful. Anything that can say "I have the bytes whose
SHA-256 is H" can serve a client that already knows H from the manifest. The manifest, served from
the project's own site, stays the authority on what H is.

## Where Nexus fits

```toml
[nexusmods]
mod_id = 57511
file_group_id = "abc123"
```

`mod_id` puts a Nexus Mods link on the page and an `integrations.nexusmods` entry in the manifest.
It is a location, like any other: the project's identity is its id, and moving off Nexus changes
nothing about it. `file_group_id` makes the workflow upload each tagged release to Nexus too.

## Moving hosts

Because identity is the id and content is the digest, a project can move from GitHub Pages to
St4sh to its own domain without becoming a different project. Publish from the new place, keep the
id, and clients that re-discover it see the same project, the same releases and the same digests at
new URLs. Nothing in the protocol depends on the domain.
