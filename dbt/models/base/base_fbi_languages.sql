SELECT
    value AS wanted_language
    , fw.uid AS wanted_id
    , _dlt_list_idx AS language_order
    , wf._dlt_id AS wanted_languages_sk
FROM {{ source("fbi", "wanted__languages") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null