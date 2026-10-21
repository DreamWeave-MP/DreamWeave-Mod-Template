+++
title = "DreamWeave Mod Template"
description = "The DreamWeave Mod Template's build tool: validates, builds, releases and records a DreamWeave site's projects, through jess."
date = 2026-10-19

[taxonomies]
tags = ["Jess", "Luau"]

[extra]
sections = ["overview", "releases", "credits"]
+++

The DreamWeave Mod Template's build tool: validates, builds, releases and records a DreamWeave site's projects, through jess.

<!-- more -->

A [Jess](https://github.com/DreamWeave-MP/jess) package, `org.dreamweave.mod-template`. Add it to a `jess.toml` and
`jess workspace sync` pins it from this site:

```toml
[dependencies]
"org.dreamweave.mod-template" = "0.3"
```

Every release below is the package's own archive, with its content digest beside the archive's
SHA-256; `jess.lock` pins the first and checks both.
