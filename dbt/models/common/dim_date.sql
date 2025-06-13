-- ------------------------------------------------------------------------------
-- Model: Dim Date
-- Description: Dimension Table, date information
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-25 | Cam      | Initial creation
-- 2025-06-14 | Cam      | Sqlfluff linting and formatting
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------


WITH RECURSIVE date_series AS (
    SELECT DATE '2000-01-01' AS date_col
    UNION ALL
    SELECT date_col + INTERVAL '1 day'
    FROM date_series
    WHERE date_col + INTERVAL '1 day' < DATE '2030-01-01'
)

SELECT
    date_col
    , EXTRACT(YEAR FROM date_col) AS year_col
    , EXTRACT(MONTH FROM date_col) AS month_col
    , EXTRACT(DAY FROM date_col) AS day_col
    , STRFTIME('%B', date_col) AS month_name  -- Replacing TO_CHAR with strftime
    , STRFTIME('%A', date_col) AS weekday_name  -- Replacing TO_CHAR with strftime
    , EXTRACT(DOW FROM date_col) AS day_of_week
    , COALESCE(EXTRACT(DOW FROM date_col) IN (0, 6), FALSE) AS is_weekend
    , EXTRACT(DOY FROM date_col) AS day_of_year
    , EXTRACT(WEEK FROM date_col) AS week_of_year
    , EXTRACT(QUARTER FROM date_col) AS quarter_col
FROM date_series