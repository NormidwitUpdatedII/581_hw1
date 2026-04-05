import argparse
import math
from pathlib import Path

import backtrader as bt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


class TrendFollowingStrategy(bt.Strategy):
    params = (
        ("n", 3),
        ("m", 3),
    )

    def __init__(self):
        self.pos_run = 0
        self.neg_run = 0

    def next(self):
        if len(self.data) < 2:
            return

        ret = (self.data.close[0] / self.data.close[-1]) - 1.0

        if ret > 0:
            self.pos_run += 1
            self.neg_run = 0
        elif ret < 0:
            self.neg_run += 1
            self.pos_run = 0
        else:
            self.pos_run = 0
            self.neg_run = 0

        if not self.position and self.pos_run >= self.params.n:
            self.buy()
        elif self.position and self.neg_run >= self.params.m:
            self.close()


class MeanReversionStrategy(bt.Strategy):
    params = (
        ("n", 3),
        ("m", 3),
    )

    def __init__(self):
        self.pos_run = 0
        self.neg_run = 0

    def next(self):
        if len(self.data) < 2:
            return

        ret = (self.data.close[0] / self.data.close[-1]) - 1.0

        if ret > 0:
            self.pos_run += 1
            self.neg_run = 0
        elif ret < 0:
            self.neg_run += 1
            self.pos_run = 0
        else:
            self.pos_run = 0
            self.neg_run = 0

        if not self.position and self.neg_run >= self.params.n:
            self.buy()
        elif self.position and self.pos_run >= self.params.m:
            self.close()


def download_data(start_date: str, end_date: str):
    # ^XU100 often has sparse history on Yahoo; XU100.IS is used as a fallback.
    ticker_candidates = ["^XU100", "XU100.IS"]

    best_ticker = None
    best_df = None

    for ticker in ticker_candidates:
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1d",
            auto_adjust=True,
            progress=False,
        )

        if df.empty:
            continue

        # Flatten MultiIndex columns when yfinance returns (field, ticker).
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]

        required = ["open", "high", "low", "close"]
        if any(col not in df.columns for col in required):
            continue

        if "volume" not in df.columns:
            df["volume"] = 0.0

        cleaned = df[["open", "high", "low", "close", "volume"]].dropna().copy()

        if best_df is None or len(cleaned) > len(best_df):
            best_df = cleaned
            best_ticker = ticker

    if best_df is None:
        raise ValueError("No usable BIST100 data returned from yfinance.")

    best_df["openinterest"] = 0.0
    best_df["daily_return"] = best_df["close"].pct_change().fillna(0.0)

    return best_df, best_ticker


def compute_metrics(daily_returns: pd.Series, drawdown_analysis: dict) -> dict:
    if daily_returns.empty:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe": np.nan,
            "max_drawdown": 0.0,
        }

    total_return = float((1.0 + daily_returns).prod() - 1.0)
    ann_return = float((1.0 + total_return) ** (252.0 / len(daily_returns)) - 1.0)

    std = float(daily_returns.std(ddof=0))
    volatility = float(std * math.sqrt(252.0))

    if std == 0.0:
        sharpe = np.nan
    else:
        sharpe = float((daily_returns.mean() / std) * math.sqrt(252.0))

    max_dd = float(drawdown_analysis.get("max", {}).get("drawdown", 0.0) / 100.0)

    return {
        "total_return": total_return,
        "annualized_return": ann_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }


def optimize_strategy(
    strategy_cls,
    price_df: pd.DataFrame,
    n_values,
    m_values,
    initial_cash: float,
    commission: float,
) -> pd.DataFrame:
    cerebro = bt.Cerebro(optreturn=False)

    data = bt.feeds.PandasData(dataname=price_df)
    cerebro.adddata(data)

    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    cerebro.optstrategy(strategy_cls, n=n_values, m=m_values)

    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days, compression=1, _name="timereturn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    runs = cerebro.run(maxcpus=1)

    rows = []
    for run in runs:
        strat = run[0]
        n = int(strat.params.n)
        m = int(strat.params.m)

        ret_dict = strat.analyzers.timereturn.get_analysis()
        daily_returns = pd.Series(ret_dict, dtype=float).sort_index()
        dd = strat.analyzers.drawdown.get_analysis()

        metrics = compute_metrics(daily_returns, dd)
        rows.append(
            {
                "n": n,
                "m": m,
                **metrics,
            }
        )

    out = pd.DataFrame(rows).sort_values(["n", "m"]).reset_index(drop=True)
    return out


def pick_best(results_df: pd.DataFrame) -> pd.Series:
    ranked = results_df.copy()
    ranked["sharpe_rank"] = ranked["sharpe"].fillna(-np.inf)

    ranked = ranked.sort_values(
        ["sharpe_rank", "annualized_return", "total_return"],
        ascending=[False, False, False],
    )

    return ranked.iloc[0]


def run_single_strategy(
    strategy_cls,
    price_df: pd.DataFrame,
    n: int,
    m: int,
    initial_cash: float,
    commission: float,
):
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=price_df)
    cerebro.adddata(data)

    cerebro.addstrategy(strategy_cls, n=n, m=m)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Days, compression=1, _name="timereturn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    strat = cerebro.run()[0]

    ret_dict = strat.analyzers.timereturn.get_analysis()
    daily_returns = pd.Series(ret_dict, dtype=float).sort_index()
    dd = strat.analyzers.drawdown.get_analysis()

    metrics = compute_metrics(daily_returns, dd)
    equity = (1.0 + daily_returns).cumprod() * initial_cash

    return metrics, equity


def plot_heatmap(results_df: pd.DataFrame, title: str, out_path: Path):
    pivot = results_df.pivot(index="n", columns="m", values="sharpe")
    values = pivot.values.astype(float)
    masked_values = np.ma.masked_invalid(values)
    cmap = plt.cm.viridis.copy()
    cmap.set_bad(color="#d9d9d9")

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(masked_values, aspect="auto", origin="lower", cmap=cmap)

    ax.set_title(title)
    ax.set_xlabel("m (sell threshold)")
    ax.set_ylabel("n (buy threshold)")

    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    cbar = fig.colorbar(im, ax=ax)
    cbar_label = "Sharpe Ratio"
    if np.isnan(values).any():
        cbar_label += " (gray = no trades/zero variance)"
    cbar.set_label(cbar_label)

    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_equity_curves(
    trend_equity: pd.Series,
    mean_equity: pd.Series,
    buy_hold_equity: pd.Series,
    out_path: Path,
):
    fig, ax = plt.subplots(figsize=(11, 6))

    trend_equity.sort_index().plot(ax=ax, label="Trend Following (best)")
    mean_equity.sort_index().plot(ax=ax, label="Mean Reversion (best)")
    buy_hold_equity.sort_index().plot(ax=ax, label="Buy & Hold", linestyle="--")

    ax.set_title("Equity Curve Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def to_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def write_report(
    out_path: Path,
    data_ticker: str,
    start_date: str,
    end_date: str,
    trend_best: pd.Series,
    mean_best: pd.Series,
    buy_hold_metrics: dict,
    winner: str,
    trend_nan_count: int,
    mean_nan_count: int,
    mean_nan_n_values: list,
):
    lines = []
    lines.append("# Assignment 1 Report - BIST100 Strategy Comparison")
    lines.append("")
    lines.append("## Setup")
    lines.append(
        f"- Data source: yfinance daily bars from {start_date} to {end_date}; "
        f"primary ticker `^XU100`, actual run used `{data_ticker}`"
    )
    lines.append("- Backtest engine: backtrader")
    lines.append("- Parameter grid: n=1..10, m=1..10 (100 combinations per strategy)")
    lines.append("- Positioning: long-only, 95% portfolio allocation per signal")
    lines.append("")
    lines.append("## Best Parameters and Metrics")
    lines.append("")
    lines.append("| Strategy | n | m | Total Return | Annualized Return | Volatility | Sharpe | Max Drawdown |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        "| Trend Following | "
        f"{int(trend_best['n'])} | {int(trend_best['m'])} | {to_pct(float(trend_best['total_return']))} | "
        f"{to_pct(float(trend_best['annualized_return']))} | {to_pct(float(trend_best['volatility']))} | "
        f"{float(trend_best['sharpe']):.3f} | {to_pct(float(trend_best['max_drawdown']))} |"
    )
    lines.append(
        "| Mean Reversion | "
        f"{int(mean_best['n'])} | {int(mean_best['m'])} | {to_pct(float(mean_best['total_return']))} | "
        f"{to_pct(float(mean_best['annualized_return']))} | {to_pct(float(mean_best['volatility']))} | "
        f"{float(mean_best['sharpe']):.3f} | {to_pct(float(mean_best['max_drawdown']))} |"
    )
    lines.append(
        "| Buy & Hold | - | - | "
        f"{to_pct(float(buy_hold_metrics['total_return']))} | {to_pct(float(buy_hold_metrics['annualized_return']))} | "
        f"{to_pct(float(buy_hold_metrics['volatility']))} | {float(buy_hold_metrics['sharpe']):.3f} | "
        f"{to_pct(float(buy_hold_metrics['max_drawdown']))} |"
    )
    lines.append("")
    lines.append("## Visuals")
    lines.append("- Sharpe heatmap (Trend Following): `results/trend_sharpe_heatmap.png`")
    lines.append("- Sharpe heatmap (Mean Reversion): `results/mean_sharpe_heatmap.png`")
    lines.append("- Equity curve comparison: `results/equity_curves.png`")
    lines.append("")
    lines.append("## Data Notes")
    lines.append(
        f"- Sharpe NaN cells (no trades or zero daily return variance): "
        f"Trend Following = {trend_nan_count}, Mean Reversion = {mean_nan_count}."
    )
    if mean_nan_n_values:
        lines.append(
            f"- For Mean Reversion, NaN Sharpe appears at n values: {', '.join(str(x) for x in mean_nan_n_values)}."
        )
    lines.append("")
    lines.append("## Conclusion")
    lines.append(
        f"Based on out-of-sample-free historical backtests with the selected optimization metric (Sharpe ratio), "
        f"the stronger approach on this sample period is: **{winner}**."
    )
    lines.append(
        "This result indicates whether momentum persistence (trend following) or short-term reversal "
        "(contrarian mean reversion) had better risk-adjusted performance on BIST100 during the tested period."
    )
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("Run: `python assignment1_bist100.py`")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="BIST100 strategy optimization assignment")
    parser.add_argument("--start", type=str, default="2010-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2026-03-29", help="End date (YYYY-MM-DD)")
    parser.add_argument("--cash", type=float, default=100000.0, help="Initial cash")
    parser.add_argument("--commission", type=float, default=0.001, help="Commission per trade")
    parser.add_argument("--outdir", type=str, default="results", help="Output directory")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    price_df, data_ticker = download_data(args.start, args.end)

    diagnostics = {
        "ticker_used": data_ticker,
        "rows": len(price_df),
        "start": str(price_df.index.min()),
        "end": str(price_df.index.max()),
        "close_min": float(price_df["close"].min()),
        "close_max": float(price_df["close"].max()),
        "close_unique": int(price_df["close"].nunique()),
    }
    pd.Series(diagnostics).to_csv(outdir / "data_diagnostics.csv", header=["value"])
    price_df.head(10).to_csv(outdir / "data_head.csv")
    price_df.tail(10).to_csv(outdir / "data_tail.csv")

    n_values = list(range(1, 11))
    m_values = list(range(1, 11))

    trend_results = optimize_strategy(
        TrendFollowingStrategy,
        price_df,
        n_values,
        m_values,
        args.cash,
        args.commission,
    )

    mean_results = optimize_strategy(
        MeanReversionStrategy,
        price_df,
        n_values,
        m_values,
        args.cash,
        args.commission,
    )

    trend_best = pick_best(trend_results)
    mean_best = pick_best(mean_results)
    trend_nan_count = int(trend_results["sharpe"].isna().sum())
    mean_nan_count = int(mean_results["sharpe"].isna().sum())
    mean_nan_n_values = sorted(
        int(x) for x in mean_results.loc[mean_results["sharpe"].isna(), "n"].dropna().unique().tolist()
    )

    trend_metrics, trend_equity = run_single_strategy(
        TrendFollowingStrategy,
        price_df,
        int(trend_best["n"]),
        int(trend_best["m"]),
        args.cash,
        args.commission,
    )
    mean_metrics, mean_equity = run_single_strategy(
        MeanReversionStrategy,
        price_df,
        int(mean_best["n"]),
        int(mean_best["m"]),
        args.cash,
        args.commission,
    )

    buy_hold_returns = price_df["close"].pct_change().fillna(0.0)
    buy_hold_drawdown = {
        "max": {
            "drawdown": (
                ((buy_hold_returns.add(1.0).cumprod() / buy_hold_returns.add(1.0).cumprod().cummax()) - 1.0)
                .min()
                * -100.0
            )
        }
    }
    buy_hold_metrics = compute_metrics(buy_hold_returns, buy_hold_drawdown)

    trend_results.to_csv(outdir / "trend_results.csv", index=False)
    mean_results.to_csv(outdir / "mean_results.csv", index=False)

    summary_df = pd.DataFrame(
        [
            {
                "strategy": "trend_following",
                "n": int(trend_best["n"]),
                "m": int(trend_best["m"]),
                **trend_metrics,
            },
            {
                "strategy": "mean_reversion",
                "n": int(mean_best["n"]),
                "m": int(mean_best["m"]),
                **mean_metrics,
            },
            {
                "strategy": "buy_and_hold",
                "n": np.nan,
                "m": np.nan,
                **buy_hold_metrics,
            },
        ]
    )
    summary_df.to_csv(outdir / "best_summary.csv", index=False)

    plot_heatmap(
        trend_results,
        "Trend Following Sharpe Heatmap (n,m)",
        outdir / "trend_sharpe_heatmap.png",
    )
    plot_heatmap(
        mean_results,
        "Mean Reversion Sharpe Heatmap (n,m)",
        outdir / "mean_sharpe_heatmap.png",
    )

    buy_hold_equity = (1.0 + buy_hold_returns).cumprod() * args.cash
    plot_equity_curves(trend_equity, mean_equity, buy_hold_equity, outdir / "equity_curves.png")

    winner = "Trend Following" if float(trend_best["sharpe"]) >= float(mean_best["sharpe"]) else "Mean Reversion"

    write_report(
        out_path=Path("short_report.md"),
        data_ticker=data_ticker,
        start_date=args.start,
        end_date=args.end,
        trend_best=trend_best,
        mean_best=mean_best,
        buy_hold_metrics=buy_hold_metrics,
        winner=winner,
        trend_nan_count=trend_nan_count,
        mean_nan_count=mean_nan_count,
        mean_nan_n_values=mean_nan_n_values,
    )

    print("Optimization complete.")
    print(f"Best Trend Following (n,m): ({int(trend_best['n'])}, {int(trend_best['m'])})")
    print(f"Best Mean Reversion (n,m): ({int(mean_best['n'])}, {int(mean_best['m'])})")
    print(f"Winner by Sharpe ratio: {winner}")
    print(f"Results saved under: {outdir.resolve()}")


if __name__ == "__main__":
    main()
