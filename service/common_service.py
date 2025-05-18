from database.db_cache import get_db
from utility.utils import Utility


class CommonServices:

    @staticmethod
    def writeCandlesToDB(candles, tableName, symbol):
        if (len(candles) > 0):
            candles = [[symbol] + row for row in candles]

            for record in candles:
                record[1] = Utility.to_naive_ist(record[1])

            db = get_db()
            db.upsert_stock_price_data(candles, tableName)

    @staticmethod
    def writeToDB(stockData, tableName, symbol):
        if "data" in stockData:
            print("\n\n\n\nInside Writing to DB " + symbol + tableName+ "\n\n\n")
            candles = stockData["data"]["candles"]
            CommonServices.writeCandlesToDB(candles, tableName, symbol)