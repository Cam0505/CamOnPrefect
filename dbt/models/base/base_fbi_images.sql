SELECT
    large AS large_image
    , thumb AS thumb_image
    , original AS original_image
    , fw.uid AS wanted_id
    , _dlt_list_idx AS image_order
    , wf._dlt_id AS wanted_images_sk
    , caption
FROM {{ source("fbi", "wanted__images") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null