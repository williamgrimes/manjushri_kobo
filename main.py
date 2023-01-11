"""Extract annotations, words and phrases from Kobo Ereader."""

import sqlite3
import string
from pathlib import Path

import pandas as pd
from wiktionaryparser import WiktionaryParser

KOBO_DB_PATH = Path("/home/will/KoboBooks/KoboReader.sqlite")

word_len = 3


wp = WiktionaryParser()

QUERY_BOOKS = """
  SELECT *
  FROM content
  WHERE ReadStatus == 2;
  """

QUERY_BOOKMARKS = """
  SELECT
  -- Bookmark.VolumeID,
  Bookmark.Text,
  Bookmark.Annotation,
  Bookmark.ExtraAnnotationData,
  Bookmark.DateCreated,
  Bookmark.DateModified,
  content.BookTitle,
  content.Title,
  content.Attribution
  FROM Bookmark INNER JOIN content
  ON Bookmark.VolumeID = content.ContentID;
"""


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


def sqlite_query_to_pd(conn: sqlite3.Connection,
                       QUERY: str,
                       ) -> pd.DataFrame:
    """Return pandas dataframe of a SQLite Query."""
    cursor = conn.cursor()
    cursor.execute(QUERY)
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(results, columns=columns)
    print(f"Query:\n{QUERY}\nReturned Dataframe with "
          f"{len(df)} rows and {len(df.columns)}.")
    return df


if __name__ == '__main__':
    conn = sqlite3.connect(KOBO_DB_PATH)

    df_books = sqlite_query_to_pd(conn, QUERY_BOOKS)

    df_bookmarks = sqlite_query_to_pd(conn, QUERY_BOOKMARKS)

    words = [clean_words_string(s) for s in list(
        df_bookmarks["Text"]) if len(s.split()) < word_len]

    quotes = [s for s in list(df_bookmarks["Text"]) if len(s.split()) >= word_len]

    meanings = [word_wiktionary(wp, w) for w in words]

    words_dict = dict(zip(words, meanings))

    df = pd.DataFrame(words_dict).head()

    conn.close()
