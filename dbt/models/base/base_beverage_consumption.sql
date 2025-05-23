-- ------------------------------------------------------------------------------
-- Model: Base_beverage_consumption
-- Description: Base Table for Beverage Consumption
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


SELECT id_drink, str_drink, str_category, str_alcoholic, str_glass, str_instructions, 
str_drink_thumb, (date_modified AT TIME ZONE 'Australia/Melbourne')::date AS date_melbourne,
str_ingredient1, str_ingredient2, 
str_ingredient3, str_ingredient4, str_ingredient5, str_ingredient6, 
str_ingredient7, str_ingredient8
	-- FROM cocktail_data.consumption
    from {{ source("beverages", "consumption") }} 