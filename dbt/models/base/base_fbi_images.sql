



SELECT large as large_image, thumb as thumb_image, original as original_image, 
fw.uid as wanted_id, "_dlt_list_idx" as image_order, 
wf."_dlt_id" as wanted_images_sk, caption
from {{ source("fbi", "wanted__images") }} as wf 
left join {{ source("fbi", "wanted") }} as fw 
on wf."_dlt_root_id" = fw."_dlt_id"