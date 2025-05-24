


SELECT wf.url as url_link, name as language_name, 
fw.uid as wanted_id
, "_dlt_list_idx" as file_order,
wf."_dlt_id" as wanted_files_sk
from {{ source("fbi", "wanted__files") }} as wf
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"