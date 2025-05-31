SELECT *
FROM {{ ref('dim_beverage_ingredient_hierarchy') }}
WHERE
  (
    SELECT COUNT(*) 
    FROM (
      SELECT ingredient AS val UNION ALL
      SELECT ingredient2 UNION ALL
      SELECT ingredient3 UNION ALL
      SELECT ingredient4 UNION ALL
      SELECT ingredient5 UNION ALL
      SELECT ingredient6 UNION ALL
      SELECT ingredient7
    )
    WHERE val IS NOT NULL
  ) != (
    SELECT COUNT(DISTINCT val)
    FROM (
      SELECT ingredient AS val UNION ALL
      SELECT ingredient2 UNION ALL
      SELECT ingredient3 UNION ALL
      SELECT ingredient4 UNION ALL
      SELECT ingredient5 UNION ALL
      SELECT ingredient6 UNION ALL
      SELECT ingredient7
    )
    WHERE val IS NOT NULL
  )