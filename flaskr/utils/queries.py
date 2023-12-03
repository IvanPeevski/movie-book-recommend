from flaskr.utils import tokenize
from flaskr.api_handlers import tmdb_handler, google_books_handler


def create_movie_queries(book_details):
    """
    Create a list of query objects for movie searches based on book details.

    :param book_details: A dictionary containing details of the book.
    :return: A list of queries
    """
    queries = set()
    categories = tokenize.normalize_categories(book_details.get('volumeInfo', {}).get('categories', []))
    overview = book_details.get('volumeInfo', {}).get('description', '')
    thematic_keywords = tokenize.preprocess_list(tokenize.extract_key_phrases(overview)[:10])

    max_length = max(len(categories), len(thematic_keywords))
    for i in range(max_length):
        if i < len(categories):
            keyword_id = tmdb_handler.get_keyword_id(categories[i])
            if keyword_id:
                queries.add(keyword_id)
        if i < len(thematic_keywords) and book_details.get('volumeInfo', {}).get('language', 'en') == 'en':
            keyword_id = tmdb_handler.get_keyword_id(thematic_keywords[i])
            if keyword_id:
                queries.add(keyword_id)
    
    return list(queries)[:5]


def create_book_queries(movie_details):
    """
    Create a focused list of search queries for books based on movie details, minimizing the use of the movie title.

    :param movie_details: A dictionary containing details of the movie.
    :return: A list of search query strings.
    """
    queries = []
    
    genres = tokenize.preprocess_list(movie_details.get('genres', []))[0:5]
    keywords = tokenize.preprocess_list(movie_details.get('keywords', []))[0:5]
    overview = movie_details.get('overview', '')

    thematic_keywords = tokenize.extract_key_phrases(overview)[:3]

    max_length = max(len(genres), len(keywords), len(thematic_keywords))
    for i in range(max_length):
        if i < len(keywords):
            queries.append(keywords[i])

        if i < len(genres) and i < len(thematic_keywords):
            queries.append(f"{thematic_keywords[i]} {genres[i]}")

        if i < len(keywords) and i < len(thematic_keywords):
            queries.append(f"{thematic_keywords[i]} {keywords[i]}")

        if i < len(genres) and i < len(keywords):
            queries.append(f"{genres[i]} {keywords[i]}")

    return list(set(queries))[:17]

