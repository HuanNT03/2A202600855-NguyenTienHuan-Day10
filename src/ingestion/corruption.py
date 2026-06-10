from __future__ import annotations

import pandas as pd


from core.utils import write_json
from pathlib import Path


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    corrupted_df = df.copy()
    log = []
    
    # 1. Drop a few latest records
    dropped_papers = []
    if len(corrupted_df) > 3:
        dropped_papers = corrupted_df.head(3)["paper_id"].tolist()
        corrupted_df = corrupted_df.iloc[3:].reset_index(drop=True)
        log.append({
            "corruption_type": "deletion",
            "description": f"Dropped {len(dropped_papers)} latest records",
            "paper_ids": dropped_papers
        })
        
    # Check if we still have rows
    if len(corrupted_df) > 0:
        # 2. Blank summary of some rows
        idx_blank = 0
        paper_id_blank = corrupted_df.loc[idx_blank, "paper_id"]
        corrupted_df.loc[idx_blank, "summary"] = ""
        corrupted_df.loc[idx_blank, "summary_chars"] = 0
        log.append({
            "corruption_type": "blank_summary",
            "description": "Blanked summary of paper",
            "paper_id": paper_id_blank
        })
        
    if len(corrupted_df) > 1:
        # 3. Inject noise into summary
        idx_noise = 1
        paper_id_noise = corrupted_df.loc[idx_noise, "paper_id"]
        corrupted_df.loc[idx_noise, "summary"] += " !!!CORRUPTED_GIBBERISH_DATA_12345!!!"
        corrupted_df.loc[idx_noise, "summary_chars"] = len(corrupted_df.loc[idx_noise, "summary"])
        log.append({
            "corruption_type": "noise_summary",
            "description": "Injected noise into summary of paper",
            "paper_id": paper_id_noise
        })
        
    if len(corrupted_df) > 2:
        # 4. Truncate title
        idx_trunc = 2
        paper_id_trunc = corrupted_df.loc[idx_trunc, "paper_id"]
        corrupted_df.loc[idx_trunc, "title"] = corrupted_df.loc[idx_trunc, "title"][:10]
        log.append({
            "corruption_type": "truncate_title",
            "description": "Truncated title to 10 characters",
            "paper_id": paper_id_trunc
        })
        
    if len(corrupted_df) > 3:
        # 5. Stale published date
        idx_stale = 3
        paper_id_stale = corrupted_df.loc[idx_stale, "paper_id"]
        corrupted_df.loc[idx_stale, "published"] = "2010-01-01"
        corrupted_df.loc[idx_stale, "age_days"] = 6000
        log.append({
            "corruption_type": "stale_published",
            "description": "Set published date to 2010-01-01 (stale)",
            "paper_id": paper_id_stale
        })
        
    if len(corrupted_df) > 4:
        # 6. Add duplicate rows
        dup_row = corrupted_df.iloc[[4]]
        corrupted_df = pd.concat([corrupted_df, dup_row], ignore_index=True)
        log.append({
            "corruption_type": "duplicate_rows",
            "description": "Duplicated record",
            "paper_id": dup_row["paper_id"].values[0]
        })
        
    # 7. Rebuild text_for_embedding
    corrupted_df["text_for_embedding"] = corrupted_df.apply(
        lambda r: f"Title: {r['title']}\nAuthors: {r['authors_joined']}\nCategories: {r['categories_joined']}\nSummary: {r['summary']}",
        axis=1
    )
    
    # 8. Write log
    write_json(Path(output_log_path), log)
    return corrupted_df

