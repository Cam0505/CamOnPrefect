-- ------------------------------------------------------------------------------
-- Model: Dim_beverage_glass_type
-- Description: Dimension Table, beverage glass type information
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

SELECT
    glass_type
    , glass_type_sk
FROM {{ ref('glass_type_snapshot') }}
GROUP BY glass_type, glass_type_sk
