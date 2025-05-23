


SELECT value as country, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as country_order, "_dlt_id" as wanted_countries_sk
from {{ source("fbi", "wanted__possible_countries") }} as wf