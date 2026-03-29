# Executive Summary (For Grading)

## 1. What Was Done
This submission implements and evaluates two BIST100 strategies in Python using Backtrader:

1. Trend Following
2. Mean Reversion (Contrarian)

Work completed:

- Daily data download from yfinance
- Daily return calculation
- Two separate Backtrader strategy classes
- Full 10x10 grid search for each strategy (100 runs each)
- Metrics for every run: total return, annualized return, volatility, Sharpe ratio, max drawdown
- Best-parameter selection and cross-strategy comparison
- CSV and PNG output generation + written reports

## 2. Core Findings
Best parameters:

- Trend Following: n=4, m=6, Sharpe=1.058
- Mean Reversion: n=1, m=10, Sharpe=0.937

Comparison result:

- Trend Following outperforms Mean Reversion on Sharpe ratio.
- Trend Following also has lower drawdown than Mean Reversion and Buy & Hold.

Answer to assignment question:

- In this tested sample, being a trend follower is better than being a contrarian.

## 3. Important Clarification
The assignment ticker is `^XU100`. Due to sparse long-history availability in yfinance for that symbol, code attempts `^XU100` first and falls back to `XU100.IS` when needed.

Latest run used: `XU100.IS` (recorded in `results/data_diagnostics.csv`).

## 4. Why Mean-Reversion Heatmap Has Gray Upper Region
This is expected, not an error.

- NaN Sharpe cells: 20
- Region: n=9 and n=10 (all m)

These parameter settings produce no effective trades / zero return variance in this sample, so Sharpe is undefined.

## 5. Files to Grade First
Recommended order:

1. `assignment1_bist100.py` (implementation)
2. `results/best_summary.csv` (final metrics)
3. `results/trend_results.csv` and `results/mean_results.csv` (full grids)
4. `results/trend_sharpe_heatmap.png`, `results/mean_sharpe_heatmap.png`, `results/equity_curves.png`
5. `short_report.md` and `docs/REPORT.md`

## 6. Requirement Coverage Checklist
- Data from yfinance: Yes
- Daily returns: Yes
- Two strategy classes: Yes
- Grid search n=1..10, m=1..10: Yes
- All parameter combinations backtested: Yes
- Required metrics per run: Yes
- Best (n,m) selected per strategy: Yes
- Final strategy comparison and conclusion: Yes
