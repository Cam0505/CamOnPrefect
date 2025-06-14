-- ------------------------------------------------------------------------------
-- Model: Base_uv
-- Description: uv data from global UV api
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-25 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

SELECT
    uv_time::date AS uv_date
    , uv
    , uv_max
    , uv_time
    , ozone
    , city
    , location__lat
    , location__lng
FROM {{ source("uv", "uv_index") }}
