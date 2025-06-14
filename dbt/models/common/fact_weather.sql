SELECT
    sw.weather_date
    , sw.city
    , sw.temperature_max
    , sw.temperature_min
    , sw.temperature_range
    , sw.temperature_mean
    , sw.precipitation_sum
    , sw.precipitation_fortnightly_anomaly
    , sw.windspeed_max
    , sw.windgusts_max
    , sw.sunshine_duration
    , sw.mean_temp_fortnightly_anomaly
    , sw.mean_temp_fortnightly_avg
    , sw.mean_temp_moving_avg
    , sg.city_sk
FROM {{ ref('staging_weather') }} AS sw
LEFT JOIN {{ ref('staging_geo') }} AS sg
    ON sw.city = sg.city