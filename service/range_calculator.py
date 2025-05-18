from typing import List, Tuple
from datetime import datetime
from service.trend_analyzer import TrendAnalyzer
import pandas as pd

class RangeCalculator:

    @staticmethod
    def compute_candle_ranges_desc_sorted(
            candles: List[Tuple[str, datetime, float, float, float, float, int, int]]
    ) -> List[Tuple[datetime, float, float]]:
        """
        Expects candles sorted by datetime descending.
        Returns a list of (datetime, adjusted_open, range) for each candle,
        where first candle of each day uses the previous day's close as open.
        """
        result = []
        previous_close = None
        current_date = None

        # Process in ascending order for proper grouping
        for candle in reversed(candles):
            symbol, dt, open_, high, low, close, volume, oi = candle
            candle_date = dt.date()

            if previous_close is not None:
                tr = max(
                    high - low,
                    abs(high - previous_close),
                    abs(low - previous_close)
                )
            else:
                tr = high - low  # No previous close available for the first candle
            result.append((dt, open_, round(tr, 2)))

            previous_close = close  # Update for next day's first candle

        # Reverse result to return in original (descending) order
        return list(reversed(result))

    @staticmethod
    def calculate_atr(ranges: list[float], period: int = 14) -> list[float]:
        """
        Calculate the ATR from a list of true ranges.
        Returns a list of ATR values (starts from index = period - 1).
        """
        ranges.reverse()
        if len(ranges) < period:
            return []

        atr_list = []
        # Calculate the first ATR
        window = ranges[0:period]
        atr = sum(window) / period
        atr_list.append(round(atr,2))

        for i in range(period , len(ranges)):
            atr = (atr * (period - 1) + ranges[i]) / period
            atr_list.append(round(atr, 2))


        return list(reversed(atr_list))

    @staticmethod
    def find_ATR(candles: List[Tuple[str, datetime, float, float, float, float, int, int]],
    interval: int = 14) -> List[Tuple[datetime, float, float]]:
        range_data = RangeCalculator.compute_candle_ranges_desc_sorted(candles)
        range = [row[2] for row in range_data]
        # print(range)
        atr = RangeCalculator.calculate_atr(range,14)
        # print("ATR == "+ str(atr))
        offset = len(candles) - len(atr)
        # print("Offset = "+str(offset))

        relevant_candles = candles[0:len(atr)]
        relevant_range = range_data[0:len(atr)]
        # print("Length of Range == "+str(len(relevant_range)) +str(relevant_range))
        #
        # print("Length of Relavant candles == "+str(len(relevant_candles)))


        # Extract required columns
        data = {
            'symbol': [c[0] for c in relevant_candles],
            'datetime': [c[1] for c in relevant_candles],
            'open': [c[2] for c in relevant_candles],
            'high': [c[3] for c in relevant_candles],
            'low': [c[4] for c in relevant_candles],
            'close': [c[5] for c in relevant_candles],
            'volume': [c[6] for c in relevant_candles],
            'range': [r[2] for r in relevant_range],
            'atrvalue': [atrVal for atrVal in atr]
        }

        data_frame = pd.DataFrame(data)
        data_frame['range_atr_ratio'] = data_frame['range']/data_frame['atrvalue']

        # TrendAnalyzer.plot_best_fit_line(atr,"ATR")
        # Create DataFrame
        return data_frame


