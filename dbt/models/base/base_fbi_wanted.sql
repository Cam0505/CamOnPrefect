-- ------------------------------------------------------------------------------
-- Model: Base_FBI_Wanted
-- Description: This model is the base for the FBI wanted persons data.
-- Source: All data in base_fbi_* models is sourced from the FBI Most Wanted API.
-- Plan to add in more countries in the future (Please work)
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
SELECT
    poster_classification
    , hair
    , race_raw
    , url AS urllink
    , uid AS pk
    , remarks
    , eyes_raw
    , race
    , place_of_birth
    , modified
    , hair_raw
    , status
    , publication
    , reward_min
    , sex
    , caution
    , eyes
    , title
    , reward_max
    , person_classification
    , description
    , path_id
    , warning_message
    , reward_text
    , details
    , age_max
    , weight_min
    , weight_max
    , height_min
    , weight AS bodyweight
    , height_max
    , age_min
    , age_range
    , nationality
    , scars_and_marks
    , ncic
    , build
    , complexion
FROM {{ source("fbi", "wanted") }}