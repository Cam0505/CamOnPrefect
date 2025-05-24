



SELECT value as occupations, fw.uid as wanted_id, 
"_dlt_list_idx" as occupations_order, wf."_dlt_id" as wanted_occupations_sk
from {{ source("fbi", "wanted__occupations") }} as wf
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"