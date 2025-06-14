SELECT
    wf.value AS dob
    , fw.uid AS wanted_id
    , wf._dlt_list_idx AS dob_order
    , wf._dlt_id AS wanted_dob_sk
FROM {{ source("fbi", "wanted__dates_of_birth_used") }} AS wf
LEFT JOIN {{ source("fbi", "wanted") }} AS fw
    ON wf._dlt_root_id = fw._dlt_id
WHERE fw.uid IS NOT null