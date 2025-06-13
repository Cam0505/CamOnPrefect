-- ------------------------------------------------------------------------------
-- Model: Staging_FBI_Wanted_Lookup
-- Description: Staging model for FBI wanted data lookup
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


SELECT
    hair
    , race_raw
    , urllink
    , remarks
    , eyes_raw
    , race
    , place_of_birth
    , modified
    , hair_raw
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
    , bodyweight
    , height_max
    , age_min
    , age_range
    , nationality
    , scars_and_marks
    , ncic
    , build
    , complexion
    , pk
FROM {{ ref('base_fbi_wanted') }}