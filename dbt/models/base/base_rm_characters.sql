-- ------------------------------------------------------------------------------
-- Model: Base_rm_characters
-- Description: Base Table for ricky and morty characters from API
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
SELECT
    id AS character_id
    , name AS character_name
    , status AS character_status
    , species AS character_species
    , gender AS character_gender
    , origin__name AS character_origin
    , location__name AS character_first_location
    , location__url AS character_first_location_url
    , image AS character_image
    , url AS character_url
    , _dlt_id AS character_dlt_id
    , created AT TIME ZONE 'UTC' AT TIME ZONE 'Australia/Melbourne' AS character_created
FROM {{ source("rick_and_morty", "character") }}