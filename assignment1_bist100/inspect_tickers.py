from pathlib import Path

import pandas as pd
import yfinance as yf

out = Path("results")
out.mkdir(exist_ok=True)

tickers = ["^XU100", "XU100.IS", "XU030.IS", "XU050.IS", "XUTUM.IS"]
rows = []
for t in tickers:
    df = yf.download(t, start="2010-01-01", interval="1d", auto_adjust=True, progress=False)
    rows.append({"ticker": t, "shape": str(df.shape)})
    p = out / f"inspect_{t.replace('^','_').replace('.','_')}.csv"
    df.to_csv(p)

pd.DataFrame(rows).to_csv(out / "inspect_tickers_summary.csv", index=False)
