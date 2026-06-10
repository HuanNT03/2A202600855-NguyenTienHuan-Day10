from __future__ import annotations


import pandas as pd
from core.config import load_settings
from core.utils import now_utc, read_json
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report


def main() -> None:
    """TODO(student): xay dung corruption -> evaluate -> repair -> compare flow.

    Pseudo-code:
    1. Load baseline metrics va clean dataset.
    2. Tao corrupted dataframe.
    3. Save corrupted artifacts.
    4. Rebuild index va evaluate.
    5. Run quality checks/freshness tren corrupted data.
    6. Repair lai tu raw records.
    7. Evaluate repaired dataset.
    8. Tao comparison report.
    """
    # 1. Load settings and baseline metrics
    settings = load_settings()
    run_date = now_utc()
    
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    baseline_df = pd.read_json(settings.paths.clean_json)

    # 2. Corrupt baseline data
    print("Corrupting baseline data...")
    corrupted_df = corrupt_clean_dataframe(baseline_df, settings.paths.corruption_log)

    # 3. Save corrupted artifacts
    corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)

    # 4. Rebuild index and evaluate corrupted data
    print("Building corrupted embedding index...")
    corrupted_index = LocalEmbeddingIndex.build(corrupted_df, settings, settings.paths.corrupted_embeddings_json)
    
    print("Evaluating corrupted pipeline...")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers
    )

    # 5. Run quality checks / freshness report on corrupted data
    print("Running quality and freshness checks on corrupted data...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(
        corrupted_df, 
        settings, 
        settings.paths.quality_dir / "corrupted_freshness_report.json"
    )

    # 6. Repair data by loading and re-cleaning raw records
    print("Repairing data from original raw records snapshot...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, run_date)
    
    repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)

    # 7. Evaluate repaired dataset
    print("Building repaired embedding index...")
    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, settings.paths.repaired_embeddings_json)
    
    print("Evaluating repaired pipeline...")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers
    )

    print("Running quality and freshness checks on repaired data...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(
        repaired_df, 
        settings, 
        settings.paths.quality_dir / "repaired_freshness_report.json"
    )

    # 8. Create comparison report
    print("Generating comparison report...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness
    )
    
    print("Corruption and repair flow pipeline completed successfully!")
    print(f"Baseline F1: {baseline_metrics['mean_token_f1']*100:.2f}%")
    print(f"Corrupted F1: {corrupted_bundle.summary['mean_token_f1']*100:.2f}%")
    print(f"Repaired F1: {repaired_bundle.summary['mean_token_f1']*100:.2f}%")

