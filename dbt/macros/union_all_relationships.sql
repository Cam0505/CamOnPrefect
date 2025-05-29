
-- macros/union_all_relations.sql

-- Macro: union_all_relations
-- Description:
--     Dynamically unions a list of relations (e.g., models or tables) using `UNION ALL`.
--     Useful when you have multiple partitioned or monthly datasets you want to combine.
-- Inputs:
--     relation_list: List of references (e.g., [ref('table1'), ref('table2')])
-- Output:
--     Returns a SQL string with all tables unioned together.
-- Created: 2025-05-29
-- Author: Cam's AI Assistant

{% macro union_all_relations(relation_list) %}
    {% set sql %}
        {% for rel in relation_list %}
            SELECT * FROM {{ rel }}{% if not loop.last %} UNION ALL {% endif %}
        {% endfor %}
    {% endset %}
    {{ return(sql) }}
{% endmacro %}