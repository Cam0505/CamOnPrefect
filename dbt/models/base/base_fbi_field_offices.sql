



SELECT value as field_office, fw.uid as wanted_id, 
"_dlt_list_idx" as field_office_order, wf."_dlt_id" as wanted_field_offices_sk
from {{ source("fbi", "wanted__field_offices") }} as wf 
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"
where fw.uid is not null