---
name: tradingagents-research
description: Research any stock ticker TradingAgents-style (analysts, bull/bear debate, trader, risk, portfolio rating) using this repo's keyless data feeds plus TradingView, with Claude as the LLM. No LLM API key needed.
---

# TradingAgents research, Claude-native

Runs this repo's TradingAgents pipeline with you, Claude, playing every agent. No LLM API key is needed: the repo supplies the data (yfinance, SEC EDGAR, all keyless) and the TradingView connector, when available, supplies a second source. Use it when the user asks to research, analyse or rate a ticker.

Inputs: `TICKER` (any symbol, e.g. NVDA, AAPL) and an analysis date `YYYY-MM-DD` (default: the last completed trading day).

## 1. Set up (once per session)

From the repo root:

```bash
python3 -m venv /tmp/ta-venv && /tmp/ta-venv/bin/pip install -q -e .
```

Run the install in the background; it takes a couple of minutes.

## 2. Pull the repo's data feeds

From the repo root, write the output to a scratch folder outside the repo:

```bash
/tmp/ta-venv/bin/python .claude/skills/tradingagents-research/ta_pull.py TICKER YYYY-MM-DD <scratch>/<ticker>
```

It writes one text file per feed (prices, fundamentals, statements, news, insider transactions, technical indicators) and prints ok/error for each. Read the files. Notes:

- Statements or profile data "withheld for this date" are normal for foreign filers (20-F/6-K) and for past dates. Fill the gap from TradingView or the company's filings.
- If `FRED_API_KEY` is set, also call `route_to_vendor("get_macro_indicators", "FEDFUNDS", date, 90)`; otherwise skip macro.

## 3. Pull TradingView data (symbol as EXCHANGE:TICKER)

If the Tradingview MCP tools are available, load them with ToolSearch and call in parallel:

- `get_financials` (TTM snapshot), `get_forecasts` (ratings, targets, estimates)
- `get_technicals-rating` (1D), `get_ohlcv` (1D, 260 bars, summary=true)
- `get_news` (limit 25), `get_symbol_data` with columns `earnings_release_next_date, Perf.1M, Perf.3M, Perf.YTD, price_52_week_high, price_52_week_low`

Cross-check price and RSI between the repo feed and TradingView. If they differ, say so and prefer the later timestamp. Use one or two web searches for the latest quarter's results and guidance, and cite the pages.

## 4. Play the agents, in the repo's order

For prompt detail, read the matching file under `tradingagents/agents/`. Keep each step short and grounded in the data; never invent a number.

1. **Market analyst** (`analysts/market_analyst.py`): trend vs 10 EMA / 50 / 200 SMA, RSI, MACD vs signal, Bollinger, ATR for volatility.
2. **Fundamentals analyst** (`analysts/fundamentals_analyst.py`): growth, margins, cash flow, balance sheet, valuation, funding and dilution.
3. **News analyst** (`analysts/news_analyst.py`): last 14 days of company news plus macro, each tagged positive, negative or sector-wide.
4. **Sentiment analyst** (`analysts/sentiment_analyst.py`): analyst ratings and target changes, insider transactions, headline tone.
5. **Bull vs bear researchers** (`researchers/`): one round each, each rebutting the other's strongest point.
6. **Research manager** (`managers/research_manager.py`): pick a side and write the investment plan.
7. **Trader** (`trader/trader.py`): entry, levels that change the view, sizing given ATR.
8. **Risk debate** (`risk_mgmt/`): aggressive, conservative and neutral views, a line or two each.
9. **Portfolio manager** (`managers/portfolio_manager.py`): final **Rating: exactly one of Buy / Overweight / Hold / Underweight / Sell** (scale in `agents/rating.py`), with the triggers that would change it.

If earnings fall within about 3 trading days, say so at the top and frame the rating around the print.

## 5. Deliver

Write the report as a document (a Claude Doc where available, otherwise Markdown): bottom line and rating first, then Fundamentals, News, Sentiment, Technicals, Bull vs bear, Trader and risk view, and Sources, with an as-of date. Use tables for metrics and put "Not investment advice" under the title. Reply to the user in two or three sentences with the rating, the one-line thesis and the link.
