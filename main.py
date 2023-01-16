"""Extract annotations, words and phrases from Kobo Ereader."""

import pandas as pd

from core import argparser, quotes, words
from core.database import KoboDB
from core.logs import ProjectLogger

logger = ProjectLogger(__name__)


def split_words_and_quotes(df: pd.DataFrame, max_word_len: int, **kwargs) -> (pd.DataFrame, pd.DataFrame):
    df["word_count"] = df["Text"].str.split().str.len()
    mask = df['word_count'] <= max_word_len
    df_words = df[mask].reset_index(drop=True).copy()
    df_quotes = df[~mask].reset_index(drop=True).copy()
    logger.i(f"Split df {len(df)} into df_words {len(df_words)} and quotes {len(df_quotes)}.")
    return df_words, df_quotes


if __name__ == '__main__':
    args = argparser.argparser()
    kwargs = vars(args)
    logger.setup_info()
    with KoboDB(kwargs.get("kobo_db")) as conn:
        cursor = conn.cursor()

        df_annotations = KoboDB.run_query(cursor, kwargs.get("sql_extract_annotations"))

        df_words, df_quotes = split_words_and_quotes(df_annotations, **kwargs)

        quotes.main(df_quotes, **kwargs)

        words.main(df_words, **kwargs)
