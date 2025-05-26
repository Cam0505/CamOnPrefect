


SELECT value as aliases, fw.uid as wanted_id, 
"_dlt_list_idx" as aliases_order, 
wf."_dlt_id" as wanted_aliases_sk
from {{ source("fbi", "wanted__aliases") }} as wf 
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"
where fw.uid is not null