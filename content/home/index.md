+++
title = "Candlelight"
description = "Lights that know what time it is. Candles gutter, lanterns dim in storms, and every flame in Vvardenfell follows the hour."
date = 2026-09-14

[taxonomies]
tags = ["Lighting", "Lua", "OpenMW"]

[extra]
# Which landing-page sections to show, in order. Omit to show everything that has data.
# overview, media, install, compatibility, components, releases, credits
sections = ["overview", "media", "install", "compatibility", "components", "releases", "credits"]
+++

Vanilla lights are painted on. They burn the same at noon and midnight, in sunshine and in an
ash storm, and a candle in a drafty Balmora hallway is exactly as steady as the sun.

Candlelight gives every light a schedule and a temper. Street lanterns come on at dusk. Exposed
flames dim and flicker when the weather turns, and recover when it clears. Interiors stay warm.
Magic lights ignore all of it, because they are magic.

<!-- more -->

{% features() %}
- **Time of day.** Every vanilla light follows a curve from dusk to dawn instead of a constant.
- **Weather.** Rain, storms and ash dim exposed flames; interiors are unaffected.
- **No save bloat.** Nothing is written to saves. Uninstalling is deleting the files.
- **Scheduled by [Tallow](@/simplified/index.md).** The same library other mods can use.
{% end %}

## How it works

Candlelight reads light records when their cell loads and asks Tallow to wake it at the next
interesting hour. Between wake-ups it does nothing, which is the cheapest thing a script can do.

{% callout(kind="note", title="This page is an example") %}
Candlelight is the DreamWeave Mod Template's complete example project. Every section on this
page is generated from `content/home/mod.toml`. The [guide](@/guide/_index.md) explains how to
make your own.
{% end %}
