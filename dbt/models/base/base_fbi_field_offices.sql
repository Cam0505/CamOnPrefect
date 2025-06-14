SELECT
    value AS field_office
    , fw.uid AS wanted_id
    , _dlt_list_idx AS field_office_order
    , wf._dlt_id AS wanted_field_offices_sk
FROM {{ source("fbi", "wanted__field_offices") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null