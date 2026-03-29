from pathlib import Path

import pandas as pd
import yfinance as yf

out = Path("results")
out.mkdir(exist_ok=True)

for end_date in ["2026-03-29", "2026-03-28", None]:
    df = yf.download("^XU100", start="2010-01-01", end=end_date, interval="1d", auto_adjust=True, progress=False)
    name = "none" if end_date is None else end_date
    df.to_csv(out / f"inspect_{name}.csv")

summary = []
for p in sorted(out.glob("inspect_*.csv")):
    d = pd.read_csv(p)
    summary.append({"file": p.name, "rows": len(d), "cols": list(d.columns)})

pd.DataFrame(summary).to_csv(out / "inspect_summary.csv", index=False)
