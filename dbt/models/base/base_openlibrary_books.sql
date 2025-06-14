SELECT
    search_term
    , key AS book_key
    , title
    , ebook_access
    , first_publish_year
    , has_fulltext
FROM {{ source("openlibrary", "books") }}