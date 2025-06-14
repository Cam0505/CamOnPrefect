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
  {{ count_grouped_records(source_table='base_rm_character_episode',
        group_cols=["character_dlt_id"],
        count_col='episode_id',
        alias='Num_Episodes'
        ) }}
)

select
    bc.character_id
    , character_name
    , character_status
    , character_species
    , character_gender
    , character_origin
    , character_image
    , character_created
    , bc.character_dlt_id
    , epc.num_episodes
    , case
        when regexp_matches(character_name, '^Rick\b', 'i') then 'Rick'
        when regexp_matches(character_name, '^Morty\b', 'i') then 'Morty'
        when regexp_matches(character_name, '^Summer\b', 'i') then 'Summer'
        when regexp_matches(character_name, '^Beth\b', 'i') then 'Beth'
        when regexp_matches(character_name, '^Jerry\b', 'i') then 'Jerry'
        else 'Other'
    end as character_group
from {{ ref('base_rm_characters') }} as bc
left join episodes_per_character as epc
    on bc.character_dlt_id = epc.character_dlt_id
order by bc.character_id
