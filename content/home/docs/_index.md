+++
title = "Candlelight documentation"
description = "Configuration, events and the curve format."
sort_by = "weight"
template = "docs/section.html"
page_template = "docs/page.html"

[extra]
docs_root = true
docs_project_name = "Candlelight"
docs_short_title = "Candlelight docs"
docs_project_path = "@/home/index.md"
docs_sidebar_label = "Documentation"
+++

Candlelight has two moving parts: a player script that watches the clock and the weather, and a
global script that owns light records. Both talk through events, so another mod can listen in.

Start with [configuration](@/home/docs/configuration.md) if you want different curves, or
[events](@/home/docs/events.md) if you are writing a mod that reacts to lights changing.
