-- ------------------------------------------------------------------------------
-- Model: Dim Country
-- Description: Dimension Table, country information (Test)
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-22 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
select
    country_code
    , country
    , country_sk
from {{ ref('staging_geo') }}
group by country_code, country, country_sk