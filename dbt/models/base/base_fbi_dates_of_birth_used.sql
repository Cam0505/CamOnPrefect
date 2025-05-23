


SELECT value as DoB, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as DoB_order, "_dlt_id" as wanted_DoB_sk
from {{ source("fbi", "wanted__dates_of_birth_used") }}