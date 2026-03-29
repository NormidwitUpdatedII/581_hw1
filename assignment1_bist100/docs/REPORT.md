# Detailed Technical Report

## 1. Assignment Objective
The assignment asks us to test two simple BIST100 trading ideas using Python:

1. Trend Following
2. Mean Reversion (Contrarian)

Required tasks:

- Download daily BIST100 data from yfinance
- Compute daily returns
- Implement both strategies in Backtrader as separate classes
- Optimize parameters over n=1..10 and m=1..10
- Evaluate each run with standard performance metrics
- Compare optimized strategies and answer: trend follower or contrarian?

## 2. Why This Design
This design was chosen to directly map one-to-one to the assignment wording while keeping the implementation transparent:

- Separate strategy classes make logic easy to verify
- Full grid search ensures no cherry-picking
- Standard metrics support fair comparison by return and risk
- Output files (CSV + PNG) provide reproducible evidence

## 3. Data and Preparation

### 3.1 Data source
- Provider: yfinance
- Assignment target ticker: `^XU100`
- Practical fallback in code: `XU100.IS` when `^XU100` is sparse

### 3.2 Final run dataset used
From `results/data_diagnostics.csv`:

- ticker_used: `XU100.IS`
- rows: 4069 daily bars
- date range: 2010-01-04 to 2026-03-27
- close range: 487.39 to 14339.30

### 3.3 Return definition
Daily return is computed as close-to-close percentage change:

`daily_return[t] = close[t] / close[t-1] - 1`

## 4. Strategy Logic

## 4.1 Trend Following Strategy
- Buy condition: n consecutive positive daily returns
- Sell condition: m consecutive negative daily returns

Interpretation: enter when upward momentum is persistent, exit when downside momentum appears.

### 4.2 Mean Reversion Strategy
- Buy condition: n consecutive negative daily returns
- Sell condition: m consecutive positive daily returns

Interpretation: buy weakness expecting rebound, exit after recovery signal.

### 4.3 Positioning and execution assumptions
- Long-only
- PercentSizer with 95% allocation per signal
- Commission set by script argument (default 0.001)
- Initial capital default: 100000

## 5. Optimization Design
Each strategy is optimized on the same full grid:

- n = 1..10
- m = 1..10
- Total combinations per strategy: 100

Both grids are fully present in output files:
- `results/trend_results.csv` (100 rows)
- `results/mean_results.csv` (100 rows)

## 6. Evaluation Metrics
Each run computes:

- Total Return
- Annualized Return
- Volatility (annualized)
- Sharpe Ratio
- Maximum Drawdown

These are computed from daily strategy returns produced by Backtrader analyzers (`TimeReturn`, `DrawDown`).

## 7. Main Results

## 7.1 Best parameter sets
From `results/best_summary.csv`:

| Strategy | n | m | Total Return | Annualized Return | Volatility | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|
| Trend Following | 4 | 6 | 2437.89% | 22.17% | 21.04% | 1.058 | 28.63% |
| Mean Reversion | 1 | 10 | 2083.93% | 21.04% | 23.31% | 0.937 | 32.80% |
| Buy & Hold | - | - | 2279.37% | 21.69% | 24.59% | 0.922 | 34.33% |

## 7.2 Top 5 parameter combinations by Sharpe

### Trend Following top 5
| Rank | n | m | Sharpe | Annualized Return | Max Drawdown |
|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 6 | 1.0579 | 22.17% | 28.63% |
| 2 | 6 | 3 | 1.0458 | 10.48% | 24.79% |
| 3 | 6 | 2 | 1.0184 | 7.54% | 12.16% |
| 4 | 10 | 5 | 1.0062 | 11.30% | 20.14% |
| 5 | 7 | 5 | 1.0035 | 13.56% | 23.51% |

### Mean Reversion top 5
| Rank | n | m | Sharpe | Annualized Return | Max Drawdown |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 10 | 0.9366 | 21.04% | 32.80% |
| 2 | 1 | 9 | 0.9234 | 20.65% | 32.80% |
| 3 | 1 | 8 | 0.8870 | 19.56% | 32.99% |
| 4 | 1 | 7 | 0.8582 | 18.65% | 33.37% |
| 5 | 4 | 10 | 0.8508 | 17.48% | 32.68% |

## 8. Interpreting the Heatmaps

### 8.1 Trend heatmap
`results/trend_sharpe_heatmap.png` shows complete coverage with valid Sharpe values for all n,m pairs.

### 8.2 Mean heatmap upper gray region (important)
`results/mean_sharpe_heatmap.png` has gray cells in the upper rows because those parameter pairs produce no effective strategy variation:

- NaN Sharpe count: 20 cells
- Affected rows: n=9 and n=10 (all m values)

This is expected behavior, not a plotting bug.

Reason: there are not enough long consecutive down-run events to trigger entries for these strict n values in this sample, so those runs have zero-return variance and Sharpe becomes undefined.

## 9. Validation and Consistency Checks
The following checks were performed:

1. Output refresh check: core result files have matching latest timestamps.
2. Grid completeness: both strategy result CSVs contain exactly 100 rows.
3. Best-row consistency: best rows from full grids match `best_summary.csv` values exactly.
4. Report consistency: metric values in report files match CSV outputs.
5. Image integrity: all PNG files open correctly.

## 10. What We Found

1. Both optimized rule-based strategies beat buy-and-hold on Sharpe in this sample.
2. Trend Following has the strongest risk-adjusted profile (highest Sharpe, lower drawdown than alternatives).
3. Mean Reversion is competitive but weaker than Trend Following on Sharpe and drawdown.

## 11. Final Conclusion
For this BIST100 backtest sample and optimization setting, the evidence supports:

- Better approach: Trend Following
- Assignment answer: it is better to be a trend follower than a contrarian in this experiment.

## 12. Limitations and Future Improvements

- In-sample optimization can overfit; a train/test split would improve robustness.
- Transaction costs/slippage sensitivity analysis could be expanded.
- Additional constraints (minimum trade count) could filter unstable parameter regions.
- Rolling walk-forward validation would provide stronger out-of-sample confidence.
