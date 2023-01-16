"""Extract quotes and write to an org-file."""

from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd

from core.logs import ProjectLogger

logger = ProjectLogger(__name__)


def clean_quotes(df_quotes: pd.DataFrame) -> pd.DataFrame:
    """
    Clean quote strings and sort quotes by DateLastRead

    Parameters:
    df_quotes (pd.DataFrame): The quotes dataframe to be cleaned
    kwargs: Additional keyword arguments

    Returns:
    pd.DataFrame : cleaned and sorted quotes dataframe
    """
    special_chars = {"\n": " ",
                     "\r": " ",
                     "\\xa0\\xa0\\xa0": " ",
                     "  ": " ",
                     }
    logger.i(
        f"Stripping whitespace and replacing special characters {special_chars=}.")
    df_quotes["Text"] = df_quotes["Text"].pipe(
        lambda x: x.str.strip()).replace(
        special_chars, regex=True)
    df_quotes.sort_values(by="DateLastRead", inplace=True)
    return df_quotes


def write_quotes_to_org(
        df_quotes: pd.DataFrame,
        org_file: Path,
        org_title: str,
        org_user: str,
        org_date: str,
        org_initial_visibility: str,
        **kwargs: Dict) -> None:
    """
    Write quotes to an .org file for viewing
    https://orgmode.org/

    Parameters:
    df_quotes (pd.DataFrame): The quotes dataframe to be cleaned
    org_file (Path): Path to org file
    org_title (str): Org header - Title for org-file
    org_user (str): Org header - Username / Author of org-file
    org_date (str): Date string for org-file header
    org_initial_visibility (str): Folded / Children / Sub-Tree
    kwargs: Additional keyword arguments

    Returns:
    None : Writes to a file
    """
    group_cols = ["DateLastRead", "Title", "Attribution"]
    df_grp = df_quotes.groupby(group_cols)
    logger.i(f"Writing to {org_file=}")
    with open(org_file, 'w') as f:
        f.write(f"#+TITLE: {org_title}")
        logger.i(f"Org-file {org_title=}")
        f.write(f"\n#+AUTHOR: {org_user}")
        logger.d(f"Org-file {org_user=}")
        f.write(f"\n#+DATE: {org_date}")
        logger.d(f"Org-file {org_date=}")
        f.write(f"\n#+STARTUP: {org_initial_visibility}\n")
        logger.d(f"Org-file {org_initial_visibility=}")
        for group_name, df_group in df_grp:
            group_info = dict(zip(group_cols, group_name))
            title = group_info.get("Title")
            author = group_info.get("Attribution")
            date = datetime.fromisoformat(
                group_info.get('DateLastRead')).strftime("%Y-%m:%d")
            f.write(f"\n* {title}")
            f.write(f"\n:PROPERTIES:")
            f.write(f"\n:AUTHOR {author}")
            f.write(f"\n:DATE LAST READ: {date}")
            f.write(f"\n:END:")

            for index, row in df_group.iterrows():
                f.write(f"\n + /\"{row.Text}/\"\n")  # write quote to file
            logger.i(
                f"--- {len(df_group)} quotes written for: {title} - {author}")
    return None


def main(df_quotes, **kwargs):

    logger.i(f"PROCESSING QUOTES")

    df_quotes = clean_quotes(df_quotes)

    write_quotes_to_org(df_quotes, **kwargs)
