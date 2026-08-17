"""Fetching and loading OHLCV market data from Bitstamp."""

from __future__ import annotations

import datetime as dt
import time

import pandas as pd
import requests

BITSTAMP_OHLC_URL = "https://www.bitstamp.net/api/v2/ohlc/{symbol}/"
REQUEST_LIMIT = 1000  # Bitstamp's max candles per request


def fetch_ohlc(
    symbol: str = "btcusd",
    step: int = 86400,
    years: float = 5,
    sleep_between_requests: float = 0.3,
) -> pd.DataFrame:
    """Fetch OHLCV candles from Bitstamp, paginating past the per-request limit.

    Args:
        symbol: Bitstamp market symbol, e.g. "btcusd".
        step: candle size in seconds (60, 300, 3600, 86400, ...).
        years: how far back to fetch, in years.
        sleep_between_requests: delay between paginated requests, to be polite to the API.

    Returns:
        DataFrame with columns [timestamp, open, high, low, close, volume],
        sorted ascending by timestamp, one row per candle.
    """
    url = BITSTAMP_OHLC_URL.format(symbol=symbol)
    end_time = int(dt.datetime.now().timestamp())
    start_time = end_time - int(years * 365 * step)

    candles: dict[str, dict] = {}
    cursor = start_time

    while cursor < end_time:
        params = {"step": step, "limit": REQUEST_LIMIT, "start": cursor}
        resp = requests.get(url, params=params, timeout=30).json()
        ohlc = resp.get("data", {}).get("ohlc", [])
        if not ohlc:
            break

        for row in ohlc:
            candles[row["timestamp"]] = row

        last_ts = int(ohlc[-1]["timestamp"])
        if last_ts <= cursor:
            break
        cursor = last_ts + step
        time.sleep(sleep_between_requests)

    df = pd.DataFrame(candles.values())
    df = df.astype(
        {
            "timestamp": "int64",
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "float64",
        }
    )
    return df.sort_values("timestamp").reset_index(drop=True)


def load_ohlc(path: str) -> pd.DataFrame:
    """Load a saved OHLCV CSV and index it by timestamp."""
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df.set_index("timestamp").sort_index()
