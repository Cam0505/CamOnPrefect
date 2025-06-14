SELECT
    code
    , book_key
FROM {{ source("openlibrary", "books__languages") }}