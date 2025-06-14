-- ------------------------------------------------------------------------------
-- Model: Staging_rm_episodes
-- Description: Staging model for Rick and Morty episodes
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

with characters_in_episodes as (
    {{ count_grouped_records(source_table='base_rm_episode_character'
        ,group_cols=["episode_dlt_id"]
        ,count_col='character_id'
        ,alias='Num_Characters'
        ) }}
)

select
    be.episode_id
    , be.episode_name
    , be.episode_air_date
    , be.episode
    , be.episode_dlt_id
    , cie.num_characters
    , case
        when
            be.episode_name ilike '%ricklantis%'
            or be.episode_name ilike '%rickmurai%'
            or be.episode_name ilike '%pickle rick%'
            or be.episode_name ilike '%rickternal%'
            then 'Rick-Focused'
        when be.episode_name ilike '%morty%' or be.episode_name ilike '%mort%' then 'Morty-Focused'
        when
            be.episode_name ilike '%interdimensional cable%' or be.episode_name ilike '%rixty minutes%'
            then 'Interdimensional Cable'
        when be.episode_name ilike '%rick%' and be.episode_name ilike '%mort%' then 'Rick & Morty Duo'
        when
            be.episode_name ilike '%park%'
            or be.episode_name ilike '%shaym%'
            or be.episode_name ilike '%recall%'
            or be.episode_name ilike '%galactica%'
            or be.episode_name ilike '%jack%'
            or be.episode_name ilike '%tomorty%'
            or be.episode_name ilike '%spotless%'
            then 'Pop Culture Reference'
        else 'Other'
    end as episode_group
    , CAST(SUBSTR(be.episode, 2, 2) as INTEGER) as season_num
    , CAST(SUBSTR(be.episode, 5, 2) as INTEGER) as episode_num
from {{ ref('base_rm_episodes') }} as be
left join characters_in_episodes as cie
    on be.episode_dlt_id = cie.episode_dlt_id