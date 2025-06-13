-- ------------------------------------------------------------------------------
-- Model: Staging_FBI_Wanted_Fact
-- Description: Staging model for FBI wanted data
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


SELECT
    bw.pk AS wanted_id
    , ba.wanted_aliases_sk
    , bdob.wanted_dob_sk
    , bfo.wanted_field_offices_sk
    , bff.wanted_files_sk
    , bfi.wanted_images_sk
    , bfl.wanted_languages_sk
    , bfo2.wanted_occupations_sk
    , bfpc.wanted_countries_sk
    , bfps.wanted_states_sk
    , bfs.wanted_subject_sk
FROM {{ ref('base_fbi_wanted') }} AS bw
LEFT JOIN {{ ref('base_fbi_aliases') }} AS ba
    ON bw.pk = ba.wanted_id
LEFT JOIN {{ ref('base_fbi_dates_of_birth_used') }} AS bdob
    ON bw.pk = bdob.wanted_id
LEFT JOIN {{ ref('base_fbi_field_offices') }} AS bfo
    ON bw.pk = bfo.wanted_id
LEFT JOIN {{ ref('base_fbi_files') }} AS bff
    ON bw.pk = bff.wanted_id
LEFT JOIN {{ ref('base_fbi_images') }} AS bfi
    ON bw.pk = bfi.wanted_id
LEFT JOIN {{ ref('base_fbi_languages') }} AS bfl
    ON bw.pk = bfl.wanted_id
LEFT JOIN {{ ref('base_fbi_occupations') }} AS bfo2
    ON bw.pk = bfo2.wanted_id
LEFT JOIN {{ ref('base_fbi_possible_countries') }} AS bfpc
    ON bw.pk = bfpc.wanted_id
LEFT JOIN {{ ref('base_fbi_possible_states') }} AS bfps
    ON bw.pk = bfps.wanted_id
LEFT JOIN {{ ref('base_fbi_subject') }} AS bfs
    ON bw.pk = bfs.wanted_id

