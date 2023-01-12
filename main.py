"""Extract annotations, words and phrases from Kobo Ereader."""
import argparse
import string

import pandas as pd
from wiktionaryparser import WiktionaryParser

from shared_utils.database import KoboDB
from shared_utils.logs import ProjectLogger

logger = ProjectLogger(__name__)

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


def argparser():
    parser = argparse.ArgumentParser(
        description="Kobo Extract Annotations.")
    parser.add_argument("--kobo_db",
                        type=str,
                        help="path to kobo sqlite database KoboReader.sqlite")
    parser.add_argument("--logs_dir",
                        default="logs/",
                        type=str,
                        help="folder containing logs.")
    parser.add_argument("--min_word_len",
                        default=3,
                        type=int,
                        help="number of words to differentiate a quote.")
    parser.add_argument("--sql_books_read",
                        default="sql/books_read.sql",
                        type=str,
                        help="path to sql query returning books read.")
    parser.add_argument("--sql_extract_annotations",
                        default="sql/extract_annotations.sql",
                        type=str,
                        help="path to sql query returning annotations.")
    return parser.parse_args()


def main(**kwargs):
    logger.setup_info()
    with KoboDB(kwargs.get("kobo_db")) as conn:
        cursor = conn.cursor()

        df_books = KoboDB.query_to_df(cursor, kwargs.get("sql_books_read"))

        df = KoboDB.query_to_df(
            cursor, kwargs.get("sql_extract_annotations"))

        df["word_count"] = df["Text"].str.split(
        ).str.len()

        words = [clean_words_string(s) for s in list(
            df["Text"]) if len(s.split()) < kwargs.get("min_word_len")]

        df_quotes = df.loc[df["Text"].str.split().apply(
            len) > kwargs.get("min_word_len")]

        meanings = [word_wiktionary(wp, w) for w in words]

        words_dict = dict(zip(words, meanings))

        df = pd.DataFrame(words_dict)


if __name__ == '__main__':
    args = argparser()
    main(**vars(args))
