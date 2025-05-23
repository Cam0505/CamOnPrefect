


SELECT value as wanted_language, "_dlt_root_id" as wanted_id, 
"_dlt_list_idx" as language_order, "_dlt_id" as wanted_languages_sk
from {{ source("fbi", "wanted__languages") }}