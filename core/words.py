import string

from nltk import WordNetLemmatizer
from nltk.corpus import wordnet

from main import logger


def clean_words(df_words):
    def word_cleaner(words_string: str) -> str:
        """Clean words, remove punctuation, make lowercase, and Lemmatize to."""
        words_string = words_string.lower()

        # Create a translation table to remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        words_string = words_string.translate(translator)

        lemmatizer = WordNetLemmatizer()
        lemmatized_word = lemmatizer.lemmatize(words_string)

        word = lemmatized_word.strip()

        return word

    df_words["Text"] = df_words["Text"].apply(word_cleaner)

    removed_rows = df_words[df_words.duplicated(subset=["Text"], keep=False)]
    logger.i(f"Duplicates dropped for: {list(removed_rows['Text'])}")
    df_words = df_words.drop_duplicates(subset=["Text"], keep='first')

    return df_words


def define_words(df_words):
    pos_map = {
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
                     "Part of speech": pos_map.get(s.pos()),
                     "Examples": [e.capitalize() for e in s.examples()],
                     } for s in synsets]
        else:
            logger.i(f"\"{word}\" - definition not found.")
            return []

    df_words = df_words.copy()
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
    df_words[['Text', 'Answer']].to_csv("test.csv", index=False, header=False)

def main(df_words, **kwargs):
    df_words = clean_words(df_words)

    df_words = define_words(df_words)

    words_to_anki_csv(df_words)
