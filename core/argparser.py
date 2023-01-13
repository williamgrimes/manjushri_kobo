"""Argument paser for project"""
import argparse
import os

from datetime import datetime


def argparser():
    """Argument paser for project"""
    parser = argparse.ArgumentParser(
        description="Kobo Extract Annotations.")
    parser.add_argument("--kobo_db",
                        type=str,
                        help="path to kobo sqlite database KoboReader.sqlite")
    parser.add_argument("--logs_dir",
                        default="logs/",
                        type=str,
                        help="folder containing logs.")
    parser.add_argument("--max_word_len",
                        default=2,
                        type=int,
                        help="number of words to differentiate a quote.")
    parser.add_argument("--sql_books_read",
                        default="sql/books_read.sql",
                        type=str,
                        help="path to sql query returning books read.")
    parser.add_argument("--sql_extract_annotations",
                        default="sql/extract_annotations.sql",
                        type=str,
                        help="path to sql query returning annotations.")
    parser.add_argument("--org_file",
                        type=str,
                        help="path to output book annotations..")
    parser.add_argument("--org_user",
                        default=os.environ.get('USER'),
                        help="Name to add to header of org file.")
    parser.add_argument("--org_date",
                        default=datetime.now().strftime("%Y-%m-%d"),
                        help="Name to add to header of org file.")
    parser.add_argument("--org_initial_visibility",
                        default="fold",
                        help="Visibility of org-file.")
    return parser.parse_args()
