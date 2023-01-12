"""Extract annotations, words and phrases from Kobo Ereader."""

import string
from pathlib import Path

import pandas as pd
from wiktionaryparser import WiktionaryParser

from shared_utils.db_utils import DBConnection, query_to_df
from shared_utils.log_utils import get_logger

logger = get_logger(__name__)

KOBO_DB_PATH = Path("/home/will/KoboBooks/KoboReader.sqlite")

QUERY_BOOKS_READ_PATH = Path("sql/books_read.sql")
QUERY_EXTRACT_ANNOTATIONS_PATH = Path("sql/extract_annotations.sql")

word_len = 3

wp = WiktionaryParser()


def clean_words_string(words_string: str) -> str:
    """Clean strings to words without punctuation."""
    words_string = words_string.lower()

    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    words_string = words_string.translate(translator)

    words_string = words_string.lower()

    return words_string


def word_wiktionary(wp: WiktionaryParser,
                    word: str,
                    keep_keys: list = ["definitions", "etymology"]) -> dict:
    """Return wiktionary entry for word."""
    word_dict = wp.fetch(word).pop()

    try:
        definitions = word_dict.get("definitions").pop()
        etymology = word_dict.get("etymology")
    except IndexError:
        print(f"Could not define {word}")

    # TODO determine return format for parts of speech

    return word_dict


if __name__ == '__main__':
    with DBConnection(KOBO_DB_PATH) as conn:
        cursor = conn.cursor()

        df_books = query_to_df(cursor, QUERY_BOOKS_READ_PATH)

        df_annotations = query_to_df(
            cursor, QUERY_EXTRACT_ANNOTATIONS_PATH)

        df_annotations["word_count"] = df_annotations["Text"].str.split(
        ).str.len()

        words = [clean_words_string(s) for s in list(
            df_annotations["Text"]) if len(s.split()) < word_len]

        df_quotes = df_annotations.loc[df_annotations["Text"].str.split().apply(
            len) > word_len]

        meanings = [word_wiktionary(wp, w) for w in words]

        words_dict = dict(zip(words, meanings))

        df = pd.DataFrame(words_dict)
