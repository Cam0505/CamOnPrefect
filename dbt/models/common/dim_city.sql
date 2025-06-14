-- ------------------------------------------------------------------------------
-- Model: Dim City
-- Description: Dimension Table, city information
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
select
    city
    , latitude
    , longitude
    , region
    , city_sk
    , country_sk
from {{ ref('staging_geo') }}
group by city, latitude, longitude, region, city_sk, country_sk