-- ------------------------------------------------------------------------------
-- Model: Dim_beverage_ingredient_jointable
-- Description: Join table for beverage ingredients
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
SELECT DISTINCT id_drink AS beverage_id
FROM {{ source("beverages", "ingredients_table") }}
WHERE id_drink IS NOT null