-- Description: Base Table for fbi most wanted - images
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-06-14 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here] (Second Test, Please work)
-- ------------------------------------------------------------------------------
SELECT
    wf.large AS large_image
    , wf.thumb AS thumb_image
    , wf.original AS original_image
    , fw.uid AS wanted_id
    , wf._dlt_list_idx AS image_order
    , wf._dlt_id AS wanted_images_sk
    , wf.caption
FROM {{ source("fbi", "wanted__images") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null