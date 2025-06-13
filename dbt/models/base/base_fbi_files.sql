-- Description: Base Table for fbi most wanted - files
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-06-14 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here] (Second Test, Please work)
-- ------------------------------------------------------------------------------
SELECT
    wf.url AS url_link
    , wf.name AS language_name
    , fw.uid AS wanted_id
    , wf._dlt_list_idx AS file_order
    , wf._dlt_id AS wanted_files_sk
FROM {{ source("fbi", "wanted__files") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT NULL