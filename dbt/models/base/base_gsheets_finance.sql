-- ------------------------------------------------------------------------------
-- Model: Base_gsheets_finance
-- Description: Base Table Google Sheets Finance
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-10 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here] (Second Test, Please work)
-- ------------------------------------------------------------------------------

SELECT 
    id, 
    stock, 
    CAST(price AS DECIMAL) AS price,  -- DuckDB doesn't have a money type
    strptime(date_time, '%m/%d/%Y %H:%M:%S') AS date_time,
    ROUND((MAX(price) OVER(PARTITION BY stock) - MIN(price) OVER(PARTITION BY stock)), 2) AS price_spread,
    ROUND((LAST(price) OVER(PARTITION BY stock ORDER BY date_time) - FIRST(price) OVER(PARTITION BY stock)), 2) AS relative_price_movement,
    ROUND((LAST(price) OVER(PARTITION BY stock) - FIRST(price) OVER(PARTITION BY stock)), 2) AS abs_price_movement,
    COUNT(id) OVER(PARTITION BY stock) AS Num_Stock_Entries
FROM {{ source("gsheets", "gsheet_finance") }}