"""Extract annotations, words and phrases from Kobo Ereader."""
from typing import Tuple

import pandas as pd

from core import argparser, quotes, words
from core.database import KoboDB
from core.logs import ProjectLogger

logger = ProjectLogger(__name__)


def split_words_and_quotes(df: pd.DataFrame,
                           max_word_len: int,
                           **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split dataframe into words and quotes based on word count

    Parameters:
    df (pd.DataFrame): The dataframe to be split
    max_word_len (int): The maximum word length to be considered as a word
    kwargs: Additional keyword arguments

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame]: Tuple of dataframes - words and quotes
    """
    df = df.assign(word_count=df['Text'].str.split().str.len())
    df_words = df.query('word_count <= @max_word_len').reset_index(drop=True)
    df_quotes = df.query('word_count > @max_word_len').reset_index(drop=True)
    logger.i(f"Splitting: {len(df)=} -> {len(df_words)=} and {len(df_quotes)=}.")
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
