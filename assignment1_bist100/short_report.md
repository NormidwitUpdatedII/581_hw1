# Assignment 1 Report - BIST100 Strategy Comparison

## Setup
- Data source: yfinance daily bars from 2010-01-01 to 2026-03-29; primary ticker `^XU100`, actual run used `XU100.IS`
- Backtest engine: backtrader
- Parameter grid: n=1..10, m=1..10 (100 combinations per strategy)
- Positioning: long-only, 95% portfolio allocation per signal

## Best Parameters and Metrics

| Strategy | n | m | Total Return | Annualized Return | Volatility | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|
| Trend Following | 4 | 6 | 2437.89% | 22.17% | 21.04% | 1.058 | 28.63% |
| Mean Reversion | 1 | 10 | 2083.93% | 21.04% | 23.31% | 0.937 | 32.80% |
| Buy & Hold | - | - | 2279.37% | 21.69% | 24.59% | 0.922 | 34.33% |

## Visuals
- Sharpe heatmap (Trend Following): `results/trend_sharpe_heatmap.png`
- Sharpe heatmap (Mean Reversion): `results/mean_sharpe_heatmap.png`
- Equity curve comparison: `results/equity_curves.png`

## Data Notes
- Sharpe NaN cells (no trades or zero daily return variance): Trend Following = 0, Mean Reversion = 20.
- For Mean Reversion, NaN Sharpe appears at n values: 9, 10.

## Conclusion
Based on out-of-sample-free historical backtests with the selected optimization metric (Sharpe ratio), the stronger approach on this sample period is: **Trend Following**.
This result indicates whether momentum persistence (trend following) or short-term reversal (contrarian mean reversion) had better risk-adjusted performance on BIST100 during the tested period.

## Reproducibility
Run: `python assignment1_bist100.py`