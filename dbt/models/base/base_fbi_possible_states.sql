

SELECT value as wanted_state, fw.uid as wanted_id, 
"_dlt_list_idx" as state_order, wf."_dlt_id" as wanted_states_sk
from {{ source("fbi", "wanted__possible_states") }} as wf
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"
where fw.uid is not null