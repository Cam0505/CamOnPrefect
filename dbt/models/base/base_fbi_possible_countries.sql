SELECT
    value AS country
    , fw.uid AS wanted_id
    , _dlt_list_idx AS country_order
    , wf._dlt_id AS wanted_countries_sk
FROM {{ source("fbi", "wanted__possible_countries") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null