+++
title = "Protocol"
description = "The DreamWeave mod distribution protocol, schema_version 2, for people implementing clients, indexes and mirrors."
sort_by = "weight"
weight = 200
template = "docs/section.html"
page_template = "docs/page.html"

[extra]
kind = "reference"
+++

This is the specification of what a DreamWeave-compatible site publishes and how a client reads it.
It is complete enough to implement a client, an index or a mirror without reading the template's
source; where the template and this text disagree, file a bug against whichever is wrong.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY mean what [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
says they mean.

## The model

A **project** is a mod, library or tool with a permanent **id**, a UUID chosen by its author. A
project has **releases**, each identified by a **version** within that project. A release has
**artifacts**, files identified by their SHA-256 digest and available from one or more **sources**.
A project's **manifest** says all of this; a site's **index** lists the manifests the site publishes.

Project identity, release identity and artifact identity are three different things:

| Thing | Identified by | Not by |
|---|---|---|
| Project | `project.id` | name, slug, URL, host, repository, Nexus id, signing key |
| Release | `(project.id, version)` under the project's versioning scheme | tag name, date, file name |
| Artifact | `digests.sha256` | file name, URL, source |

## Documents

| Document | Where | Schema |
|---|---|---|
| Site index | `<site>/dreamweave.json` | [dreamweave-index-2.schema.json](../../schemas/dreamweave-index-2.schema.json) |
| Project manifest | wherever the index or a page's `<link>` says; conventionally `<site>/dreamweave/projects/<id>.json` | [modManifest-2.schema.json](../../schemas/modManifest-2.schema.json) |
| Release payload | `dreamweave.release.json` at an archive's root | [dreamweave-release-payload-2.schema.json](../../schemas/dreamweave-release-payload-2.schema.json) |

All three are UTF-8 JSON with `"schema_version": "2"` and a `document` field naming which one it is.
A client MUST check both before reading anything else.

The pages in this section cover [discovery](@/guide/protocol/discovery.md), the
[manifest](@/guide/protocol/manifest.md), [versions and releases](@/guide/protocol/versions.md),
[artifacts](@/guide/protocol/artifacts.md), [installation](@/guide/protocol/installation.md), and
[extensions and evolution](@/guide/protocol/evolution.md).

## What the protocol does not do

It does not name a central registry, allocate ids, rank projects, moderate content, run install
scripts, or decide whom to trust. Those belong to clients, indexes and people. A conforming site is
a set of static files; a conforming client needs nothing but HTTP GET.
