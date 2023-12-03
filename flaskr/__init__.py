import os
from flask import Flask, jsonify, render_template, request
from flaskr.api_handlers import tmdb_handler, google_books_handler
from flaskr.utils import queries



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query')
        search_type = request.args.get('type')  # 'movie' or 'book'

        if search_type == 'movie':
            results = tmdb_handler.search_movies(query)
        elif search_type == 'book':
            results = google_books_handler.search_books(query)
        else:
            results = []

        return jsonify(results)

    @app.route('/recommend_books', methods=['GET'])
    def recommend_books():
        item_id = request.args.get('id')
        include_adaptations = request.args.get('include_adaptations') == 'true'
        movie = tmdb_handler.get_movie(item_id)

        # Generate book search queries
        book_queries = queries.create_book_queries(movie)
        # Fetch books and score them
        book_recommendations = google_books_handler.fetch_and_score_books(book_queries[0:100], movie, include_adaptations)
        return jsonify(book_recommendations)

    @app.route('/recommend_movies', methods=['GET'])
    def recommend_movies():
        book_id = request.args.get('id')
        include_adaptations = request.args.get('include_adaptations') == 'true'
        book_details = google_books_handler.get_book_details(book_id)
        book_lang = book_details.get('volumeInfo', {}).get('language', 'en')
        #if book_lang != 'en':
            # no free translation apis :(
            #book_details['volumeInfo']['title'] = translation.translate(book_details['volumeInfo']['title'], book_lang, 'en')
            #book_details['volumeInfo']['description'] = translation.translate(book_details['volumeInfo']['description'], book_lang, 'en')
        movie_genres = tmdb_handler.movie_genres()
        movie_queries = queries.create_movie_queries(book_details)
        movie_recommendations = tmdb_handler.fetch_and_score_movies(movie_queries, book_details, movie_genres, include_adaptations)

        return jsonify(movie_recommendations)
    

    return app