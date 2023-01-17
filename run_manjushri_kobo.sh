#!/bin/bash

PROJECT_DIR="Projects/manjushri_kobo"

cd "$HOME"/$PROJECT_DIR/

source "$HOME"/.virtualenvs/manjushri_kobo_env/bin/activate

python -m main \
    --kobo_db "/media/${USER}/KOBOeReader/.kobo/KoboReader.sqlite" \
    --org_file "${HOME}/Org/book-annotations.org" \
    --anki_csv "anki_vocabulary.csv"
