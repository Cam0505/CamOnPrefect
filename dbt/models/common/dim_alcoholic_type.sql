-- ------------------------------------------------------------------------------
-- Model: Dim_alcoholic_type
-- Description: Dimension Table, alcoholic type information (Test)
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------

SELECT alcoholic_type, 
alcoholic_type_sk
	From {{ref('staging_beverage_lookup')}}
group by alcoholic_type, alcoholic_type_sk