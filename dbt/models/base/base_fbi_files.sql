


SELECT url as url_link, name as language_name, "_dlt_root_id" as wanted_id
, "_dlt_list_idx" as file_order,
"_dlt_id" as wanted_files_sk
from {{ source("fbi", "wanted__files") }} as wf