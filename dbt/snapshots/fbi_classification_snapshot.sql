-- ------------------------------------------------------------------------------
-- Model: fbi_classification_snapshot.sql
-- Description: Track changes in source FBI classifications over time
-- ------------------------------------------------------------------------------
-- Change Log:
-- Date       | Author   | Description
-- -----------|----------|-------------------------------------------------------
-- 2025-05-23 | Cam      | Initial creation
-- YYYY-MM-DD | NAME     | [Add future changes here]
-- ------------------------------------------------------------------------------
{% snapshot fbi_classification_snapshot %}

{{
    config(
        target_schema='public_snapshots',
        unique_key='pk',
        strategy='check',
        check_cols=['person_classification'],
        invalidate_hard_deletes=True
    )
}}


SELECT
    person_classification
    , pk
FROM {{ ref('base_fbi_wanted') }}
GROUP BY person_classification, pk

{% endsnapshot %}