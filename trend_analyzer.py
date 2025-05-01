from typing import List
import numpy as np
import matplotlib.pyplot as plt

class TrendAnalyzer:
    @staticmethod
    def detect_trend(close_prices: List[float]) -> str:
        """
        Determines the trend (uptrend, downtrend, sideways) from a list of close prices.

        Parameters:
            close_prices: A list of recent close prices in order.

        Returns:
            A string representing the trend.
        """
        if len(close_prices) < 2:
            return "not enough data"

        x = np.arange(len(close_prices))
        y = np.array(close_prices)

        # Fit a linear regression line
        slope, _ = np.polyfit(x, y, 1)

        # Threshold to avoid false trends due to noise
        if slope > 0.01:
            return "uptrend"
        elif slope < -0.01:
            return "downtrend"
        else:
            return "sideways"

    @staticmethod
    def rolling_slope_trend(close_prices: List[float], window_size: int = 10) -> List[float]:
        """
        Computes the slope of a linear fit (trend) for each rolling window of close prices.

        Parameters:
            close_prices: List of close prices (e.g., 400 values).
            window_size: Number of points to use for each linear fit (default is 10).

        Returns:
            List of slopes (one per window), showing how the trend changes over time.
        """
        slopes = []
        x = np.arange(window_size)

        for i in range(len(close_prices) - window_size + 1):
            y = close_prices[i:i + window_size]
            y.reverse()
            m, _ = np.polyfit(x, y, 1)
            slopes.append(round(m, 2))

        return slopes

    @staticmethod
    def plot_best_fit_line(data: List[float], title: str):
        # Generate x values for the x-axis (e.g., 0, 1, 2, ..., n-1)
        data.reverse()
        x = np.arange(len(data))

        # Calculate the best fit line (linear regression)
        slope, intercept = np.polyfit(x, data, 1)  # 1 indicates linear fitting (degree 1)
        best_fit_line = slope * x + intercept

        # Plotting the data and the best fit line
        plt.scatter(x, data, color='blue', label='Data')
        plt.plot(x, best_fit_line, color='red', label='Best Fit Line')

        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title(title)
        plt.legend()

        plt.show()