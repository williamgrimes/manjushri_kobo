"""Argument paser for project"""
import argparse
import os

from datetime import datetime
from pathlib import Path


def argparser():
    """Argument paser for project"""
    parser = argparse.ArgumentParser(
        description="Kobo Extract Annotations.")
    parser.add_argument("--kobo_db",
                        type=str,
                        help="Path to kobo sqlite database KoboReader.sqlite")
    parser.add_argument("--logs_dir",
                        default="logs/",
                        type=str,
                        help="Folder containing project logs.")
    parser.add_argument("--max_word_len",
                        default=2,
                        type=int,
                        help="Number of words to differentiate a quote form words.")
    parser.add_argument("--sql_extract_annotations",
                        default="sql/extract_annotations.sql",
                        type=str,
                        help="Path to sql query returning annotations.")
    parser.add_argument("--org_file",
                        type=Path,
                        help="Path to output book annotations..")
    parser.add_argument("--org_title",
                        default="Book Annotations",
                        type=str,
                        help="Title of the Org file..")
    parser.add_argument("--org_user",
                        default=os.environ.get('USER'),
                        type=str,
                        help="Name to add to header of org file.")
    parser.add_argument("--org_date",
                        default=datetime.now().strftime("%Y-%m-%d"),
                        type=str,
                        help="Name to add to header of org file.")
    parser.add_argument("--org_initial_visibility",
                        default="fold",
                        type=str,
                        help="Visibility of org-file.")
    parser.add_argument("--anki_csv",
                        default="anki_vocabulary.csv",
                        type=Path,
                        help="Path to anki csv output.")
    return parser.parse_args()
