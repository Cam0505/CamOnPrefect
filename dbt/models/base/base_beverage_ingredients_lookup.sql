-- ------------------------------------------------------------------------------
-- Model: Base_beverage_ingredients_lookup
-- Description: Base Table for Beverage Ingredients
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
Select
    it.source_ingredient As ingredient
    , it.id_drink As beverage_id
    , it.str_drink As beverage_name
From {{ source("beverages", "ingredients_table") }} As it
Where it.id_drink Is Not null
