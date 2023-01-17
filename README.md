# Manjushri Kobo

Mañjushri (Sanskrit: मञ्जुश्री) is a bodhisattva associated with prajñā
(wisdom) in Mahāyāna Buddhism. Manjushri is said to cut through ignorance and
personifies correct knowledge [^1].

This project is a tool for extracting annotations from Kobo ebooks;
organising the extracted annotations into word definitions and quotes. The aim
is to have an easily searchable file of quotations, and a system for
learning new vocabulary found in ebooks read on the Kobo.

Quotations are written to a structured Org file [^2], and single words are
extracted to a `.csv` with associated definitions, ready for import into an
Anki flash card deck [^3]. In this way when reading and finding unfamiliar
vocabulary one can learn that vocabulary using Anki.

The project works with a Kobo Clara HD [^4], but should work equally with any
Kobo that uses a sqlite database located here:

```
/media/${USER}/KOBOeReader/.kobo/KoboReader.sqlite
```

### Quotes

Quotes are annotated text that are longer than three words in length, they
are sections of a book that can be refered back to, and are extracted to a
`.org` file structured into sections for each book.

### Words
Single annotated words are usually unfamiliar vocabulary that can be annotated,
the word is extracted and NLTK wordnet used to find the definition,
part of speech and examples. This is then exported to a csv where the first
field is the front of an Anki flashcard and the second field the back. The
file can then be imported into an Anki deck.

## Installation

To run this project create a virtual environment and install the required
libraries from the `requirements.txt` as follows.

```bash
/usr/bin/python3.11 -m venv manjushri_kobo
source manjushri_kobo/bin/activate
pip install -r requirements.txt
```

## Usage

The entrypoint for this project is the `main.py` which can be called specifying
the kobo database, output org file location, and anki file, as follows:

```bash
python3.11 -m main \
    --kobo_db </path/to/kobo.sqlite> \
    --org_file </path/to/org_file> \
    --anki_csv </path/to/anki_csv>
```

```bash
bash run_manjushri_kobo.sh
```

The script will then extract all annotations, split them into words and quotes,
and look up the words in a dictionary.  Quotes will be extracted to an org file.

## Dependencies
 + Python 3.11
 + NLTK
 + NLTK - WordNet
 + Pandas

Make sure to install the dependencies before running the script.

## Credits
Developed by William Grimes

## References

[^1]: https://en.wikipedia.org//wiki/Manjushri
[^2]: https://orgmode.org/
[^3]: https://apps.ankiweb.net/
[^4]: https://en.wikipedia.org/wiki/Kobo_eReader#Kobo_Clara_HD
