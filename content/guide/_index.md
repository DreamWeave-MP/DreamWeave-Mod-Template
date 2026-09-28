+++
title = "Guide"
description = "Make a mod page, publish releases, and put a mod on the DreamWeave network."
sort_by = "weight"
template = "docs/section.html"
page_template = "docs/page.html"

[extra]
docs_root = true
docs_project_name = "Mod Template"
docs_short_title = "Mod Template guide"
docs_sidebar_label = "Guide"
docs_repository_url = "https://github.com/DreamWeave-MP/DreamWeave-Mod-Template"
+++

The DreamWeave Mod Template turns a repository into three things at once: a mod page people can
read, archives people can install, and a set of static files that tools can read without
scraping either. You write two files per mod. Everything else is generated, checked, and
published by the workflow.

{{ schematic(data_path="data/schematics/publishing.json") }}

If this is your first mod on the template, read [Start here](@/guide/start-here.md) and stop
when your page is up. Come back for [Releases](@/guide/releases.md) when you have something to
release. The [protocol](@/guide/protocol/_index.md) pages are for people writing tools that read
what the template publishes; you do not need them to publish a mod.
