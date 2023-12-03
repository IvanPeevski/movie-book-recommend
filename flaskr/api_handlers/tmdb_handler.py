import json
import requests
from flaskr.utils import similarity

TMDB_API_KEY = 'fad9ef38bf774e691adae600ff8d5d2b'


def movie_genres():
    """
    Get a list of movie genres.

    :return: A list of movie genres.
    """
    base_url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        genres = json.loads(response.content).get('genres', [])
        return genres
    else:
        return []

def search_movies(query, format_results=True):
    """
    Search for movies based on a query string.

    :param query: The search string.
    :return: A list of movies matching the query.
    """
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': query
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = json.loads(response.content).get('results')
        if format_results:
            return format_movie_results(results)
        return results
    else:
        return []
    
def get_keyword_id(keyword):
    """
    Get the ID of a keyword.

    :param keyword: The keyword to search for.
    :return: The ID of the keyword.
    """
    base_url = "https://api.themoviedb.org/3/search/keyword"
    params = {
        'api_key': TMDB_API_KEY,
        'query': keyword
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = json.loads(response.content).get('results')
        if results:
            return results[0].get('id')
        return None
    else:
        return None
    
def discover_movies(keyword):
    """
    Discover movies from TMDB API based on keywords
    :param keywords: keyword ID.
    :return: List of discovered movies.
    """
    base_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'with_keywords': keyword,
        'sort_by': 'vote_count.desc',
        'page': 1
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return []

def format_movie_results(movies):
    """
    Format the movie results to include only relevant information.

    :param movies: The list of movies from the TMDB API response.
    :return: A formatted list of movies.
    """
    formatted_results = []
    for movie in movies:
        formatted_movie = {
            'id': movie.get('id'),
            'title': movie.get('title'),
            'overview': movie.get('overview'),
            'previewImage': 'https://image.tmdb.org/t/p/w500' + movie.get('poster_path') if movie.get('poster_path') else ""
        }
        formatted_results.append(formatted_movie)
    
    return formatted_results


def get_movie_keywords(movie_id):
    """
    Get the keywords for a movie based on its ID.

    :param movie_id: The ID of the movie.
    :return: A list of keywords.
    """
    base_url = "https://api.themoviedb.org/3/movie/{}/keywords".format(movie_id)
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        keywords = json.loads(response.content).get('keywords', [])
        return [keyword.get('name') for keyword in keywords]
    else:
        return []
    
def get_movie(movie_id):
    """
    Get a movie based on its ID.

    :param movie_id: The ID of the movie.
    :return: A movie object.
    """
    base_url = "https://api.themoviedb.org/3/movie/{}".format(movie_id)
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        movie = json.loads(response.content)
        keywords = get_movie_keywords(movie_id)
        return movie_data(movie, keywords)
    else:
        return None
    
def movie_data(movie, keywords, genreDict=None):
    """
    Format the movie to include only relevant information.

    :param movie: The movie from the TMDB API response.
    :return: A formatted movie.
    """
    formatted_movie = {
        'id': movie.get('id'),
        'title': movie.get('title'),
        'overview': movie.get('overview'),
        'genres': [genre.get('name', '') for genre in movie.get('genres', [])],
        'keywords': keywords,
        'previewImage': 'https://image.tmdb.org/t/p/w500' + movie.get('poster_path') if movie.get('poster_path') else "",
        'rating': movie.get('vote_average', 0),
        'vote_count': movie.get('vote_count', 0),
        'year': movie.get('release_date', '')[:4] if movie.get('release_date') else ''
    }

    if genreDict:
        formatted_movie['genres'] = [genreDict.get(genre_id, '') for genre_id in movie.get('genres', [])]
    
    return formatted_movie

def fetch_and_score_movies(queries, book, movie_genres, include_adaptations=False):
    """
    Fetch movies based on a list of queries and score them based on their similarity to the book.

    :param queries: A list of search query strings.
    :param book: A dictionary containing details of the book.
    :param movie_genres: An array of movie genres.
    :param include_adaptations: Whether to include movies that are adaptations of the book.
    :return: A list of movies sorted by their similarity score.
    """
    movies = []
    seen = set()
    genre_dict = {genre['id']: genre['name'].lower() for genre in movie_genres}

    for query in queries:
        movie_results = discover_movies(query)
        for movie in movie_results:
            if movie.get('id') not in seen:
                movies.append(movie_data(movie, get_movie_keywords(movie['id']), genre_dict))
                seen.add(movie.get('id'))

    movies = similarity.score_movies(movies, book, include_adaptations=include_adaptations)
    return movies[0:15]