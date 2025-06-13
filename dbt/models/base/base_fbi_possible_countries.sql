-- Description: Base Table for fbi most wanted - occupations
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-06-14 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here] (Second Test, Please work)
-- ------------------------------------------------------------------------------
SELECT
    wf.value AS country
    , fw.uid AS wanted_id
    , wf._dlt_list_idx AS country_order
    , wf._dlt_id AS wanted_countries_sk
FROM {{ source("fbi", "wanted__possible_countries") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null