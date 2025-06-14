-- ------------------------------------------------------------------------------
-- Model: base_weather
-- Description: Base Table for weather data from API, Can perform bulk loads
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


SELECT
    date::date AS weather_date
    , city
    , temperature_max
    , temperature_min
    , temperature_mean
    , precipitation_sum
    , windspeed_max
    , windgusts_max
    , sunshine_duration
    , location__lat AS latitude
    , location__lng AS longitude
FROM {{ source("weather", "daily_weather") }}