local world = require 'openmw.world'

local pausedUntil = 0

return {
  eventHandlers = {
    CandlelightRefresh = function(data)
      if world.getGameTime() < pausedUntil then return end
      for _, player in ipairs(world.players) do
        player:sendEvent('CandlelightChanged', { light = player, brightness = data.factor })
      end
    end,
    CandlelightPause = function(data) pausedUntil = world.getGameTime() + data.seconds end,
  },
}
