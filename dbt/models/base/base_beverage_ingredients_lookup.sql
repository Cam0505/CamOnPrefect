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
Select it.source_ingredient as Ingredient,
it.id_drink as beverage_id,
it.str_drink as Beverage_Name
from {{ source("beverages", "ingredients_table") }}  as it
where it.id_drink is not null
