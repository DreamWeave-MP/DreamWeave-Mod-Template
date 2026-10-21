+++
title = "Events"
description = "Events Candlelight sends and accepts."
weight = 20

[extra]
kind = "api"
+++

{{ api_signature(value="CandlelightChanged { light: GameObject, brightness: number }") }}

Sent to the player script whenever Candlelight changes a light's brightness. `brightness` is the
multiplier applied to the record's radius and color, from `0` to `1`.

```lua
local core = require 'openmw.core'

return {
  eventHandlers = {
    CandlelightChanged = function(data)
      if data.brightness == 0 then
        print(data.light.recordId .. ' went out')
      end
    end,
  },
}
```

{{ api_signature(value="CandlelightPause { seconds: number }") }}

Accepted by the global script. Freezes every light for `seconds` of game time, for cutscenes that
want the lighting to hold still.
