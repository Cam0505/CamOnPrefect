


SELECT value as DoB, fw.uid as wanted_id, 
"_dlt_list_idx" as DoB_order, wf."_dlt_id" as wanted_DoB_sk
from {{ source("fbi", "wanted__dates_of_birth_used") }} as wf 
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"
where fw.uid is not null