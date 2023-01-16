"""Extract annotations, words and phrases from Kobo Ereader."""
import string
from datetime import datetime

import pandas as pd
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from core import argparser
from core.database import KoboDB
from core.logs import ProjectLogger

logger = ProjectLogger(__name__)


def df_split_words_quotes(df: pd.DataFrame, max_word_len: int,**kwargs) -> (pd.DataFrame, pd.DataFrame):
    df["word_count"] = df["Text"].str.split().str.len()
    df_words, df_quotes = df[(mask := df['word_count'] <= max_word_len)].copy(), df[~mask].copy()
    logger.i(f"Split df {len(df)} into df_words {len(df_words)} and quotes {len(df_quotes)}.")
    return df_words, df_quotes

def write_quotes(df_quotes, org_file, org_user, org_date, org_initial_visibility, **kwargs):
    df_quotes.sort_values(by=["DateLastRead"], inplace=True)
    replacers = {"\n": " ", "\r": " ", "\\xa0\\xa0\\xa0": " ", "  ": " "}
    df_quotes["Text"] = df_quotes["Text"].str.strip()
    df_quotes["Text"] = df_quotes["Text"].replace(replacers, regex=True)
    group_cols = ["DateLastRead", "Title", "Attribution"]
    df_grp = df_quotes.groupby(group_cols)
    with open(org_file, 'w') as f:
        f.write(f"#+TITLE: Book Annotations")
        f.write(f"\n#+AUTHOR: {org_user}")
        f.write(f"\n#+DATE: {org_date}")
        f.write(f"\n#+STARTUP: {org_initial_visibility}\n")
        for group_name, df_group in df_grp:
            group_info = dict(zip(group_cols, group_name))
            date = datetime.fromisoformat(group_info.get('DateLastRead')).strftime("%Y-%m:%d")
            f.write(f"\n* {group_info.get('Title')}")
            f.write(f"\n:PROPERTIES:")
            f.write(f"\n:AUTHOR {group_info.get('Attribution')}")
            f.write(f"\n:DATE LAST READ: {date}")
            f.write(f"\n:END:")

            for index, row in df_group.iterrows():
                f.write(f"\n + /\"{row.Text}/\"\n")
    return None


def clean_word(words_string: str) -> str:
    """Clean words, remove punctuation, make lowercase, and Lemmatize to."""
    words_string = words_string.lower()

    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    words_string = words_string.translate(translator)

    lemmatizer = WordNetLemmatizer()
    lemmatized_word = lemmatizer.lemmatize(words_string)

    word = lemmatized_word.strip()

    return word

def define_words(df_words):
    pos_code_map = {
        "n": "Noun",
        "v": "Verb",
        "a": "Adjective",
        "s": "Adjective Satellite",
        "r": "Adverb"
    }

    cols = ["Definition", "PartOfSpeech", "Examples"]
    def define(row):
        word = row["Text"]
        synsets = wordnet.synsets(word)
        if synsets:
            logger.i(f"\"{word}\" - {len(synsets)} definition(s) found.")
            return [{"Definition": s.definition().capitalize(),
                     "Part of speech": pos_code_map.get(s.pos()),
                     "Examples": [e.capitalize() for e in s.examples()],
                     } for s in synsets]
        else:
            logger.i(f"\"{word}\" - definition not found.")
            return []

    df_words["Answer"] = df_words.apply(define, axis=1)

    df_defined, df_undefined = df_words[(mask := df_words["Answer"].astype(bool))].copy(), df_words[~mask].copy()

    undefined_words = list(df_undefined["Text"])
    for word in undefined_words:
        logger.i(f"Defintion not found in wordnet: \"{word}\"")
    return df_defined

def words_to_anki_csv(df_words):
    df_words["Text"] = df_words["Text"].apply(lambda r: f"<h1>{r.capitalize()}</h1>")

    def anki_format(answer):
        lines_separator = "----------------------------------------"
        def _format(i, answer):
            answer_str = f"\n{lines_separator}"
            answer_str += f"<large> {i + 1} </large>"
            answer_str += f"{lines_separator}\n"
            answer_str += f"<em><b>\n{answer['Definition']}</b> - ({answer['Part of speech']})</em>"
            if examples := answer.get("Examples"):
                answer_str += "<small>"
                answer_str += f'<u>\n\nExamples:</u>\n'
                for example in examples:
                    answer_str += f"<em>\"{example}\"</em>\n"
                answer_str += "</small>"
            return answer_str
        answer_str = [_format(i, a) for i, a in enumerate(answer)]
        return f"\n".join(answer_str) + f"\n{lines_separator}---{lines_separator}"

    df_words["Answer"] = df_words["Answer"].apply(anki_format)
    return df_words

if __name__ == '__main__':
    args = argparser.argparser()
    kwargs = vars(args)
    logger.setup_info()
    with KoboDB(kwargs.get("kobo_db")) as conn:
        cursor = conn.cursor()
        #df_books = KoboDB.run_query(cursor, kwargs.get("sql_books_read"))
        df = KoboDB.run_query(cursor, kwargs.get("sql_extract_annotations"))

        df_words, df_quotes = df_split_words_quotes(df, **kwargs)

        write_quotes(df_quotes, **kwargs)

        df_words["Text"] = df_words["Text"].apply(clean_word)

        removed_rows = df_words[df_words.duplicated(subset=["Text"], keep=False)]
        logger.i(f"Duplicates dropped for: {list(removed_rows['Text'])}")
        df_words = df_words.drop_duplicates(subset=["Text"], keep='first')

        df_words = define_words(df_words)

        df_words = words_to_anki_csv(df_words)

        df_words[['Text', 'Answer']].to_csv("test.csv", index=False, header=False)
