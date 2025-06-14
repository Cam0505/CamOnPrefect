-- ------------------------------------------------------------------------------
-- Model: glass_type_snapshots.sql
-- Description: Track changes in source glass types over time
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
{% snapshot glass_type_snapshot %}

{{
    config(
        target_schema='public_snapshots',
        unique_key='beverage_id',
        strategy='check',
        check_cols=['glass_type', 'glass_type_sk'],
        invalidate_hard_deletes=True
    )
}}

SELECT
    id_drink AS beverage_id
    , source_glass AS glass_type
    , {{ dbt_utils.generate_surrogate_key(["glass_type"]) }} AS glass_type_sk
FROM {{ source("beverages", "glass_table") }}

{% endsnapshot %}