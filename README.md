# AlgoTrade

A small BTC/USD backtesting lab: pull 5 years of daily OHLCV data from the [Bitstamp API](https://www.bitstamp.net/api/), compute technical indicators, and backtest trading strategies with [`vectorbt`](https://github.com/polakowo/vectorbt).

## Contents

- `main.ipynb` - the backtesting notebook:
  - Loads & prepares 5 years of daily OHLCV data
  - Computes indicators: SMA(20)/SMA(50)/SMA(200), RSI(14), MACD, Bollinger Bands, ATR
  - Backtests three strategies - **Moving Average Crossover** (trend-following), **RSI Mean Reversion** (contrarian), and **Golden Cross** (SMA 20/200 trend filter)
  - Compares all three against a buy & hold benchmark (returns, Sharpe, max drawdown, win rate) - the Golden Cross is the one that actually beats buy & hold, by staying out of BTC's deepest drawdowns
  - Equity curve, drawdown, and trade plots for each strategy
- `data.ipynb` - fetches daily OHLC candles for BTC/USD from Bitstamp's `/api/v2/ohlc/` endpoint, paginating past the 1000-candle-per-request limit to cover a full 5-year window.
- `tutorial.csv` - 5 years of daily OHLCV data (timestamp, open, high, low, close, volume) used by `main.ipynb`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "numpy<2" pandas vectorbt requests ipykernel
```

> `vectorbt` requires `numpy<2` - installing a newer numpy in the same environment will break it at import time.

## Usage

- Run `data.ipynb` to fetch fresh OHLCV data (adjust `market_symbol`, `STEP`, and `YEARS` as needed).
- Run `main.ipynb` top to bottom to reproduce the indicators, strategies, and comparison charts. Tune strategy parameters (MA windows, RSI thresholds, fees) in the config cell at the top.

## Disclaimer

For research and educational purposes only - not financial advice. Backtest results on limited historical data do not predict future performance.
