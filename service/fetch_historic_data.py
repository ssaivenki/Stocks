import time
import json

from service.common_service import CommonServices
from utility.utils import Utility
from utility.config import Configuration
from database.db_cache import get_db

class HistoricDataManager:
    def __init__(self):
        self.historic_candles_cache = {}
    allHistoricCandles ={}

    def get_historic_OHLC_from_upstox_for_sector(self, symbol: str = None, sector: str = None, candle_count:int  = 200):
        # Get all the stocks for the sector and call the
        db = get_db()
        stocks = db.fetch_isin_symbol_from_db(symbol, sector)
        # print("Stock List in the sector == " + str(stocks))
        for stock in stocks:
            self.get_historical_OHLC_from_upstox_for_one_stock(stock[0], stock[1],candle_count)

    def get_historic_OHLC_from_upstox_for_all_sector_one_timeframe(self, timeframe: str = 'days/1', candle_count: int = 300):

        print("\n\n Timeframe == "+timeframe)
        # Get the isin for the stock
        db = get_db()
        stocks = db.fetch_isin_symbol_from_db()

        fromDate, toDate = Utility.get_start_end_date_for_historic_data_fetch(timeframe, candle_count)
        for stock in stocks:
            self.getHistoricDataFromUpstoxForOneSymbol(stock[0], stock[1], timeframe, toDate, fromDate)


    def get_historic_OHLC_from_upstox_for_one_stock_one_timeframe(self, symbol:str = 'INFY', timeframe:str = "minutes/15", candle_count:int = 200):
        # Get the isin for the stock
        db = get_db()
        stocks = db.fetch_isin_symbol_from_db(symbol)
        print("Stock List in the sector == " + str(stocks))
        fromDate, toDate = Utility.get_start_end_date_for_historic_data_fetch(timeframe, candle_count)
        for stock in stocks:
            self.getHistoricDataFromUpstoxForOneSymbol(stock[0], symbol, timeframe,toDate,fromDate)

    def get_historical_OHLC_from_upstox_for_one_stock(self, ISIN, symbol, candle_count:int = 200):
        for tf_table_map in Configuration.all_timeframes_tablemap:
            timeframe = tf_table_map[0]
            finalurl = Configuration.historical_url + ISIN + "/" + timeframe
            fromDate, toDate = Utility.get_start_end_date_for_historic_data_fetch(timeframe, candle_count)
            # print("Symbol - " + symbol + "TF = "+timeframe + " From "+str(fromDate) + " to " + str(toDate))
            self.getHistoricDataFromUpstoxForOneSymbol(ISIN, symbol, timeframe,toDate,fromDate)

    def getHistoricDataFromUpstoxForOneSymbol(self, ISIN, symbol, timeframe,toDate,fromDate):
        print("\n\n Inside getHistoricDataFromUpstoxForOneSymbol  Timeframe == " + timeframe)

        url = Configuration.historical_url + ISIN + "/" + timeframe + "/" + str(toDate) + "/" + str(fromDate)
        # print("\n\n" + "Url = " + url + "\n")
        responseJson = Utility.sentGetRequest(url,Configuration.headers)

        dataJson = json.loads(responseJson)
        if dataJson["status"] == 'error':
            print(dataJson)
            if dataJson["errors"][0]['errorCode'] == 'UDAPI10005':
                time.sleep(15)
                return self.getHistoricDataFromUpstoxForOneSymbol(ISIN,symbol,timeframe,toDate,fromDate)
        else:
            tableName = Utility.getTableForTimeFrame(timeframe)
            print(dataJson)

            # print("Write to the table "+ str(tableName) + "Symbol = "+str(symbol) )
            CommonServices.writeToDB(dataJson, tableName, symbol)
            candles = dataJson["data"]["candles"]

            return candles

    def getHistoricDataFromUpstox(self,  timeframe, toDate, fromDate, forceUpdate, noOfCandles):
        # Force Reading from Upstox

        if (forceUpdate == "1"):
            instruments = Utility.readFromFile(Configuration.rootFolder+"data/symbolInfo.txt")
            historicCandles = {}
        

            for record in instruments:
                ISIN = record["ISIN"]
                symbol = record["Symbol"]
                # print(ISIN+"_"+record["Symbol"])
            
                candles = self.getHistoricDataFromUpstoxForOneSymbol(ISIN, symbol, headers,timeframe,toDate,fromDate)

                if (candles != None):
                    historicCandles[ISIN] = candles
            #Utility.writeToFile(Configuration.dataFolder+"HistoricData_"+timeframe+".txt",historicCandles)
            self.allHistoricCandles["HistoricData_"+timeframe] = historicCandles
            return historicCandles
        # If we have it in the cache, then take it from there
        # Else if we have it in File, then take it from there
        # Else go to the Upstox
        else:
            try:
                historicCandles = self.allHistoricCandles["HistoricData_"+timeframe]
                if (self.allHistoricCandles != None):
                    return historicCandles
            except:

                historicCandles = Utility.readFromFile1(Configuration.dataFolder+"HistoricData_"+timeframe+".txt",noOfCandles)
                if (historicCandles != None):
                    self.allHistoricCandles["HistoricData_"+timeframe] = historicCandles
                    return historicCandles
                else:
                    return self.getHistoricDataFromUpstox(headers,timeframe,toDate,fromDate,1,noOfCandles)

    # Historical data - Check if it is locally available. If not get from upstox
    def getHistoricData(self,  symbol, timeframe,toDate, fromDate, forceUpdate, noOfCandles):
        historicCandles = self.getHistoricDataFromUpstox(timeframe,toDate,fromDate,forceUpdate,noOfCandles)
        if symbol in historicCandles:
            return historicCandles[symbol]
        else:
            return None

    def getClosePrice(self, symbol: str, table, start_date:str, end_date:str = None):
        # Get the data from the right table for the timeframe and Symbol for the duration
        db = get_db()
        stock_data = db.fetch_stock_price_from_db(table, symbol, start_date, end_date)

        closePrice = [row[5] for row in stock_data]
        # print("\nClose Price for " + symbol + " == " + str(closePrice) + "\n")

        return closePrice

    def fetch_n_candles_close_prices_from_db(self, symbol: str, table: str, candle_count:int = 200):
        db = get_db()
        stock_data = db.fetch_n_candles_stock_prices_from_db(table, symbol, candle_count)
        closePrice = [row[5] for row in stock_data]
        dates = [row[1] for row in stock_data]
        # print("\nClose Price for " + symbol + " == " + str(closePrice) + "\n")

        return closePrice,dates

    def fetch_n_candles_stock_prices_from_db(self, symbol: str, table: str, candle_count:int = 200):
        db = get_db()
        stock_data = db.fetch_n_candles_stock_prices_from_db(table, symbol, candle_count)
        print("Inside fetch_n_candles_stock_prices_from_db Table = "+table + " Symbol = "+symbol)
        # print(stock_data)
        return stock_data

    def update_historic_price_all_sector_all_tf(self, no_of_candles = 400):
        '''
        For all the sectors, update the price data for all the timeframes
        :param no_of_candles: No of candles to get
        :return:
        '''
        # Get all the instruments from DB
        db = get_db()
        instruments = db.fetch_isin_symbol_from_db()

        # For each instrument, update the candle data from upstox for all timeframe to DB

