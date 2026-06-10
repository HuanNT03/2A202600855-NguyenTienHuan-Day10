from __future__ import annotations


import pandas as pd
from core.config import load_settings
from core.utils import now_utc, read_json
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report
from retrieval.agent import build_agent, run_agent_question
from pathlib import Path


def main() -> None:
    """TODO(student): xay dung baseline pipeline end-to-end.

    Pseudo-code:
    1. Load settings.
    2. Load hoac fetch raw records.
    3. Clean data.
    4. Save clean CSV/JSON.
    5. Build Chroma index.
    6. Tao hoac load evaluation set.
    7. Evaluate.
    8. Run quality checks va freshness report.
    9. Tao markdown report.
    10. Co the demo agent tren vai sample question.
    """
    # 1. Load settings
    settings = load_settings()
    run_date = now_utc()

    # 2. Load or fetch raw records
    raw_records_path = settings.paths.raw_records_json
    if settings.refresh_source or not raw_records_path.exists():
        print("Fetching fresh records from Crossref API...")
        records = fetch_source_records(settings)
    else:
        print("Loading raw records from snapshot...")
        records = load_raw_records(raw_records_path)

    # 3. Clean data
    df = build_clean_dataframe(records, run_date)

    # 4. Save clean CSV/JSON
    df.to_csv(settings.paths.clean_csv, index=False)
    df.to_json(settings.paths.clean_json, orient="records", indent=2)

    # 5. Build Chroma index
    print("Building local embedding index...")
    index = LocalEmbeddingIndex.build(df, settings, settings.paths.embeddings_json)

    # 6. Build or load evaluation set
    testset_path = settings.paths.eval_testset
    if settings.refresh_test_set or not testset_path.exists():
        print("Building new evaluation set...")
        test_set = build_test_set(df, testset_path)
    else:
        print("Loading existing evaluation set...")
        test_set = read_json(testset_path)

    # 7. Evaluate
    print("Evaluating baseline pipeline...")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=testset_path,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers
    )

    # 8. Run quality checks and freshness report
    print("Running quality checks and freshness report...")
    quality_report = run_data_quality_checks(df, settings, "baseline_quality")
    freshness_report = build_freshness_report(df, settings, settings.paths.freshness_report)

    # 9. Create markdown report
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "source_filter": settings.source_filter,
        "total_fetched": len(records)
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=eval_bundle.summary,
        quality=quality_report,
        freshness=freshness_report
    )

    # 10. Demo agent
    if len(df) > 0:
        try:
            print("Initializing and running Agent demo...")
            agent = build_agent(settings, index)
            sample_q = f"What is the summary of the paper '{df.iloc[0]['title']}'?"
            response = run_agent_question(agent, sample_q)
            print(f"Question: {sample_q}")
            print(f"Agent response: {response}")
        except Exception as e:
            print(f"Skipping agent demo due to LLM provider exception or credentials issue: {e}")

    print("Baseline phase 1 pipeline completed successfully!")

