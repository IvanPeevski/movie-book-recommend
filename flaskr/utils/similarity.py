from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flaskr.utils import tokenize


def score_movies(movies, book_details, include_adaptations=False):
    """
    Score movies based on their relevance to a given book.

    :param movies: List of movies to be scored.
    :param book_details: Details of the selected book.
    :return: List of scored movies.
    """
    scoring = {
        "genre": 0.3,
        "keyword": 0.15,
        "title": 0.4,
        "synopsis": 0.25,
    }
    if not include_adaptations:
        #punish title similarity
        scoring = {
            "genre": 0.3,
            "keyword": 0.8,
            "title": -0.3,
            "synopsis": 0.4,
        }
    
    for movie in movies:
        movie['score'] = 0
        movie['score'] += genre_similarity_score(book_details, movie) * scoring["genre"]
        movie['score'] += keyword_similarity_score(book_details, movie) * scoring["keyword"]
        movie['score'] += title_similarity_score(book_details, movie) * scoring["title"]
        movie['score'] += synopsis_similarity_score(book_details, movie) * scoring["synopsis"]

        #a slight boost for movies with more than 0 ratings
        movie['score'] += movie['score'] *  0.1 * (movie.get('vote_count', 0) > 0)
    
    return sorted(movies, key=lambda x: x['score'], reverse=True)

def score_books(books, movie_details, include_adaptations=False):
    """
    Score books based on their relevance to a given movie.

    :param books: List of books to be scored.
    :param movie_details: Details of the selected movie.
    :return: List of scored books.
    """
    scoring = {
        "genre": 0.3,
        "keyword": 0.15,
        "title": 0.4,
        "synopsis": 0.25,
    }
    if not include_adaptations:
        #punish title similarity
        scoring = {
            "genre": 0.3,
            "keyword": 0.8,
            "title": -0.3,
            "synopsis": 0.4,
        }

    for book in books:
        volume_info = book.get('volumeInfo', {})
        book['score'] = 0
        book['score'] += genre_similarity_score(book, movie_details) * scoring["genre"]
        book['score'] += keyword_similarity_score(volume_info, movie_details) * scoring["keyword"]
        book['score'] += title_similarity_score(volume_info, movie_details) * scoring["title"]
        book['score'] += synopsis_similarity_score(volume_info, movie_details) * scoring["synopsis"]

        #a slight boost for books with more than 0 ratings
        book['score'] += book['score'] *  0.1 * (book.get('ratingsCount', 0) > 0)

    return sorted(books, key=lambda x: x['score'], reverse=True)

def genre_similarity_score(book, movie):
    """
    Calculate genre similarity score between a book and a movie.

    :param book: Book data.
    :param movie: Movie data.
    :return: Genre similarity score.
    """
    movie_genres = tokenize.preprocess_keywords(' '.join(movie.get('genres', [])))
    book_genres = ' '.join(tokenize.normalize_categories(book.get('categories', [])))
    return text_similarity(movie_genres, book_genres)

def keyword_similarity_score(book, movie):
    """
    Calculate genre similarity score between a book and a movie.

    :param book: Book data.
    :param movie: Movie data.
    :return: Genre similarity score.
    """
    movie_genres = tokenize.preprocess_keywords(' '.join(movie.get('keywords', [])))
    book_genres = ' '.join(tokenize.normalize_categories(book.get('categories', [])))

    return text_similarity(movie_genres, book_genres)



def title_similarity_score(book, movie):
    """
    Calculate keyword similarity score between a book and a movie.

    :param book: Book data.
    :param movie: Movie data.
    :return: Keyword similarity score.
    """
    book_keywords = tokenize.preprocess_keywords(book.get('title', ''))
    movie_keywords = tokenize.preprocess_keywords(movie.get('title', ''))

    return text_similarity(book_keywords, movie_keywords)


def synopsis_similarity_score(book, movie):
    """
    Calculate the similarity score between a book's description and a movie's synopsis.

    :param book: Book data.
    :param movie: Movie data.
    :return: Synopsis similarity score.
    """
    book_description = tokenize.preprocess_keywords(tokenize.extract_key_phrases(book.get('description', '')))
    movie_synopsis = tokenize.preprocess_keywords(tokenize.extract_key_phrases(movie.get('overview', '')))

    return text_similarity(book_description, movie_synopsis)

def text_similarity(text1, text2):
    """
    Calculate the similarity score between two texts.

    :param text1: First text.
    :param text2: Second text.
    :return: Text similarity score.
    """
    if not text1 or not text2:
        return 0

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return np.squeeze(similarity)
