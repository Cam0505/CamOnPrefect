



SELECT value as field_office, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as field_office_order, "_dlt_id" as wanted_field_offices_sk
from {{ source("fbi", "wanted__field_offices") }}