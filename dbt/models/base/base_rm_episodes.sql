-- ------------------------------------------------------------------------------
-- Model: base_rm_episode
-- Description: Base Table for ricky and morty episodes from API
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
SELECT
    id AS episode_id
    , name AS episode_name
    , episode
    , url AS episode_url
    , _dlt_id AS episode_dlt_id
    , STRPTIME(air_date, '%B %d, %Y') AS episode_air_date
    , created AT TIME ZONE 'UTC' AT TIME ZONE 'Australia/Melbourne' AS episode_created
FROM {{ source("rick_and_morty", "episode") }}