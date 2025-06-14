SELECT
    bil.ingredient
    , bil.beverage_id
    , bil.beverage_name
    , bil2.ingredient AS ingredient2
    , bil3.ingredient AS ingredient3
    , bil4.ingredient AS ingredient4
    , bil5.ingredient AS ingredient5
    , bil6.ingredient AS ingredient6
    , bil7.ingredient AS ingredient7
FROM {{ ref('base_beverage_ingredients_lookup') }} AS bil
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil2
    ON bil.beverage_id = bil2.beverage_id AND bil.ingredient != bil2.ingredient
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil3
    ON bil.beverage_id = bil3.beverage_id AND bil3.ingredient NOT IN (bil2.ingredient, bil.ingredient)
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil4
    ON bil.beverage_id = bil4.beverage_id AND bil4.ingredient NOT IN (bil3.ingredient, bil2.ingredient, bil.ingredient)
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil5
    ON
        bil.beverage_id = bil5.beverage_id
        AND bil5.ingredient NOT IN (bil4.ingredient, bil3.ingredient, bil2.ingredient, bil.ingredient)
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil6
    ON
        bil.beverage_id = bil6.beverage_id
        AND bil6.ingredient NOT IN (bil5.ingredient, bil4.ingredient, bil3.ingredient, bil2.ingredient, bil.ingredient)
LEFT JOIN {{ ref('base_beverage_ingredients_lookup') }} AS bil7
    ON
        bil.beverage_id = bil7.beverage_id
        AND bil7.ingredient NOT IN (
            bil6.ingredient, bil5.ingredient, bil4.ingredient, bil3.ingredient, bil2.ingredient, bil.ingredient
        )
