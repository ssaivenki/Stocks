from service.trend_analyzer import TrendAnalyzer


class Plots:
    @staticmethod
    def smooth_and_plotTrend(price, symbol, no_of_candles, no_of_points_to_fit, title, plot_zero):
        price_slopes = TrendAnalyzer.rolling_slope_trend(price, no_of_candles)
        print("Closed Price Slopes - Candle count = 10 Symbol = " + symbol + " Table = " + title + str(price_slopes))
        if len(price_slopes) > no_of_points_to_fit:
            TrendAnalyzer.plot_best_fit_line(price_slopes[:no_of_points_to_fit], symbol + " " + title + str(no_of_candles), plot_zero)

