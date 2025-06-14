-- Description: Base Table for fbi most wanted - occupations
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-06-14 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here] (Second Test, Please work)
-- ------------------------------------------------------------------------------
SELECT
    wf.value AS occupations
    , fw.uid AS wanted_id
    , wf._dlt_list_idx AS occupations_order
    , wf._dlt_id AS wanted_occupations_sk
FROM {{ source("fbi", "wanted__occupations") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null