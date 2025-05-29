{% macro convert_to_melbourne(column_name) %}
    {{ column_name }} AT TIME ZONE 'UTC' AT TIME ZONE 'Australia/Melbourne'
{% endmacro %}