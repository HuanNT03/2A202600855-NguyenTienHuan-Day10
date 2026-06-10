# Corruption Simulation & Recovery Comparison Report

## Metrics Summary Table
| Metric | Baseline | Corrupted | Repaired |
|---|---|---|---|
| **Total Samples** | 20 | 20 | 20 |
| **Retrieval Hit Rate** | 100.00% | 40.00% | 100.00% |
| **Mean Token F1** | 75.00% | 27.45% | 75.00% |
| **Judge Accuracy** | 75.00% | 25.00% | 75.00% |
| **Mean Judge Score** | 4.00 | 2.00 | 4.00 |
| **Data Quality Pass** | PASSED | FAILED | PASSED |
| **Data Freshness** | FRESH | STALE | FRESH |


## RAG Performance Analysis

### Impact of Corruption
When data was corrupted:
- **Quality & Freshness**: Overall data quality and freshness checks failed. Stale papers were injected, titles were truncated, and summaries were blanked.
- **Retrieval & QA Accuracy**: The retrieval hit rate and token F1 dropped, because corrupted metadata (truncated titles, empty summaries) resulted in poor vector search matching and incomplete answers.

### Impact of Repair
After the pipeline was repaired:
- **Quality & Freshness**: Data quality and freshness checks passed again.
- **Retrieval & QA Accuracy**: The retrieval hit rate, token F1, and judge accuracy recovered back to baseline levels, demonstrating that maintaining clean data ingestion pipelines is critical for reliable RAG performance.
