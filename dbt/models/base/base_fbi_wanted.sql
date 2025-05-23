


SELECT poster_classification, hair, race_raw, url as urllink, uid as pk, remarks, eyes_raw, race, place_of_birth, modified, hair_raw, 
status, publication, reward_min, sex, caution, eyes, title, reward_max, person_classification, 
description, path_id, "_dlt_id" as wanted_id, warning_message, reward_text, details, age_max, weight_min, 
weight_max, height_min, weight as bodyweight, height_max, age_min, age_range, nationality, scars_and_marks, ncic, build, complexion
from {{ source("fbi", "wanted") }}