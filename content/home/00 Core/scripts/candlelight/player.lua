local I = require 'openmw.interfaces'
local core = require 'openmw.core'

local stormFactor = 0.45
local rainFactor = 0.7

local function weatherFactor()
  local weather = core.weather.getCurrent()
  if not weather then return 1 end
  if weather.name == 'Thunderstorm' or weather.name == 'Ashstorm' then return stormFactor end
  if weather.name == 'Rain' then return rainFactor end
  return 1
end

return {
  engineHandlers = {
    onActive = function()
      I.Tallow.every(
        'dusk',
        function() core.sendGlobalEvent('CandlelightRefresh', { factor = weatherFactor() }) end
      )
    end,
  },
}
