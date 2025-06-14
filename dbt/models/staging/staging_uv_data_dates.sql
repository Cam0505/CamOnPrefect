{{
  config(
    materialized = "view"
  )
}}


SELECT date_col
FROM {{ ref('dim_date') }} AS t
WHERE
    date_col <= (current_date - 1)
    AND NOT EXISTS (
        SELECT 1
        FROM {{ ref('base_uv') }} AS o
        WHERE o.uv_date = t.date_col
    )
ORDER BY date_col DESC
LIMIT 6