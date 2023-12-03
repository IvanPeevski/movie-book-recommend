import json
import requests
from flaskr.utils import similarity

def search_books(query, max_results=40, format_results=True):
    """
    Search for books based on a query string.

    :param query: The search string.
    :return: A list of books matching the query.
    """
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': max_results,
        'printType': 'books',
    }
    headers = {'Accept-Language': 'en-US'}
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json().get('items', [])
        if format_results:
            return format_book_results(results)
        return results
    else:
        return []

def format_book_results(books):
    """
    Format the book results to include only relevant information.

    :param books: The list of books from the Google Books API response.
    :return: A formatted list of books.
    """
    seen = set()
    formatted_results = []
    for book in books:
        volume_info = book.get('volumeInfo', {})
        if volume_info.get('title') in seen or not volume_info.get('description'):
            continue
        formatted_book = {
            'id': book.get('id'),
            'title': volume_info.get('title'),
            'overview': volume_info.get('description'),
            'previewImage': volume_info.get('imageLinks', {}).get('thumbnail'),
            'ratingsCount': volume_info.get('ratingsCount', 0),
            'authors': volume_info.get('authors', []),
            'year': volume_info.get('publishedDate', '')[:4],
            'rating': volume_info.get('averageRating', 0),
        }
        formatted_results.append(formatted_book)
        seen.add(formatted_book['title'])

    return formatted_results

def get_book_details(book_id):
    """
    Get the details for a book based on its ID.

    :param book_id: The ID of the book.
    :return: A dictionary containing the book details.
    """
    base_url = "https://www.googleapis.com/books/v1/volumes/{}".format(book_id)
    params = {}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return book_data(response.json())
    else:
        return {}
    
def book_data(book):
    return {
                'id': book['id'],
                'volumeInfo': book['volumeInfo'],
            }

def fetch_and_score_books(queries, movie, include_adaptations=False):
    """
    Fetch books from Google Books API and score them based on their similarity to the movie.

    :param queries: A list of search queries.
    :param movie: The movie data.
    :return: A list of scored books.
    """
    books = []
    seen = set()
    for query in queries:
        book_result = search_books(query, 40, format_results=False)
        for book in book_result:
            if book['id'] not in seen and book['volumeInfo'].get('description') and book['volumeInfo'].get('ratingsCount'):
                books.append(book_data(book))
                seen.add(book['id'])
    books = similarity.score_books(books, movie, include_adaptations)[:15]
    
    return format_book_results(books[:15])