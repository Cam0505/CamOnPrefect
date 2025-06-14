-- ------------------------------------------------------------------------------
-- Model: Staging_rm_locations
-- Description: Staging model for Rick and Morty locations
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

with resident_per_location as (
	{{ count_grouped_records(source_table='base_rm_location_residents',
        group_cols=["location_dlt_id"],
        count_col='character_id',
        alias='Num_Characters'
        ) }}
)

select
    bl.location_id
    , location_name
    , location_type
    , location_dimension
    , location_created
    , bl.location_dlt_id
    , rpl.num_characters
    , case
        when
            LOWER(location_type) in (
                'planet', 'asteroid', 'quasar', 'mount', 'elemental rings', 'dwarf planet (celestial dwarf)'
            )
            then 'Celestial Body'
        when
            LOWER(location_type) in (
                'teenyverse'
                , 'miniverse'
                , 'microverse'
                , 'diegesis'
                , 'non-diegetic alternative reality'
                , 'box'
                , 'machine'
            )
            then 'Artificial World'
        when
            LOWER(location_type) in ('game', 'dream', 'memory', 'tv', 'consciousness', 'nightmare', 'fantasy town')
            then 'Virtual/Simulated'
        when
            LOWER(location_type) in (
                'space station'
                , 'resort'
                , 'spa'
                , 'base'
                , 'police department'
                , 'customs'
                , 'daycare'
                , 'spacecraft'
                , 'arcade'
            )
            then 'Location Type'
        when
            LOWER(location_type) in ('hell', 'reality', 'liquid', 'death star', 'artificially generated world')
            then 'Abstract Realm'
        when LOWER(location_type) in ('country', 'cluster', 'menagerie', 'convention') then 'Social Structure'
        when LOWER(location_type) in ('quadrant') then 'Quadrant/Zone'
        else 'Unknown'
    end as location_categories
    , case
        when location_dimension ilike '%unknown%' then 'Unclassified'
        when LOWER(location_dimension) like 'dimension c%' then 'Standard Format'
        when location_dimension ilike '%Fascist%' then 'Fascist Variant'
        when
            location_dimension ilike '%Magic%'
            or location_dimension ilike '%Fantasy%'
            or location_dimension ilike '%Post-Apocalyptic%'
            or location_dimension ilike '%Merged%'
            or location_dimension ilike '%Evil Rick%'
            or location_dimension ilike '%Testicle%'
            or location_dimension ilike '%Eric Stoltz%'
            or location_dimension ilike '%Wasp%'
            or location_dimension ilike '%Phone%'
            or location_dimension ilike '%Spider%'
            or location_dimension ilike '%Pizza%'
            or location_dimension ilike '%Chair%'
            or location_dimension ilike '%Tusk%'
            or location_dimension ilike '%Cromulon%' then 'Thematic'
        when location_dimension ilike '%Replacement%' or location_dimension ilike '%Cronenberg%' then 'Canonical Named'
        else 'Other'
    end as dimension_group
from {{ ref('base_rm_locations') }} as bl
left join resident_per_location as rpl
    on bl.location_dlt_id = rpl.location_dlt_id