-- ------------------------------------------------------------------------------
-- Model: Staging_geo
-- Description: Staging model for geographic data
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
select
    city_id
    , city
    , latitude
    , longitude
    , country_code
    , country
    , region
    , {{ dbt_utils.generate_surrogate_key(["city", "country"]) }} as city_sk
    , {{ dbt_utils.generate_surrogate_key(["country"]) }} as country_sk
from {{ ref('base_geo') }}