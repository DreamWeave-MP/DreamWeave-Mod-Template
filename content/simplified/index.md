+++
title = "Tallow"
description = "A tiny OpenMW Lua library that wakes your script at dusk, at dawn, or on the hour."

[taxonomies]
tags = ["Library", "Lua", "OpenMW"]
+++

Tallow schedules callbacks against the game clock, so a script that cares about the time of day
can sleep until the time it cares about instead of checking every frame.

<!-- more -->

```lua
local I = require 'openmw.interfaces'

I.Tallow.every('dusk', function()
  print('The lamps are lit.')
end)
```

`every(moment, callback)` accepts `'dusk'`, `'dawn'` or an hour from `0` to `23`. Callbacks run
once per occurrence, in the order they were registered.

{% callout(kind="note", title="This page is an example") %}
Tallow is the template's minimal example. Its whole `mod.toml` is an id, a slug, a runtime, one
content file and one release. [Candlelight](@/home/index.md) depends on it.
{% end %}
