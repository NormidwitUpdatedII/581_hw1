# Bist100-Algorithmic-Trading-Strategy-Comparison

**Script:** `Bist100-Algorithmic-Trading-Strategy-Comparison-src/assignment1_bist100.py` | **Report:** `Bist100-Algorithmic-Trading-Strategy-Comparison-src/short_report.md`

---

## Assignment Overview

Test two simple rule-based trading strategies on the BIST100 index and determine which approach — trend following or mean reversion — delivers better risk-adjusted performance.

| Parameter | Value |
|---|---|
| Data source | yfinance (`XU100.IS`, daily bars) |
| Sample period | 2010-01-04 to 2026-03-27 (4,069 trading days) |
| Backtest engine | Backtrader |
| Optimization grid | n = 1…10, m = 1…10 (100 combinations per strategy) |
| Selection criterion | Sharpe ratio |
| Positioning | Long-only, 95% allocation per signal |
| Commission | 0.1% per trade |

---

## Strategies

**Trend Following** (`TrendFollowingStrategy`): Buy after `n` consecutive days of positive returns; sell after `m` consecutive days of negative returns. Bets on momentum persistence.

**Mean Reversion** (`MeanReversionStrategy`): Buy after `n` consecutive days of negative returns; sell after `m` consecutive days of positive returns. Bets on short-term reversal.

---

## Answer to the Assignment Question

> *Is it better to be a trend follower or a contrarian in BIST100?*

**Trend Following.** The optimized Trend Following strategy (n=4, m=6) achieves a Sharpe ratio of **1.058** versus **0.937** for the best Mean Reversion setup (n=1, m=10). It also produces lower volatility (21.0% vs. 23.3%) and a smaller maximum drawdown (28.6% vs. 32.8%). See `short_report.md` for the full analysis.

| Strategy | n | m | Sharpe | Ann. Return | Max Drawdown |
|---|:-:|:-:|--:|--:|--:|
| Trend Following | 4 | 6 | **1.058** | 22.17% | 28.63% |
| Mean Reversion | 1 | 10 | 0.937 | 21.04% | 32.80% |
| Buy & Hold | — | — | 0.922 | 21.69% | 34.33% |

---

## Quickstart

```bash
# Install dependencies
cd Bist100-Algorithmic-Trading-Strategy-Comparison-src
pip install -r requirements.txt

# Run full pipeline (data download → backtest → optimization → output)
python assignment1_bist100.py
```

> **Note on ticker:** The assignment specifies `^XU100`. The script attempts this first and automatically falls back to `XU100.IS` when long-history data is sparse. The ticker actually used is logged to `results/data_diagnostics.csv`.

---

## Repository Structure

```
.
├── README.md
└── Bist100-Algorithmic-Trading-Strategy-Comparison-src/
    ├── assignment1_bist100.py     # Main script: strategies, grid search, metrics, plots
    ├── short_report.md            # Report with tables, heatmaps, equity curves, conclusion
    ├── requirements.txt           # Python dependencies
    ├── run_output.txt             # Console output from the latest run
    ├── inspect_data.py            # Helper: inspect downloaded price data
    ├── inspect_tickers.py         # Helper: check ticker availability in yfinance
    └── results/
        ├── best_summary.csv       # Best (n, m) and metrics for each strategy + buy-and-hold
        ├── trend_results.csv      # Full 10×10 grid results — Trend Following (100 rows)
        ├── mean_results.csv       # Full 10×10 grid results — Mean Reversion (100 rows)
        ├── trend_sharpe_heatmap.png
        ├── mean_sharpe_heatmap.png
        ├── equity_curves.png
        ├── data_diagnostics.csv   # Ticker used, row count, date range, price range
        ├── data_head.csv          # First rows of downloaded data
        ├── data_tail.csv          # Last rows of downloaded data
        └── RESULTS_INDEX.md       # Index of all output files
```

---

## Output Files

| File | Description |
|---|---|
| `results/best_summary.csv` | One row per strategy (+ buy-and-hold) with best params and all metrics |
| `results/trend_results.csv` | 100-row grid — every (n, m) for Trend Following |
| `results/mean_results.csv` | 100-row grid — every (n, m) for Mean Reversion |
| `results/trend_sharpe_heatmap.png` | Sharpe heatmap for Trend Following (all 100 cells valid) |
| `results/mean_sharpe_heatmap.png` | Sharpe heatmap for Mean Reversion (gray = NaN, see note below) |
| `results/equity_curves.png` | Portfolio value over time for all three approaches |

> **Note on gray cells in the Mean Reversion heatmap:** The top two rows (n = 9, n = 10) are gray because those parameter combinations effectively never trigger an entry in this sample — requiring 9–10 consecutive down-days is too strict. Zero trades → zero return variance → Sharpe is undefined. This is expected, not a bug.

---

## Requirement Coverage

| Assignment Requirement | Implementation |
|---|---|
| Daily BIST100 data from yfinance | `yf.download("XU100.IS", ...)` in `assignment1_bist100.py` |
| Daily returns computed | Close-to-close % change: `r_t = P_t / P_{t-1} − 1` |
| Two separate Backtrader strategy classes | `TrendFollowingStrategy`, `MeanReversionStrategy` |
| Grid search n = 1…10, m = 1…10 | 100 combinations × 2 strategies = 200 backtests |
| Metrics per run | Total return, annualized return, volatility, Sharpe, max drawdown |
| Best (n, m) selected per strategy | Argmax Sharpe over full grid |
| Strategies compared, question answered | `short_report.md` Section 5 and this README |
| Short report with tables, plots, conclusions | `short_report.md` |