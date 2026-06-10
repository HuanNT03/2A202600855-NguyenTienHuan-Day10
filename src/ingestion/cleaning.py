from __future__ import annotations

from datetime import datetime

import pandas as pd

from ingestion.crossref import PaperRecord


from core.utils import normalize_whitespace, compact_join


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """TODO(student): clean raw records thanh dataframe san sang de embed.

    Pseudo-code:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    if not records:
        cols = [
            "paper_id", "title", "summary", "authors", "categories", 
            "primary_category", "published", "updated", "abs_url", 
            "pdf_url", "comment", "authors_joined", "categories_joined", 
            "summary_chars", "text_for_embedding", "age_days"
        ]
        return pd.DataFrame(columns=cols)

    data = [r.__dict__ for r in records]
    df = pd.DataFrame(data)

    # 1. Normalize
    df["title"] = df["title"].apply(lambda x: normalize_whitespace(x) if isinstance(x, str) else "")
    df["summary"] = df["summary"].apply(lambda x: normalize_whitespace(x) if isinstance(x, str) else "")
    df["authors"] = df["authors"].apply(lambda lst: [normalize_whitespace(a) for a in lst if a] if isinstance(lst, list) else [])
    df["categories"] = df["categories"].apply(lambda lst: [normalize_whitespace(c) for c in lst if c] if isinstance(lst, list) else [])
    
    # 2. Parse dates & 3. calculate age_days
    def to_date(d_str):
        try:
            return pd.to_datetime(d_str).date()
        except Exception:
            return run_date.date()

    df["published_date"] = df["published"].apply(to_date)
    df["age_days"] = df["published_date"].apply(lambda d: (run_date.date() - d).days)
    df["published"] = df["published_date"].apply(lambda d: d.isoformat())
    df["updated"] = df["updated"].apply(lambda d: to_date(d).isoformat())
    df = df.drop(columns=["published_date"])

    # 4. Helper columns
    df["authors_joined"] = df["authors"].apply(lambda lst: compact_join(lst, sep=", "))
    df["categories_joined"] = df["categories"].apply(lambda lst: compact_join(lst, sep=", "))
    df["summary_chars"] = df["summary"].apply(len)
    df["text_for_embedding"] = df.apply(
        lambda r: f"Title: {r['title']}\nAuthors: {r['authors_joined']}\nCategories: {r['categories_joined']}\nSummary: {r['summary']}",
        axis=1
    )

    # 5. Drop duplicates and filter bad records
    df = df.drop_duplicates(subset=["paper_id"], keep="first")
    df = df[
        (df["paper_id"].str.strip() != "") & 
        (df["title"].str.strip() != "") & 
        (df["summary"].str.strip() != "")
    ]

    # 6. Sort
    df = df.sort_values(by=["published", "title"], ascending=[False, True]).reset_index(drop=True)
    return df

