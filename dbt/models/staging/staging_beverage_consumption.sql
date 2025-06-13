-- ------------------------------------------------------------------------------
-- Model: Staging_Beverage_Consumption
-- Description: Fact Table data, consumption events generated from API 
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

select
    bc.id_drink as beverage_id
    , bc.str_drink as beverage_name
    , bcl.beverage_category_sk
    , bc.str_glass as glass_type
    , bcl.beverage_type_sk
    , bcl.beverage_type
    , bcl.alcoholic_type_sk
    , bcl.alcoholic_type
    , bc.str_category
    , bc.str_alcoholic
    , bgl.glass_type_sk
    , bc.str_instructions as beverage_instructions
    , bc.str_drink_thumb as beverage_url
    , bc.date_melbourne
    , bc.str_ingredient1
    , bc.str_ingredient2
    , bc.str_ingredient3
    , bc.str_ingredient4
    , bc.str_ingredient5
    , bc.str_ingredient6
    , bc.str_ingredient7
    , bc.str_ingredient8
-- from public_base.base_beverage_consumption as bc
from {{ ref('base_beverage_consumption') }} as bc
-- left join public_base.base_beverage_glass_lookup as bgl
left join {{ ref('glass_type_snapshot') }} as bgl
    on bc.id_drink = bgl.beverage_id and bgl.dbt_valid_to is null
left join {{ ref('staging_beverage_lookup') }} as bcl
    on bc.id_drink = bcl.beverage_id
