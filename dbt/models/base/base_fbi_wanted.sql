-- ------------------------------------------------------------------------------
-- Model: Base_FBI_Wanted
-- Description: This model is the base for the FBI wanted persons data.
-- Plan to add in more countries in the future (Please work)
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


SELECT poster_classification, hair, race_raw, url as urllink, uid as pk, remarks, eyes_raw, race, place_of_birth, modified, hair_raw, 
status, publication, reward_min, sex, caution, eyes, title, reward_max, person_classification, 
description, path_id, "_dlt_id" as wanted_id, warning_message, reward_text, details, age_max, weight_min, 
weight_max, height_min, weight as bodyweight, height_max, age_min, age_range, nationality, scars_and_marks, ncic, build, complexion
from {{ source("fbi", "wanted") }}