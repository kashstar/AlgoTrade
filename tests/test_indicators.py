import numpy as np
import pandas as pd

from algotrade.indicators import compute_indicators


def _synthetic_ohlc(n: int = 300) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    close = pd.Series(100 + np.cumsum(np.sin(np.linspace(0, 20, n))), index=idx)
    high = close + 1
    low = close - 1
    return pd.DataFrame({"close": close, "high": high, "low": low})


def test_compute_indicators_shapes_and_warmup():
    df = _synthetic_ohlc()
    ind = compute_indicators(df["close"], df["high"], df["low"], long_window=200)

    frame = ind.to_frame(df["close"])
    assert len(frame) == len(df)
    assert list(frame.columns) == [
        "close",
        "sma_fast",
        "sma_slow",
        "sma_long",
        "rsi",
        "macd",
        "macd_signal",
        "bb_upper",
        "bb_lower",
        "atr",
    ]
    # SMA(200) can't have a value before 200 bars of history
    assert frame["sma_long"].iloc[:199].isna().all()
    assert frame["sma_long"].iloc[199:].notna().all()


def test_bollinger_bands_bracket_price_most_of_the_time():
    df = _synthetic_ohlc()
    ind = compute_indicators(df["close"], df["high"], df["low"])
    frame = ind.to_frame(df["close"])
    valid = frame.dropna(subset=["bb_upper", "bb_lower"])
    within_band = (valid["close"] <= valid["bb_upper"]) & (valid["close"] >= valid["bb_lower"])
    assert within_band.mean() > 0.8
