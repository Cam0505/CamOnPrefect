



SELECT large as large_image, thumb as thumb_image, original as original_image, 
"_dlt_root_id" as wanted_id, "_dlt_list_idx" as image_order, 
"_dlt_id" as wanted_images_sk, caption
from {{ source("fbi", "wanted__images") }}