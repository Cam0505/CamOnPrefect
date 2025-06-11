

SELECT search_term,
	key as book_key,
	title,
	ebook_access,
	first_publish_year,
	has_fulltext
From {{ source("openlibrary", "books") }} 