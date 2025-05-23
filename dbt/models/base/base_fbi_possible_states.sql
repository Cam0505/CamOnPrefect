

SELECT value as wanted_state, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as state_order, "_dlt_id" as wanted_states_sk
from {{ source("fbi", "wanted__possible_states") }} as wf