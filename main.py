"""Extract annotations, words and phrases from Kobo Ereader."""
import string

import pandas as pd
from wiktionaryparser import WiktionaryParser

from core import argparser
from core.database import KoboDB
from core.logs import ProjectLogger

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


if __name__ == '__main__':
    args = argparser.argparser()
    kwargs = vars(args)
    logger.setup_info()
    with KoboDB(kwargs.get("kobo_db")) as conn:
        cursor = conn.cursor()
        #df_books = KoboDB.run_query(cursor, kwargs.get("sql_books_read"))

        df = KoboDB.run_query(cursor, kwargs.get("sql_extract_annotations"))
        df["word_count"] = df["Text"].str.split().str.len()

        words = [clean_words_string(s) for s in list(
            df["Text"]) if len(s.split()) < kwargs.get("min_word_len")]

        df_quotes = df.loc[df["Text"].str.split().apply(
            len) > kwargs.get("min_word_len")]

        meanings = [word_wiktionary(wp, w) for w in words]

        words_dict = dict(zip(words, meanings))

        df = pd.DataFrame(words_dict)
