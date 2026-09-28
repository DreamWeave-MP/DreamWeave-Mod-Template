local core = require 'openmw.core'
local time = require 'openmw_aux.time'

local DUSK_HOUR = 19
local DAWN_HOUR = 6

local subscribers = {}
local lastHour = -1

local function hourOf(moment)
  if moment == 'dusk' then return DUSK_HOUR end
  if moment == 'dawn' then return DAWN_HOUR end
  assert(
    type(moment) == 'number' and moment >= 0 and moment <= 23,
    'Tallow: moment must be dusk, dawn or an hour from 0 to 23'
  )
  return moment
end

local function every(moment, callback)
  local hour = hourOf(moment)
  subscribers[hour] = subscribers[hour] or {}
  table.insert(subscribers[hour], callback)
end

time.runRepeatedly(function()
  local hour = math.floor(core.getGameTime() / time.hour) % 24
  if hour == lastHour then return end
  lastHour = hour
  for _, callback in ipairs(subscribers[hour] or {}) do
    callback()
  end
end, time.minute * 5, { type = time.GameTime })

return {
  interfaceName = 'Tallow',
  interface = { version = 1, every = every },
}
