# Results Folder Index

## 1. Core Grading Artifacts

- `best_summary.csv`
  - Final best metrics for trend following, mean reversion, and buy-and-hold.

- `trend_results.csv`
  - Full 10x10 optimization table for trend following.

- `mean_results.csv`
  - Full 10x10 optimization table for mean reversion.

- `trend_sharpe_heatmap.png`
  - Heatmap of Sharpe values over trend strategy parameter grid.

- `mean_sharpe_heatmap.png`
  - Heatmap of Sharpe values over mean reversion parameter grid.
  - Gray cells indicate undefined Sharpe (no trades/zero variance), not a plotting error.

- `equity_curves.png`
  - Equity curve comparison for best trend, best mean, and buy-and-hold.

## 2. Data Transparency Artifacts

- `data_diagnostics.csv`
  - Which ticker was used, row count, date range, min/max close.

- `data_head.csv`
  - First 10 rows of prepared data used in backtesting.

- `data_tail.csv`
  - Last 10 rows of prepared data used in backtesting.

## 3. Debug/Inspection Artifacts (Optional, Not Required for Grading)
These files were created during validation/debugging and are not required for assignment grading:

- `debug/inspect_2026-03-28.csv`
- `debug/inspect_2026-03-29.csv`
- `debug/inspect_none.csv`
- `debug/inspect_summary.csv`
- `debug/inspect_tickers_summary.csv`
- `debug/inspect_XU030_IS.csv`
- `debug/inspect_XU050_IS.csv`
- `debug/inspect_XU100_IS.csv`
- `debug/inspect_XUTUM_IS.csv`
- `debug/inspect__XU100.csv`

## 4. Quick Integrity Notes

- Core optimization files should show 100 rows each for trend and mean grids.
- `best_summary.csv` values should match best rows from each full grid.
- Mean heatmap gray top rows correspond to NaN Sharpe in `mean_results.csv` for n=9 and n=10.
