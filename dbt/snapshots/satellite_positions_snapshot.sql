{% snapshot satellite_positions_snapshot %}
{{
    config(
      target_schema='public_snapshots',
      unique_key='satellite_id',
      strategy='timestamp',
      updated_at='sat_timestamp'
    )
}}

select
    satellite_id
    , satellite_name
    ,{{ convert_to_timezone(column_name='timestamp') }} as sat_timestamp
    , tle_line1
    , tle_line2
    , x_km
    , y_km
    , z_km
    , distance_km
from {{ source('satellite', 'satellite_positions') }}

{% endsnapshot %}