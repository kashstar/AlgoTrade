"""Technical indicators used across strategies, built on vectorbt."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import vectorbt as vbt


@dataclass
class Indicators:
    """Bundle of computed vectorbt indicator objects for one OHLCV series."""

    sma_fast: vbt.MA
    sma_slow: vbt.MA
    sma_long: vbt.MA
    rsi: vbt.RSI
    macd: vbt.MACD
    bb: vbt.BBANDS
    atr: vbt.ATR

    def to_frame(self, close: pd.Series) -> pd.DataFrame:
        """Flatten the indicators into a single DataFrame for display/inspection."""
        return pd.DataFrame(
            {
                "close": close,
                "sma_fast": self.sma_fast.ma,
                "sma_slow": self.sma_slow.ma,
                "sma_long": self.sma_long.ma,
                "rsi": self.rsi.rsi,
                "macd": self.macd.macd,
                "macd_signal": self.macd.signal,
                "bb_upper": self.bb.upper,
                "bb_lower": self.bb.lower,
                "atr": self.atr.atr,
            }
        )


def compute_indicators(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    *,
    fast_window: int = 20,
    slow_window: int = 50,
    long_window: int = 200,
    rsi_window: int = 14,
    macd_windows: tuple[int, int, int] = (12, 26, 9),
    bb_window: int = 20,
    bb_alpha: float = 2,
    atr_window: int = 14,
) -> Indicators:
    """Compute the standard indicator set used by the strategies in this project."""
    fast_macd, slow_macd, signal_macd = macd_windows
    return Indicators(
        sma_fast=vbt.MA.run(close, window=fast_window),
        sma_slow=vbt.MA.run(close, window=slow_window),
        sma_long=vbt.MA.run(close, window=long_window),
        rsi=vbt.RSI.run(close, window=rsi_window),
        macd=vbt.MACD.run(
            close, fast_window=fast_macd, slow_window=slow_macd, signal_window=signal_macd
        ),
        bb=vbt.BBANDS.run(close, window=bb_window, alpha=bb_alpha),
        atr=vbt.ATR.run(high, low, close, window=atr_window),
    )
