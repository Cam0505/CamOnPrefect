



SELECT value as occupations, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as occupations_order, "_dlt_id" as wanted_occupations_sk
from {{ source("fbi", "wanted__occupations") }}