+++
title = "The network"
description = "How clients, indexes and mirrors use what this site publishes, and how to check you are ready."
weight = 90

[extra]
kind = "guide"
+++

There is no DreamWeave server in the middle of this. A mod's own site says what the mod is, and
anything else is a reader.

{{ schematic(data_path="data/schematics/network.json") }}

## Is this mod ready?

Every site built from the template has a [Network](@/network.md) page. For each project it shows the
id, the manifest URL and digest, and a list of checks: discovery, published releases, channel heads,
content hashes, resolvable relationships, signatures, source revisions, mirrors, and any content file
in the payload that `mod.toml` does not mention. They are computed when the site is built and cover
structure, not taste.

"Ready" means a client starting from your page can find the manifest, pick a release for its
channel, download it from a listed source, and verify it. A project with only a development channel
is on the network; a project with a recorded stable release is on it properly.

## CHIMERA and other clients

A client never needs to know this template exists. Given any URL on the site it:

1. finds `dreamweave.json` through the page's `<link>` or by walking up the path;
2. reads the project manifest and checks `project.id`;
3. picks the head of the channel the player follows and checks runtimes, platforms and critical
   extensions;
4. resolves `requires` by id or capability, checks `conflicts`;
5. downloads an artifact from any source and verifies size and SHA-256, falling back to the next
   source on mismatch;
6. optionally verifies a Sigstore bundle against the identity the manifest names;
7. applies the declarative install data: data directories, content files in order, fallback entries,
   settings the player agrees to.

Everything in that list is in [the protocol](@/guide/protocol/_index.md). None of it involves HTML,
JavaScript, GitHub's API or DreamWeave infrastructure.

## St4sh and other indexes

An index crawls sites it knows about, reads `dreamweave.json`, and fetches a manifest when its
`manifest_sha256` changes. It can search, categorize, rank, cache manifests and mirror artifacts. It
should show which origin every manifest came from, and it must not become the only copy of a
project's identity or releases: when the index is gone, the project's own site still says everything.

## Mirrors and caches

A mirror stores artifacts by SHA-256 and serves them to anyone who asks for that digest. It does not
need permission, because it is never trusted: a client already knows the digest from the project's
manifest and rejects anything else. Authors can list mirrors in `mod.toml` ([Distribution](@/guide/distribution.md));
clients can also use caches nobody listed. Nothing about this depends on the transport, so a LAN
cache, an archive service, or peer-to-peer transfer later all fit without a protocol change.

## Existing channels

Nothing here replaces GitHub Releases, Nexus Mods or anywhere else a mod is already published. Those
become sources and integrations in the manifest. Players who never touch a DreamWeave client see an
ordinary mod page with ordinary download buttons.
