import time
import json
from utils import Utility
from config import Configuration
from stock_database import StockDatabase
from db_cache import get_db

class HistoricDataManager:
    def __init__(self):
        self.historic_candles_cache = {}
    allHistoricCandles ={}

    def getHistoricDataFromUpstoxForOneSymbol(self, ISIN, symbol, headers,reqParams,timeframe,toDate,fromDate):
        url = Configuration.historical_url

        timeframe = "days/1"
        url = url + ISIN + "/" + timeframe + "/" + toDate + "/" + fromDate
        responseJson = Utility.sentGetRequest(url,headers,reqParams)

        dataJson = json.loads(responseJson)
        if dataJson["status"] == 'error':
            print(dataJson)
            if dataJson["errors"][0]['errorCode'] == 'UDAPI10005':
                time.sleep(15)
                return self.getHistoricDataFromUpstoxForOneSymbol(ISIN,symbol,headers,reqParams,timeframe,toDate,fromDate)
        else:
            tableName = Utility.getTableForTimeFrame(timeframe)
            print("Write to the table "+ tableName + "Symbol = " + symbol)
            self.writeToDB(dataJson, tableName, symbol)
            candles = dataJson["data"]["candles"]

            return candles

    def getHistoricDataFromUpstox(self, headers, reqParams, timeframe, toDate, fromDate, forceUpdate, noOfCandles):
        # Force Reading from Upstox

        if (forceUpdate == "1"):
            instruments = Utility.readFromFile(Configuration.rootFolder+"data/symbolInfo.txt")
            historicCandles = {}
        

            for record in instruments:
                ISIN = record["ISIN"]
                symbol = record["Symbol"]
                print(ISIN+"_"+record["Symbol"])
            
                candles = self.getHistoricDataFromUpstoxForOneSymbol(ISIN, symbol, headers,reqParams,timeframe,toDate,fromDate)

                if (candles != None):
                    historicCandles[ISIN] = candles
            Utility.writeToFile(Configuration.dataFolder+"HistoricData_"+timeframe+".txt",historicCandles)
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
                    return getHistoricDataFromUpstox(headers,reqParams,timeframe,toDate,fromDate,1,noOfCandles)

    # Historical data - Check if it is locally available. If not get from upstox
    def getHistoricData(self, headers, reqParams, symbol, timeframe,toDate, fromDate, forceUpdate, noOfCandles):
        historicCandles = self.getHistoricDataFromUpstox(headers,reqParams,timeframe,toDate,fromDate,forceUpdate,noOfCandles)
        if symbol in historicCandles:
            return historicCandles[symbol]
        else:
            return None

    def writeToDB(self, stockData, tableName, symbol):
        if "data" in stockData:
            print("\n\n\n\nInside Writing to DB\n\n\n")
            candles = stockData["data"]["candles"]
            self.writeCandlesToDB(candles, tableName, symbol)

    def writeCandlesToDB(self, candles, tableName, symbol):
        if (len(candles) > 0):
            candles = [[symbol] + row for row in candles]
            print("Inside WriteCandlesToDB")
            print(candles)
            db = get_db()
            db.upsert_stock_data(candles, tableName)

    # Intraday Candle OHLC
    def getIntradayOHLC(self,headers,reqParams,ISIN,symbol):
        url = Configuration.intraday_url
        #timeframes = ["minutes/1","minutes/5","minutes/15", "hours/1"]
        #timeframes = ["minutes/1"]

        for tf_table_map in Configuration.timeframe_tablemap:

            timeframe = tf_table_map[0]
            finalurl = url+ISIN+"/"+timeframe
            responseJson = Utility.sentGetRequest(finalurl,headers,reqParams)
            
            stockData = json.loads(responseJson)
            print(stockData)
            header = ["Date","Open","High","Low","Close","Volume","OI"]
            tableName = tf_table_map[1]
            self.writeToDB(stockData,tableName,symbol)


            #if (dictionary['status'] == 'error'):
            #    print(dictionary)
            #else:
            #    candles = dictionary["data"]["candles"]
            #    Utility.writeToExcelFolder(Configuration.reportFolder+"intraday/",symbol+".xlsx",timeframe.replace('/','_'),[header]+candles)

        
