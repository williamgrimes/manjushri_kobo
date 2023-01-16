"""Extract words and write to a csv-file."""
import string
from pathlib import Path
from typing import List, Dict

import pandas as pd
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet

from core.logs import ProjectLogger

logger = ProjectLogger(__name__)


def clean_words(df_words: pd.DataFrame) -> pd.DataFrame:
    """
    Clean words, strip whitespace, remove punctuation, make lowercase,
    and Lemmatize. Then drop duplicate rows in dataframe.

    Parameters:
    df_words (pd.DataFrame): The dataframe containing single words to clean

    Returns:
    pd.DataFrame: Dataframe of cleaned words
    """

    translator = str.maketrans('', '', string.punctuation)
    lemmatizer = WordNetLemmatizer()

    def _word_cleaner(word: str) -> str:
        word_before = word
        word = word.strip().lower().translate(translator)
        word = lemmatizer.lemmatize(word)
        logger.d(f"Word cleaned: \"{word_before}\" -> \"{word}\"")
        return word

    df_words["Text"] = df_words["Text"].apply(_word_cleaner)

    rows_dropped = df_words[df_words.duplicated(subset=["Text"], keep=False)]
    logger.i(
        f"{len(rows_dropped)} duplicate words dropped: {list(rows_dropped['Text'])}")
    df_words = df_words.drop_duplicates(subset=["Text"], keep='first')

    return df_words


def define_words(df_words: pd.DataFrame) -> pd.DataFrame:
    """
    Lookup word definitions, part of speech and examples using NLTK wordnet.

    Parameters:
    df_words (pd.DataFrame): The dataframe containing single words to lookup

    Returns:
    pd.DataFrame: Dataframe containing Answer column
    """

    pos_map = {"n": "Noun", "v": "Verb", "a": "Adjective",
               "s": "Adjective Satellite", "r": "Adverb"}

    def _wordnet_define(word: str) -> List:
        synsets = wordnet.synsets(word)
        if synsets:  # Definition found in wordnet
            logger.i(f"\"{word}\" - {len(synsets)} definition(s) found.")
            return [{"Definition": s.definition().capitalize(),
                     "Part of speech": pos_map.get(s.pos()),
                     "Examples": [e.capitalize() for e in s.examples()],
                     } for s in synsets]
        else:
            logger.i(f"\"{word}\" - definition not found.")
            return []

    df_words = df_words.copy()
    df_words["Answer"] = df_words["Text"].apply(_wordnet_define)

    df_defined, df_undefined = df_words[(
        mask := df_words["Answer"].astype(bool))].copy(), df_words[~mask].copy()

    logger.i(f"{len(df_defined)} word definitions found in wordnet.")
    undefined_words = list(df_undefined["Text"])
    logger.d(f"{len(undefined_words)} word definitions not found in wordnet: "
             f"{', '.join(undefined_words)}")
    return df_defined


def write_words_to_anki_csv(
        df_words: pd.DataFrame,
        anki_csv: Path,
        **kwargs: Dict) -> None:
    """
    Output definitions into a csv to be imported into Anki, where field 1 is
    the question and field 2 is the answer e.g.

    <h1>Inchoate</h1>,
    ----------------------------------------<large> 1 </large>----------------------------------------
    <em><b>
    Only partly in existence; imperfectly formed</b> - (Adjective Satellite)</em><small><u>

    Examples:</u>
    <em>""Incipient civil disorder""</em>
    <em>""An incipient tumor""</em>
    <em>""A vague inchoate idea""</em>
    </small>

    Parameters:
    df_words (pd.DataFrame): The dataframe containing single words to lookup
    anki_csv (Path): Path to output anki csv: Question, Answer

    Returns:
    None: Dataframe written to file
    """

    logger.d(f"Capitalize and <h1> tag questions in field 1")
    df_words["Text"] = df_words["Text"].apply(
        lambda r: f"<h1>{r.capitalize()}</h1>")

    logger.d(f"Format answers for Anki and enumerate definitions.")

    def _anki_formmater(answer):
        lines_separator = "----------------------------------------"

        def _format(i, a):
            a_str = f"\n{lines_separator}"
            a_str += f"<large> {i + 1} </large>"
            a_str += f"{lines_separator}\n"
            a_str += f"<em><b>\n{a['Definition']}</b> - ({a['Part of speech']})</em>"
            if examples := a.get("Examples"):
                a_str += "<small>"
                a_str += f'<u>\n\nExamples:</u>\n'
                for example in examples:
                    a_str += f"<em>\"{example}\"</em>\n"
                a_str += "</small>"
            return a_str

        answer_str = [_format(i, a) for i, a in enumerate(answer)]
        return f"\n".join(answer_str) + \
            f"\n{lines_separator}---{lines_separator}"

    df_words["Answer"] = df_words["Answer"].apply(_anki_formmater)

    logger.i(
        f"Writing {len(df_words)} definition question and answers to {anki_csv=}.")
    df_words[['Text', 'Answer']].to_csv(anki_csv, index=False, header=False)
    return None


def main(df_words, **kwargs):

    logger.i(f"PROCESSING WORDS "
             f"max_word_len = {kwargs.get('max_word_len')}.")

    df_words = clean_words(df_words)

    df_words = define_words(df_words)

    write_words_to_anki_csv(df_words, **kwargs)
