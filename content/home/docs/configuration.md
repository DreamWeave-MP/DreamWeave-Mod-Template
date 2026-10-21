+++
title = "Configuration"
description = "Curves, weather factors and what they do."
weight = 10

[extra]
kind = "guide"
+++

Open **Options → Scripts → Candlelight**. Every setting applies on the next cell load.

## Curves

A curve maps the hour of the day to a brightness multiplier. The default street-lantern curve is
off from 07:00 to 19:00 and ramps up over the hour after sunset.

| Setting | Default | Meaning |
|---|---|---|
| Dusk ramp | 60 minutes | How long lights take to reach full brightness after sunset. |
| Storm factor | 0.45 | Brightness multiplier for exposed flames during storms. |
| Rain factor | 0.7 | Brightness multiplier for exposed flames in rain. |

{% callout(kind="warning", title="Do not set factors above 1") %}
A factor above 1 brightens lights past their record value. OpenMW clamps it, but the flicker
curve does not, and you get strobing.
{% end %}

## Interiors

Interiors are never dimmed by weather. That is not configurable, because a roof is not a setting.
