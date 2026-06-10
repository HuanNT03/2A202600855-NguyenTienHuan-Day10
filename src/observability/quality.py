from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


from core.utils import write_json
from pathlib import Path


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """TODO(student): tao bo data quality checks.

    Pseudo-code:
    1. Check row count.
    2. Check `paper_id` not null va unique.
    3. Check `title` not null.
    4. Check do dai `summary`.
    5. Check freshness bang `age_days`.
    6. Ghi ket qua vao `data/quality/`.
    """
    row_count = len(df)
    row_count_ok = row_count >= 5
    
    paper_id_not_null = df["paper_id"].notnull().all() if row_count > 0 else True
    paper_id_not_empty = ((df["paper_id"].str.strip() != "").all()) if row_count > 0 else True
    paper_id_unique = df["paper_id"].is_unique if row_count > 0 else True
    paper_id_ok = bool(paper_id_not_null and paper_id_not_empty and paper_id_unique)
    
    title_ok = bool(df["title"].notnull().all() and (df["title"].str.strip() != "").all()) if row_count > 0 else True
    summary_chars_ok = bool((df["summary_chars"] >= 10).all()) if row_count > 0 else True
    freshness_ok = bool((df["age_days"] <= settings.freshness_threshold_days).all()) if row_count > 0 else True
    
    overall_passed = bool(row_count_ok and paper_id_ok and title_ok and summary_chars_ok and freshness_ok)
    
    report = {
        "report_name": report_name,
        "overall_passed": overall_passed,
        "checks": {
            "row_count_check": {
                "description": "At least 5 rows present",
                "passed": row_count_ok,
                "value": row_count
            },
            "paper_id_check": {
                "description": "paper_id not null, not empty, and unique",
                "passed": paper_id_ok,
                "unique": paper_id_unique,
                "not_null_or_empty": bool(paper_id_not_null and paper_id_not_empty)
            },
            "title_check": {
                "description": "title not null and not empty",
                "passed": title_ok
            },
            "summary_length_check": {
                "description": "summary length >= 10 characters",
                "passed": summary_chars_ok
            },
            "freshness_check": {
                "description": f"all papers age_days <= {settings.freshness_threshold_days}",
                "passed": freshness_ok
            }
        }
    }
    
    write_json(settings.paths.quality_dir / f"{report_name}.json", report)
    return report


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """TODO(student): tong hop freshness report.

    Pseudo-code:
    1. Tim latest va oldest published date.
    2. Dem so dong stale.
    3. Tao payload:
       - latest_published
       - oldest_published
       - stale_rows
       - total_rows
       - is_fresh
    4. Ghi JSON report.
    """
    if len(df) == 0:
        report = {
            "latest_published": "N/A",
            "oldest_published": "N/A",
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": True
        }
    else:
        latest_published = str(df["published"].max())
        oldest_published = str(df["published"].min())
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
        total_rows = len(df)
        is_fresh = stale_rows == 0
        
        report = {
            "latest_published": latest_published,
            "oldest_published": oldest_published,
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": is_fresh
        }
        
    write_json(Path(report_path), report)
    return report

