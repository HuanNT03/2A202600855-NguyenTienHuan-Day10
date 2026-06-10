from __future__ import annotations

from typing import Any

import pandas as pd


from core.utils import first_sentence, write_json
from pathlib import Path


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """TODO(student): tao bo evaluation set tu cleaned dataframe.

    Pseudo-code:
    1. Kiem tra so luong document toi thieu.
    2. Chon mot so paper dai dien.
    3. Tao nhieu loai cau hoi:
       - summary
       - authors
       - date
       - categories
    4. Moi row can co:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Ghi file JSON vao output_path.
    """
    if len(df) < 1:
        raise ValueError("Cleaned dataframe is empty; cannot build a test set.")

    # Select representative papers (up to 5)
    num_papers = min(5, len(df))
    selected_papers = df.head(num_papers).to_dict(orient="records")

    test_set = []
    question_counter = 1

    for row in selected_papers:
        paper_id = row["paper_id"]
        title = row["title"]
        authors_joined = row["authors_joined"]
        categories_joined = row["categories_joined"]
        published = row["published"]
        summary = row["summary"]

        # 1. Summary question
        test_set.append({
            "id": f"q_{question_counter:03d}",
            "question_type": "summary",
            "question": f"What is the summary of the paper '{title}'?",
            "ground_truth": first_sentence(summary),
            "ground_truth_doc_ids": [paper_id]
        })
        question_counter += 1

        # 2. Authors question
        test_set.append({
            "id": f"q_{question_counter:03d}",
            "question_type": "authors",
            "question": f"Who authored the paper '{title}'?",
            "ground_truth": authors_joined,
            "ground_truth_doc_ids": [paper_id]
        })
        question_counter += 1

        # 3. Date question
        test_set.append({
            "id": f"q_{question_counter:03d}",
            "question_type": "date",
            "question": f"When was the paper '{title}' published?",
            "ground_truth": published,
            "ground_truth_doc_ids": [paper_id]
        })
        question_counter += 1

        # 4. Categories question
        test_set.append({
            "id": f"q_{question_counter:03d}",
            "question_type": "categories",
            "question": f"What categories are associated with the paper '{title}'?",
            "ground_truth": categories_joined,
            "ground_truth_doc_ids": [paper_id]
        })
        question_counter += 1

    write_json(Path(output_path), test_set)
    return test_set

