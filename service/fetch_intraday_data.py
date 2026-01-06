import json

from service.common_service import CommonServices
from utility.config import Configuration
from utility.utils import Utility
from database.stock_database import StockDatabase
from database.db_cache import get_db

class IntradayDataManager:

    def get_intraday_OHLC_from_upstox_for_sector(self, symbol: str = None, sector: str = None):
        # Get all the stocks for the sector and call the
        db = get_db()
        stocks = db.fetch_isin_symbol_from_db(symbol, sector)
        print("Stock List in the sector == "+str(stocks))
        for stock in stocks:
            self.get_intraday_OHLC_from_upstox_for_one_stock( stock[0], stock[1])

    # Intraday Candle OHLC
    def get_intraday_OHLC_from_upstox_for_one_stock(self, ISIN, symbol):
        url = Configuration.intraday_url
        reqParams = {}

        for tf_table_map in Configuration.timeframe_tablemap_for_intraday:
            timeframe = tf_table_map[0]
            finalurl = url + ISIN + "/" + timeframe
            responseJson = Utility.sentGetRequest(finalurl, Configuration.headers, reqParams)

            stockData = json.loads(responseJson)
            # print(stockData)
            header = ["Date", "Open", "High", "Low", "Close", "Volume", "OI"]
            tableName = tf_table_map[1]
            CommonServices.writeToDB(stockData, tableName, symbol)

            # if (dictionary['status'] == 'error'):
            #    print(dictionary)
            # else:
            #    candles = dictionary["data"]["candles"]
            #    Utility.writeToExcelFolder(Configuration.reportFolder+"intraday/",symbol+".xlsx",timeframe.replace('/','_'),[header]+candles)

