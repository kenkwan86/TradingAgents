"""Pull every TradingAgents data feed for one ticker into a folder of text files."""
import sys, os, datetime as dt
from tradingagents.dataflows.router import route_to_vendor

ticker, date, out = sys.argv[1].upper(), sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
d = dt.date.fromisoformat(date)
ago = lambda n: (d - dt.timedelta(days=n)).isoformat()

calls = {
    "prices_1y": ("get_stock_data", ticker, ago(365), date),
    "fundamentals": ("get_fundamentals", ticker, date),
    "income_statement": ("get_income_statement", ticker, "quarterly", date),
    "balance_sheet": ("get_balance_sheet", ticker, "quarterly", date),
    "cashflow": ("get_cashflow", ticker, "quarterly", date),
    "news_14d": ("get_news", ticker, ago(14), date),
    "global_news_7d": ("get_global_news", date, 7, 15),
    "insider_transactions": ("get_insider_transactions", ticker, None),
}
for ind in ["close_50_sma", "close_200_sma", "close_10_ema", "rsi", "macd", "macds", "boll_ub", "boll_lb", "atr"]:
    calls[f"ind_{ind}"] = ("get_indicators", ticker, ind, date, 30)

for name, (method, *args) in calls.items():
    try:
        text = str(route_to_vendor(method, *args))
        status = "ok"
    except Exception as e:
        text, status = f"ERROR {type(e).__name__}: {e}", "error"
    with open(os.path.join(out, f"{name}.txt"), "w") as f:
        f.write(text)
    print(f"{status:5} {name} ({len(text)} chars)")
