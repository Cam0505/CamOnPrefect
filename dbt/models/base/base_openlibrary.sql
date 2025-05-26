

SELECT search_term, topic_filter, title, author_name, publish_year, edition_count
From {{ source("openlibrary", "python_books") }} 
union all
SELECT search_term, topic_filter, title, author_name, publish_year, edition_count
FROM {{ source("openlibrary", "apache_airflow_books") }}
union all
SELECT search_term, topic_filter, title, author_name, publish_year, edition_count
FROM {{ source("openlibrary", "data_engineering_books") }}
union all
SELECT search_term, topic_filter, title, author_name, publish_year, edition_count
FROM {{ source("openlibrary", "data_warehousing_books") }}
union all
SELECT search_term, topic_filter, title, author_name, publish_year, edition_count
FROM {{ source("openlibrary", "sql_books") }}