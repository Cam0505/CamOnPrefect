-- ------------------------------------------------------------------------------
-- Model: Dim Fact Beverage Consumption
-- Description: Fact Table, beverage consumption information
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
SELECT
    beverage_id
    , beverage_name
    , glass_type_sk
    , beverage_category_sk
    , beverage_type_sk
    , alcoholic_type_sk
    , beverage_type
    , alcoholic_type
    , beverage_instructions
    , beverage_url
    , glass_type
    , date_melbourne
    , str_ingredient1
    , str_ingredient2
    , str_ingredient3
    , str_ingredient4
    , str_ingredient5
    , str_ingredient6
    , str_ingredient7
    , str_ingredient8
FROM {{ ref('staging_beverage_consumption') }}