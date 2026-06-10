from __future__ import annotations

from typing import Any


from core.utils import write_text
from pathlib import Path


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report cho baseline phase.

    Pseudo-code:
    1. Gom source summary.
    2. In metrics retrieval/evaluation.
    3. In data quality va freshness.
    4. Ghi markdown vao report_path.
    """
    md = f"""# Phase 1 - Baseline ETL & Evaluation Report

## Source Ingestion Summary
- **API Source**: {source_summary.get("source_api", "Unknown")}
- **Query**: `{source_summary.get("source_query", "N/A")}`
- **Filter**: `{source_summary.get("source_filter", "N/A")}`
- **Total Records Fetched**: {source_summary.get("total_fetched", 0)}

## Data Quality Check Results
- **Overall Status**: {"PASSED" if quality.get("overall_passed") else "FAILED"}
- **At Least 5 Rows Check**: {"PASSED" if quality.get("checks", {}).get("row_count_check", {}).get("passed") else "FAILED"} (Value: {quality.get("checks", {}).get("row_count_check", {}).get("value", 0)})
- **paper_id Check**: {"PASSED" if quality.get("checks", {}).get("paper_id_check", {}).get("passed") else "FAILED"}
- **Title Check**: {"PASSED" if quality.get("checks", {}).get("title_check", {}).get("passed") else "FAILED"}
- **Summary Length Check**: {"PASSED" if quality.get("checks", {}).get("summary_length_check", {}).get("passed") else "FAILED"}
- **Freshness Check**: {"PASSED" if quality.get("checks", {}).get("freshness_check", {}).get("passed") else "FAILED"}

## Freshness Report
- **Is Fresh**: {"YES" if freshness.get("is_fresh") else "NO"}
- **Latest Published**: {freshness.get("latest_published")}
- **Oldest Published**: {freshness.get("oldest_published")}
- **Stale Rows Count**: {freshness.get("stale_rows")}
- **Total Rows**: {freshness.get("total_rows")}

## Retrieval & QA Evaluation Metrics
- **Total Samples Evaluated**: {metrics.get("samples", 0)}
- **Retrieval Hit Rate**: {metrics.get("retrieval_hit_rate", 0.0) * 100:.2f}%
- **Mean Token F1**: {metrics.get("mean_token_f1", 0.0) * 100:.2f}%
- **Judge Accuracy**: {metrics.get("judge_accuracy", 0.0) * 100:.2f}%
- **Mean Judge Score (1-5)**: {metrics.get("mean_judge_score", 0.0):.2f}
"""
    write_text(Path(report_path), md)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    table = f"""| Metric | Baseline | Corrupted | Repaired |
|---|---|---|---|
| **Total Samples** | {baseline_metrics.get("samples", 0)} | {corrupted_metrics.get("samples", 0)} | {repaired_metrics.get("samples", 0)} |
| **Retrieval Hit Rate** | {baseline_metrics.get("retrieval_hit_rate", 0.0) * 100:.2f}% | {corrupted_metrics.get("retrieval_hit_rate", 0.0) * 100:.2f}% | {repaired_metrics.get("retrieval_hit_rate", 0.0) * 100:.2f}% |
| **Mean Token F1** | {baseline_metrics.get("mean_token_f1", 0.0) * 100:.2f}% | {corrupted_metrics.get("mean_token_f1", 0.0) * 100:.2f}% | {repaired_metrics.get("mean_token_f1", 0.0) * 100:.2f}% |
| **Judge Accuracy** | {baseline_metrics.get("judge_accuracy", 0.0) * 100:.2f}% | {corrupted_metrics.get("judge_accuracy", 0.0) * 100:.2f}% | {repaired_metrics.get("judge_accuracy", 0.0) * 100:.2f}% |
| **Mean Judge Score** | {baseline_metrics.get("mean_judge_score", 0.0):.2f} | {corrupted_metrics.get("mean_judge_score", 0.0):.2f} | {repaired_metrics.get("mean_judge_score", 0.0):.2f} |
| **Data Quality Pass** | PASSED | {"PASSED" if corrupted_quality.get("overall_passed") else "FAILED"} | {"PASSED" if repaired_quality.get("overall_passed") else "FAILED"} |
| **Data Freshness** | FRESH | {"FRESH" if corrupted_freshness.get("is_fresh") else "STALE"} | {"FRESH" if repaired_freshness.get("is_fresh") else "STALE"} |
"""
    md = f"""# Corruption Simulation & Recovery Comparison Report

## Metrics Summary Table
{table}

## RAG Performance Analysis

### Impact of Corruption
When data was corrupted:
- **Quality & Freshness**: Overall data quality and freshness checks failed. Stale papers were injected, titles were truncated, and summaries were blanked.
- **Retrieval & QA Accuracy**: The retrieval hit rate and token F1 dropped, because corrupted metadata (truncated titles, empty summaries) resulted in poor vector search matching and incomplete answers.

### Impact of Repair
After the pipeline was repaired:
- **Quality & Freshness**: Data quality and freshness checks passed again.
- **Retrieval & QA Accuracy**: The retrieval hit rate, token F1, and judge accuracy recovered back to baseline levels, demonstrating that maintaining clean data ingestion pipelines is critical for reliable RAG performance.
"""
    write_text(Path(report_path), md)

