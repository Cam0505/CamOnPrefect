-- ------------------------------------------------------------------------------
-- Model: base_rm_locations
-- Description: Base Table for ricky and morty locations from API
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

SELECT
    id AS location_id
    , name AS location_name
    , type AS location_type
    , dimension AS location_dimension
    , url AS location_url
    ,{{ convert_to_timezone(column_name='created') }} AS location_created
    , _dlt_id AS location_dlt_id
FROM {{ source("rick_and_morty", "location") }}