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


SELECT bw.wanted_id, 
ba.wanted_aliases_sk
,bdob.wanted_DoB_sk
,bfo.wanted_field_offices_sk
,bff.wanted_files_sk
,bfi.wanted_images_sk
,bfl.wanted_languages_sk
,bfo2.wanted_occupations_sk
,bfpc.wanted_countries_sk
,bfps.wanted_states_sk
,bfs.wanted_subject_sk
from {{ref('base_fbi_wanted')}}  bw
left join {{ref('base_fbi_aliases')}} as ba
on bw.wanted_id = ba.wanted_id
left join {{ref('base_fbi_dates_of_birth_used')}} as bdob
on bw.wanted_id = bdob.wanted_id
left join {{ref('base_fbi_field_offices')}} as bfo
on bw.wanted_id = bfo.wanted_id
left join {{ref('base_fbi_files')}} as bff
on bw.wanted_id = bff.wanted_id
left join {{ref('base_fbi_images')}} as bfi
on bw.wanted_id = bfi.wanted_id
left join {{ref('base_fbi_languages')}} as bfl
on bw.wanted_id = bfl.wanted_id
left join {{ref('base_fbi_occupations')}} as bfo2
on bw.wanted_id = bfo2.wanted_id
left join {{ref('base_fbi_possible_countries')}} as bfpc
on bw.wanted_id = bfpc.wanted_id
left join {{ref('base_fbi_possible_states')}} as bfps
on bw.wanted_id = bfps.wanted_id
left join {{ref('base_fbi_subject')}} as bfs
on bw.wanted_id = bfs.wanted_id

