{{
  config(
    materialized = "view"
  )
}}

with all_dates as (
    select date_col
    from {{ ref('dim_date') }}
    where date_col <= (current_date - 1)
)

, cities as (
    select cities.city
    from (
        values
        ('Sydney')
        , ('Melbourne')
        , ('Brisbane')
        , ('Perth')
        , ('Adelaide')
        , ('Canberra')
        , ('Hobart')
        , ('Darwin')
    ) as cities (city)
)

, all_combinations as (
    select
        d.date_col
        , c.city
    from all_dates as d
    cross join cities as c
)

, missing as (
    select
        ac.date_col
        , ac.city
    from all_combinations as ac
    left join {{ ref('base_uv') }} as bu
        on
            ac.date_col = bu.uv_date
            and ac.city = bu.city
    where bu.city is null
)

select
    date_col
    , city
from missing
order by date_col desc, city asc
limit 50