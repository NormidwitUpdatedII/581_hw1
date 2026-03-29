# BIST100 Assignment 1 - README

## Assignment Objective
Trade idea:

Test two simple trading strategies on BIST100 using Python.

Data requirement:

- Use daily data for BIST100 index (ticker: `^XU100`) from yfinance.
- Calculate daily returns.

Strategies:

1. Trend Following Strategy
   - Buy after `n` consecutive days of positive returns.
   - Sell after `m` consecutive days of negative returns.

2. Mean Reversion Strategy
   - Buy after `n` consecutive days of negative returns.
   - Sell after `m` consecutive days of positive returns.

## How This Repository Matches the Assignment

1. Python code uses Backtrader and defines two separate strategy classes in `assignment1_bist100.py`:
   - `TrendFollowingStrategy`
   - `MeanReversionStrategy`

2. Data is downloaded from yfinance and daily returns are computed.

3. Optimization runs a grid search for both strategies with:
   - `n = 1..10`
   - `m = 1..10`
   - Total parameter combinations per strategy: 100

4. Evaluation computes these metrics for each run:
   - Total return
   - Annualized return
   - Volatility
   - Sharpe ratio
   - Maximum drawdown

5. Comparison step selects best `(n, m)` for each strategy and compares optimized results.

## Direct Answer to the Assignment Question
Question: Is it better to be a trend follower or a contrarian in BIST100?

Result for this tested sample:

The optimized Trend Following strategy has a higher Sharpe ratio than the optimized Mean Reversion strategy.

Conclusion: In this backtest sample, being a trend follower performs better than being a contrarian.

## Files Requested by the Assignment

Please submit at minimum:

- `assignment1_bist100.py` (Python code: data, strategies, optimization, evaluation)
- `short_report.md` (short report with results, tables/plots, and conclusion)

Generated result tables/plots are saved under `results/` and are referenced by the short report.

## Reproducibility

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the full pipeline:

```powershell
python assignment1_bist100.py
```

This run produces:

- Optimization outputs (`trend_results.csv`, `mean_results.csv`, `best_summary.csv`)
- Visualization files (`trend_sharpe_heatmap.png`, `mean_sharpe_heatmap.png`, `equity_curves.png`)
- Data diagnostics files
- Updated `short_report.md`

## Current Project Structure

```text
assignment1_bist100/
|- assignment1_bist100.py
|- inspect_data.py
|- inspect_tickers.py
|- requirements.txt
|- short_report.md
|- run_output.txt
|- README.md
\- results/
   |- best_summary.csv
   |- trend_results.csv
   |- mean_results.csv
   |- trend_sharpe_heatmap.png
   |- mean_sharpe_heatmap.png
   |- equity_curves.png
   |- data_diagnostics.csv
   |- data_head.csv
   |- data_tail.csv
   \- RESULTS_INDEX.md
```
