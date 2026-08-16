# AlgoTrade

Fetches OHLC (open/high/low/close/volume) market data from the [Bitstamp API](https://www.bitstamp.net/api/) for algo trading experiments.

## Contents

- `data.ipynb` — pulls 1-minute OHLC candles for BTC/USD from Bitstamp's `/api/v2/ohlc/` endpoint.
- `tutorial.csv` — sample OHLC data (timestamp, open, high, low, close, volume).

## Usage

```bash
pip install requests pandas
```

Run `data.ipynb` to fetch fresh OHLC data. Adjust `market_symbol`, `step` (candle size in seconds), and `limit` (number of candles) as needed.
