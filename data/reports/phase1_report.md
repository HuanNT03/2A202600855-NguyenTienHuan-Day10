# Phase 1 - Baseline ETL & Evaluation Report

## Source Ingestion Summary
- **API Source**: Crossref REST API
- **Query**: `agentic retrieval augmented generation large language model`
- **Filter**: `from-pub-date:2025-12-12,has-abstract:true`
- **Total Records Fetched**: 23

## Data Quality Check Results
- **Overall Status**: PASSED
- **At Least 5 Rows Check**: PASSED (Value: 23)
- **paper_id Check**: PASSED
- **Title Check**: PASSED
- **Summary Length Check**: PASSED
- **Freshness Check**: PASSED

## Freshness Report
- **Is Fresh**: YES
- **Latest Published**: 2026-06-02
- **Oldest Published**: 2025-12-19
- **Stale Rows Count**: 0
- **Total Rows**: 23

## Retrieval & QA Evaluation Metrics
- **Total Samples Evaluated**: 20
- **Retrieval Hit Rate**: 100.00%
- **Mean Token F1**: 75.00%
- **Judge Accuracy**: 75.00%
- **Mean Judge Score (1-5)**: 4.00
