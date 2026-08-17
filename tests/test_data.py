import pandas as pd

from algotrade.data import load_ohlc


def test_load_ohlc_indexes_by_timestamp(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "timestamp,open,high,low,close,volume\n"
        "1609459200,100,110,90,105,1.5\n"
        "1609545600,105,115,95,110,2.0\n"
    )

    df = load_ohlc(str(csv_path))

    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.is_monotonic_increasing
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.loc[pd.Timestamp("2021-01-01"), "close"] == 105
