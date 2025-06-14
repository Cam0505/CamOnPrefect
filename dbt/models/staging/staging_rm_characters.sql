-- ------------------------------------------------------------------------------
-- Model: Staging_rm_characters
-- Description: Staging model for characters data
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
with episodes_per_character as (
  {{ count_grouped_records(source_table='base_rm_character_episode'
        ,group_cols=["character_dlt_id"]
        ,count_col='episode_id'
        ,alias='Num_Episodes'
        ) }}
)

select
    bc.character_id
    , bc.character_name
    , bc.character_status
    , bc.character_species
    , bc.character_gender
    , bc.character_origin
    , bc.character_image
    , bc.character_created
    , bc.character_dlt_id
    , epc.num_episodes
    , case
        when regexp_matches(bc.character_name, '^Rick\b', 'i') then 'Rick'
        when regexp_matches(bc.character_name, '^Morty\b', 'i') then 'Morty'
        when regexp_matches(bc.character_name, '^Summer\b', 'i') then 'Summer'
        when regexp_matches(bc.character_name, '^Beth\b', 'i') then 'Beth'
        when regexp_matches(bc.character_name, '^Jerry\b', 'i') then 'Jerry'
        else 'Other'
    end as character_group
from {{ ref('base_rm_characters') }} as bc
left join episodes_per_character as epc
    on bc.character_dlt_id = epc.character_dlt_id
order by bc.character_id
