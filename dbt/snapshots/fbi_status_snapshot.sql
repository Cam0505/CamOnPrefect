-- ------------------------------------------------------------------------------
-- Model: fbi_status_snapshot.sql
-- Description: Track changes in source FBI statuses over time
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
{% snapshot fbi_status_snapshot %}

{{
    config(
        target_schema='public_snapshots',
        unique_key='pk',
        strategy='check',
        check_cols=['fbi_status'],
        invalidate_hard_deletes=True
    )
}}


SELECT status as fbi_status, pk
FROM {{ ref('base_fbi_wanted') }}
GROUP BY status, fbi_status, pk

{% endsnapshot %}