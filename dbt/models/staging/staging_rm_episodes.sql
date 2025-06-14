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
    {{ count_grouped_records(source_table='base_rm_episode_character',
        group_cols=["episode_dlt_id"],
        count_col='character_id',
        alias='Num_Characters'
        ) }}
)

select
    episode_id
    , episode_name
    , episode_air_date
    , episode
    , be.episode_dlt_id
    , cie.num_characters
    , case
        when
            episode_name ilike '%ricklantis%'
            or episode_name ilike '%rickmurai%'
            or episode_name ilike '%pickle rick%'
            or episode_name ilike '%rickternal%'
            then 'Rick-Focused'
        when episode_name ilike '%morty%' or episode_name ilike '%mort%' then 'Morty-Focused'
        when
            episode_name ilike '%interdimensional cable%' or episode_name ilike '%rixty minutes%'
            then 'Interdimensional Cable'
        when episode_name ilike '%rick%' and episode_name ilike '%mort%' then 'Rick & Morty Duo'
        when
            episode_name ilike '%park%'
            or episode_name ilike '%shaym%'
            or episode_name ilike '%recall%'
            or episode_name ilike '%galactica%'
            or episode_name ilike '%jack%'
            or episode_name ilike '%tomorty%'
            or episode_name ilike '%spotless%'
            then 'Pop Culture Reference'
        else 'Other'
    end as episode_group
    , CAST(SUBSTR(episode, 2, 2) as INTEGER) as season_num
    , CAST(SUBSTR(episode, 5, 2) as INTEGER) as episode_num
from {{ ref('base_rm_episodes') }} as be
left join characters_in_episodes as cie
    on be.episode_dlt_id = cie.episode_dlt_id