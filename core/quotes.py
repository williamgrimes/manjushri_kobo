from datetime import datetime


def clean_quotes(df_quotes, **kwargs):
    df_quotes.sort_values(by=["DateLastRead"], inplace=True)
    replacers = {"\n": " ", "\r": " ", "\\xa0\\xa0\\xa0": " ", "  ": " "}
    df_quotes["Text"] = df_quotes["Text"].str.strip()
    df_quotes["Text"] = df_quotes["Text"].replace(replacers, regex=True)
    return df_quotes


def write_quotes_to_org(df_quotes, org_file, org_user, org_date, org_initial_visibility, **kwargs):
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


def main(df_quotes, **kwargs):
    df_quotes = clean_quotes(df_quotes)

    write_quotes_to_org(df_quotes, **kwargs)
