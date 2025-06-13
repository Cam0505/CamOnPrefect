SELECT
    name AS author_name
    , book_key
FROM {{ source("openlibrary", "books__authors") }}