
SELECT name as author_name,
	book_key
From {{ source("openlibrary", "books__authors") }} 