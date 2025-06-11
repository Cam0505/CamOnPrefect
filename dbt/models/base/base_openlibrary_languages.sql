SELECT code,
	book_key
From {{ source("openlibrary", "books__languages") }} 