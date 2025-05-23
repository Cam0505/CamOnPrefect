


SELECT value as aliases, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as aliases_order, 
"_dlt_id" as wanted_aliases_sk
from {{ source("fbi", "wanted__aliases") }}