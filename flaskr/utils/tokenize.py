import os
import nltk

# Set the NLTK data directory
nltk_data_dir = '/app/nltk_data'
nltk.data.path.append(nltk_data_dir)

# Check if it exsists
def download_nltk_data(package, subfolder):
    data_path = os.path.join(nltk_data_dir, subfolder)
    if not os.path.exists(data_path):
        nltk.download(package, download_dir=nltk_data_dir)

download_nltk_data('punkt', 'tokenizers/punkt')
download_nltk_data('stopwords', 'corpora/stopwords')
download_nltk_data('wordnet', 'corpora/wordnet')


from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re

def extract_key_phrases(text):
    """
    Extract key phrases from text using NLP techniques.

    :param text: String containing the text to analyze.
    :return: List of key phrases or words.
    """
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(token) for token in tokens]

    # Return unique lemmas
    return list(set(lemmas))

def preprocess_keywords(text):
    """
    Preprocess text data to extract keywords.

    :param text: Input text.
    :return: Preprocessed text.
    """
    return ''.join(e.lower() for e in text if e.isalnum() or e.isspace())

def preprocess_list(words):
    """
    Preprocess a list of words.

    :param words: List of words.
    :return: Preprocessed list of words.
    """
    return [preprocess_keywords(word) for word in words]

def normalize_categories(genre_list):
    genre_frequency = Counter()

    for genre_string in genre_list:
        # Split, preprocess, and count genres
        split_genres = [preprocess_keywords(g) for g in re.split(r'[/&]', genre_string)]
        genre_frequency.update(filter(None, split_genres))

    # Remove non-genre terms
    non_genre_descriptors = {'general', 'contemporary'}
    filtered_genres = [genre for genre, count in genre_frequency.items() if genre not in non_genre_descriptors]

    return filtered_genres
