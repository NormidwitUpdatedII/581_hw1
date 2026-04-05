


# Assignment 1 — BIST100 Strategy Comparison




## 1. Data

Daily closing prices for the BIST100 index were downloaded via **yfinance** (ticker: `XU100.IS`) covering **2010-01-04 to 2026-03-27** — a total of **4,069 trading days**. The index closed between 487 and 14,339 points over this period, reflecting substantial structural growth in Turkish equities. Daily returns were computed as close-to-close percentage changes:

$$r_t = \frac{P_t}{P_{t-1}} - 1$$

> **Note on ticker:** The assignment specifies `^XU100`. The code attempts this ticker first and falls back to `XU100.IS` when long-history data is sparse. The final run used `XU100.IS`, as recorded in `results/data_diagnostics.csv`.

---

## 2. Strategies

Both strategies are **long-only** with 95% portfolio allocation per signal and a 0.1% commission per trade. They are implemented as two independent Backtrader strategy classes.

**Trend Following:** Enter long after *n* consecutive days of positive returns; exit after *m* consecutive days of negative returns. The rationale is momentum persistence — a sustained run of positive days signals that buying pressure is likely to continue.

**Mean Reversion:** Enter long after *n* consecutive days of negative returns; exit after *m* consecutive days of positive returns. The rationale is short-term reversal — sustained weakness is expected to attract buyers and produce a rebound.

---

## 3. Optimization

Each strategy was independently optimized over a full 10×10 grid of *n* = 1…10 and *m* = 1…10, yielding **100 backtested combinations per strategy**. The best parameter set was selected by maximizing the **Sharpe ratio**. Full grid results are stored in the accompanying CSV files.

---

## 4. Results

### 4.1 Best Parameter Sets

| Strategy | n | m | Total Return | Ann. Return | Volatility | Sharpe | Max Drawdown |
|---|:-:|:-:|--:|--:|--:|--:|--:|
| Trend Following | 4 | 6 | **2,437.89%** | **22.17%** | **21.04%** | **1.058** | **28.63%** |
| Mean Reversion | 1 | 10 | 2,083.93% | 21.04% | 23.31% | 0.937 | 32.80% |
| Buy & Hold | — | — | 2,279.37% | 21.69% | 24.59% | 0.922 | 34.33% |

Both optimized strategies outperform buy-and-hold on Sharpe ratio. Trend Following leads across every dimension: highest return, lowest volatility, and shallowest maximum drawdown.

---

### 4.2 Sharpe Ratio Heatmaps

The Trend Following heatmap shows **complete coverage** with no missing cells. The highest-Sharpe region clusters around moderate entry windows (n = 4–7) paired with short-to-medium exit triggers (m = 2–6). Very short entry windows (n = 1–2) produce noisier, less consistent outcomes. Very long exit windows (m = 9–10) tend to erode performance by keeping the position open through sustained reversals.

---


The Mean Reversion heatmap has **20 gray (NaN) cells** in the top two rows (n = 9 and n = 10, all values of m). This is expected behavior, not a plotting error: requiring 9–10 consecutive down-days before entering is so restrictive that the strategy generates virtually no trades in this sample, producing zero return variance and an undefined Sharpe ratio. The best-performing region is concentrated at n = 1, combined with long exit windows (m = 7–10), indicating that a single down-day followed by a patient hold is the most effective contrarian setup on this data.

---

### 4.3 Equity Curves


All three equity curves trend sharply upward, consistent with the strong secular growth of BIST100 over 16 years. Trend Following (n=4, m=6) produces the smoothest curve: it closely tracks bullish phases while sidestepping some of the larger drawdowns via its exit rule. Mean Reversion (n=1, m=10) is more active and exhibits steeper short-term drops during volatile periods, though it ultimately recovers. Buy-and-hold terminates between the two strategies in total value but carries the largest peak-to-trough loss.

---

### 4.4 Top 5 Parameter Combinations

**Trend Following**

| Rank | n | m | Sharpe | Ann. Return | Max Drawdown |
|:-:|:-:|:-:|--:|--:|--:|
| 1 | 4 | 6 | 1.058 | 22.17% | 28.63% |
| 2 | 6 | 3 | 1.046 | 10.48% | 24.79% |
| 3 | 6 | 2 | 1.018 | 7.54% | 12.16% |
| 4 | 10 | 5 | 1.006 | 11.30% | 20.14% |
| 5 | 7 | 5 | 1.004 | 13.56% | 23.51% |

**Mean Reversion**

| Rank | n | m | Sharpe | Ann. Return | Max Drawdown |
|:-:|:-:|:-:|--:|--:|--:|
| 1 | 1 | 10 | 0.937 | 21.04% | 32.80% |
| 2 | 1 | 9 | 0.923 | 20.65% | 32.80% |
| 3 | 1 | 8 | 0.887 | 19.56% | 32.99% |
| 4 | 1 | 7 | 0.858 | 18.65% | 33.37% |
| 5 | 4 | 10 | 0.851 | 17.48% | 32.68% |

A structural pattern is visible in the mean reversion rankings: all top-5 entries share n = 1. Requiring more than one consecutive down-day before entering consistently reduces performance, suggesting that multi-day losing streaks on BIST100 are not reliable reversal setups — they more often signal continuation rather than bounce.

---

## 5. Conclusion

**In this experiment, it is better to be a trend follower than a contrarian on BIST100.**

Trend Following (n=4, m=6) achieves a Sharpe ratio of **1.058**, versus **0.937** for the best Mean Reversion setup — a meaningful gap in risk-adjusted terms. It also delivers lower annualized volatility (21.0% vs. 23.3%) and a shallower maximum drawdown (28.6% vs. 32.8%). Notably, even a passive buy-and-hold strategy outperforms the best mean reversion configuration on total return (2,279% vs. 2,084%), implying that active contrarian rules added risk exposure without proportionate reward over this period.

This outcome aligns with the momentum literature on emerging equity markets. BIST100 is heavily influenced by macro sentiment swings, exchange rate dynamics, and cross-border capital flows — all forces that tend to produce sustained directional moves rather than rapid mean reversion at daily frequencies. A strategy that waits for confirmation of upward momentum before entering is therefore better suited to this market's behavior than one that fades short-term weakness.

---

## 6. Limitations and Future Work

The results reported here should be interpreted with caution for several reasons.

**In-sample optimization.** Parameters were selected by maximizing Sharpe on the same data used for evaluation. This guarantees some degree of overfitting. A train/test split or rolling walk-forward validation would provide more reliable out-of-sample evidence — the actual performance gap between the two strategies might be narrower or wider on truly unseen data.

**Transaction cost sensitivity.** A fixed 0.1% commission is assumed. In practice, slippage, bid-ask spreads, and market impact could differ materially, especially for mean reversion strategies that tend to trade more frequently. A sensitivity analysis across a range of cost assumptions would strengthen the conclusions.

**Minimum trade count filter.** Some parameter combinations — particularly strict mean reversion setups — produce very few trades, leading to unstable metric estimates. Imposing a minimum trade count before reporting Sharpe would improve the reliability of the heatmaps.

**Long-only constraint.** Both strategies only go long. Allowing short positions would make mean reversion a fully symmetric contrarian strategy and could change the relative ranking.

**Single instrument.** Results are specific to BIST100 over one sample period. Testing on individual index constituents or other emerging market indices would indicate whether the trend-following edge generalizes beyond this context.

---

## 7. Reproducibility

```bash
pip install -r requirements.txt
python assignment1_bist100.py
```

All outputs are written to the `results/` directory. The ticker fallback logic (`^XU100` → `XU100.IS`) is handled automatically inside the script.

## Submitted Files

| File | Description |
|---|---|
| `assignment1_bist100.py` | Main script: data download, strategy classes, grid search, metrics, output generation |
| `short_report.md` | This report |
| `results/best_summary.csv` | Best (n, m) and metrics for each strategy + buy-and-hold |
| `results/trend_results.csv` | Full 10×10 grid results for Trend Following (100 rows) |
| `results/mean_results.csv` | Full 10×10 grid results for Mean Reversion (100 rows) |
| `results/trend_sharpe_heatmap.png` | Sharpe heatmap — Trend Following |
| `results/mean_sharpe_heatmap.png` | Sharpe heatmap — Mean Reversion |
| `results/equity_curves.png` | Equity curve comparison across all three approaches |
| `requirements.txt` | Python dependencies for reproducibility |

