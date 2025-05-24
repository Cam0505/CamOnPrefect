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
,bw.pk
from {{ref('base_fbi_wanted')}}  bw
left join {{ref('base_fbi_aliases')}} as ba
on bw.pk = ba.wanted_id
left join {{ref('base_fbi_dates_of_birth_used')}} as bdob
on bw.pk  = bdob.wanted_id
left join {{ref('base_fbi_field_offices')}} as bfo
on bw.pk  = bfo.wanted_id
left join {{ref('base_fbi_files')}} as bff
on bw.pk  = bff.wanted_id
left join {{ref('base_fbi_images')}} as bfi
on bw.pk  = bfi.wanted_id
left join {{ref('base_fbi_languages')}} as bfl
on bw.pk  = bfl.wanted_id
left join {{ref('base_fbi_occupations')}} as bfo2
on bw.pk  = bfo2.wanted_id
left join {{ref('base_fbi_possible_countries')}} as bfpc
on bw.pk  = bfpc.wanted_id
left join {{ref('base_fbi_possible_states')}} as bfps
on bw.pk  = bfps.wanted_id
left join {{ref('base_fbi_subject')}} as bfs
on bw.pk  = bfs.wanted_id

