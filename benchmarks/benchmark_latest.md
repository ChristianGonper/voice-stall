# Benchmark Report

- Timestamp: `2026-02-27T20:37:40`
- Iterations: `2000`

## Dictation Service (orchestrator overhead)
- Mean: `0.001 ms`
- Median: `0.001 ms`
- P95: `0.001 ms`

## Dictionary Apply
- Mean: `0.005 ms`
- Median: `0.005 ms`
- P95: `0.005 ms`

## Notes
- `dictation_service` should stay near-zero; any growth indicates orchestration regressions.
- `dictionary_apply` should remain sub-millisecond; growth suggests regex bloat.
- Compare this file across commits for trend tracking.
