


SELECT value as wanted_subject, "_dlt_root_id" as wanted_id, "_dlt_list_idx" as subject_order
, "_dlt_id" as wanted_subject_sk
from {{ source("fbi", "wanted__subjects") }} as wf