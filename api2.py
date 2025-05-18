
from upstox_api.api import *
from datetime import timedelta
from pprint import pprint
import sys
from tempfile import gettempdir
import requests
import json
import os
import pandas as pd

from service.range_calculator import RangeCalculator
from service.fetch_historic_data import HistoricDataManager
from service.fetch_intraday_data import IntradayDataManager
from utility.utils import Utility
from utility.config import Configuration
from database.db_cache import get_db
from service.instrument import Instrument
from service.reports_service import Reports
from service.support_resistance import SupportResistance
from service.trend_analyzer import TrendAnalyzer


class App:


    # Return positive Value (How much of breakout) if the first candle high is broken by the second candle close
    # Return negative Value (How much of breakdown) if the first candle low is broken by the second candle close 
    # Return 0 Otherwise 
    def findBreakOutOrDown(candle1, candle2):
        retVal = 0
        if (candle1[2] < candle2[4]):
            retVal = candle2[4] - candle1[2]
            print("Breakout")
        elif (candle1[3] > candle2[4]):
            retVal = candle2[4] - candle1[3]
            print("BreakDown")
        return retVal

    def findBreakOutOrDownForAllInstruments():
        instruments = readFromFile(rootFolder+"data/symbolInfo.txt")
    

        reqParams = {}
        timeframe1 = "1minute"
        
        toDate=date.today()
        fromDate="2023-05-07"
        timeframe2="day"
        listOfBreakOuts = []
        listOfBreakDowns = []
        
        historicCandles = {}
        index = 0
        for record in instruments:
            ISIN = record["ISIN"]      
            print(ISIN+"_"+record["Symbol"])
    
            intradayCandles_1minute = getIntradayOHLC(headers,reqParams,ISIN,timeframe1)
            historicCandles_day = getHistoricData(headers,reqParams,ISIN,timeframe2,toDate,fromDate)
    
            if (intradayCandles_1minute != None and historicCandles_day != None) :
                # OHLCV
                symbolInfo = {}
                symbolInfo["candles"] = historicCandles_day
                symbolInfo["Name"] = instrumentNameList[index]
    
                historicCandles[symbol] = symbolInfo
                breakOuts = {} 
                breakOutStatus = findBreakOutOrDown(historicCandles_day[0],intradayCandles_1minute[0])
                if (breakOutStatus > 0):
                    breakOuts["name"] = instrumentNameList[index]
                    breakOuts["value"] = breakOutStatus
                    listOfBreakOuts.append(breakOuts)
                elif (breakOutStatus < 0):
                    breakOuts["name"] = instrumentNameList[index]
                    breakOuts["value"] = breakOutStatus
                    listOfBreakDowns.append(breakOuts)
                print(historicCandles_day[0],intradayCandles_1minute[0])
                print(breakOutStatus)    
        
        writeToFile(rootFolder+"data/historicCandles_1Day.txt", historicCandles)    
            
            
        
        BOAndBD = {}
        BOAndBD["listOfBreakOuts"] = listOfBreakOuts
        BOAndBD["listOfBreakDowns"] = listOfBreakDowns

        print("List of BreakOuts/Downs are ",BOAndBD)

    def findTrend(candles, remarks):
        length = len(candles)
        finalClose = candles[0][4]
        closeDiffArr = []
        for i in range(1, length - 1):
            close = round(finalClose - candles[i][4],2)
            closeDiffArr.append(close)

        #print(remarks,":::::",closeDiffArr)
        return closeDiffArr
    '''
    def getMinMaxValue(candles):
        
        
        # Initialize min to first candle Low and max to first candle high 
        minVal = candles[0][3]
        maxVal = candles[0][2]
        minCloseVal = candles[0][4]
        maxCloseVal = candles[0][4]
        
        for candle in candles:
            if minVal > candle[3]:
                minVal = candle[3]
            
            if maxVal < candle[2]:
                maxVal = candle[2]


            

        return minVal, maxVal

    def getDiffWithMinMax(candles):
        diffWithMin = []
        diffWithMax = []

        minVal, maxVal = getMinMaxValue(candles)
        for candle in candles :
            diffWithMin.append(round(candle[4] - minVal,2))
            diffWithMax.append(round(maxVal - candle[4],2))

        return diffWithMin,diffWithMax



    def findMinMax(array):
        min = 0
        max = 0
        if len(array) > 0:
            min = array[0]
            max = array[0]
            for ele in array:
                if min > ele:
                    min = ele
                if max < ele:
                    max = ele
        return min, max

    '''
    def initializeParams(self):
        
        forceUpdate = 0
        cutoff = 25
        noOfDays = 200
        timeframe = "days/1"
        noOfCandles = 75

        if (len(sys.argv) > 1):
            forceUpdate = sys.argv[1]
            if (len(sys.argv) > 2):
                cutoff = (int)(sys.argv[2])
                if (len(sys.argv) > 3):
                    noOfDays = (int)(sys.argv[3])
                    if (len(sys.argv) > 4):
                        timeframe = sys.argv[4]
                        if (len(sys.argv) > 5):
                            noOfCandles = (int)(sys.argv[5])
        else:
            print("Run as py ./api2.py <forceUpdate> <cutoff> <noOfDays> <timeframe> <noOfCandles>")
            print("forceUpdate - 0 Means Not to fetch from UpStox 1 Means fetch from UpStox")
            print("cutoff - Current Price > cutoff % from Min or Max")
            print("noOfDays - No of days to go back")
            print("timeframe - Specifies the time frame of the candles. Possible values: 1minute, 30minute, day, week, month.")
            print("noOfCandles - No of Candles to go back. This is be less than or equal to noOfDays if day is selected")
            
            
        return forceUpdate, cutoff, noOfDays, timeframe, noOfCandles
    
    def getIntradayOHLCDataFromUpstox(self):
        reqParams = {}
        
        forceUpdate, cutoff, noOfDays, timeframe, noOfCandles = self.initializeParams()

        instruments = Utility.readFromFile(Configuration.dataFolder + Configuration.symbolsFileName)
        intradayCandles = {}
        intradayDM = IntradayDataManager()
        for record in instruments:
            ISIN = record["ISIN"]
            symbol = record["Symbol"]
            print(ISIN + "_" +symbol)
            intradayDM.get_intraday_OHLC_from_upstox_for_one_stock(reqParams, ISIN, symbol)

    def get_intraday_OHLC_from_upstox(self, symbol: str = None, sector: str = None):
        intraDM = IntradayDataManager()
        intraDM.get_intraday_OHLC_from_upstox_for_sector(symbol, sector)

    def get_historic_OHLC_from_upstox_for_sector(self, symbol: str = None, sector: str = None, candle_count:int = 100):
        histDM = HistoricDataManager()
        histDM.get_historic_OHLC_from_upstox_for_sector(symbol, sector, candle_count)

    def get_historic_OHLC_from_upstox_for_one_stock_one_timeframe(self, symbol:str = 'INFY', timeframe:str = "minutes/15", candle_count:int = 200):
        histDM = HistoricDataManager()
        histDM.get_historic_OHLC_from_upstox_for_one_stock_one_timeframe(symbol,timeframe,candle_count)

    def myMain(self, sector: str = None):
        #findBreakOutOrDownForAllInstruments()
        


        forceUpdate, cutoff, noOfDays, timeframe, noOfCandles = self.initializeParams()

        toDate = date.today()
        toDate = toDate + timedelta(days = 1)
        fromDate = toDate - timedelta(days = int(noOfDays))

        # Read the instruments from the file
        # instruments = Utility.readFromFile(Configuration.dataFolder + Configuration.symbolsFileName)
        instruments = get_db().fetch_isin_symbol_from_db(sector)
        priority1List = []
        lowPriceList = []
        highPriceList = []
        for record in instruments:
            print("Processing for instrument "+record[1])
            ISIN = record[0]

            histDM = HistoricDataManager()
            candles = histDM.getHistoricData(Configuration.headers,ISIN,timeframe,str(toDate),str(fromDate),forceUpdate,noOfCandles)

            if candles is None:
                # Skip the Symbol processing
                print("Skipping the processing of Symbol ", record[1])
            else:
                # symbol = record["Symbol"]
                # tableName = Utility.getTableForTimeFrame(timeframe)
                # histDM.writeCandlesToDB(candles, tableName, symbol)
                totalCandlesCount: int = len(candles)
                print("Candle Count == ", totalCandlesCount, "From Date = ", fromDate, "To Date == ", toDate)
                
                # If sector key is present in the symbolInfo for this record, then write to the sector file
                if record[2] is not None:
                    # Write to the sector file sheet name should be the Symbol
                    header = ["Date","Open","High","Low","Close","Volume","OI"]
                    #Utility.writeToExcel(Configuration.reportFolder+record["Sector"]+"_"+timeframe+".xlsx", record["Symbol"],[header]+candles)

                closedRunningDiff = []
                for index in range(totalCandlesCount):
                    closeDiffArr = Utility.findTrend(candles[index:totalCandlesCount], "Diff between "+str(index)+" candle and rest "+candles[index][0][0:10])
                    if len(closeDiffArr) > 0:
                        closedRunningDiff.append(closeDiffArr[0])

                diffWithMinVal, diffWithMaxVal = Utility.getDiffWithMinMax(candles)
                minVal, maxVal = Utility.findMinMax(diffWithMinVal)
                minVal, maxVal = Utility.findMinMax(diffWithMaxVal)
                forceUpdate = 0

                currentCandleCloseVal = candles[0][4]
                currentCandleDiffWithMin = diffWithMinVal[0]
                currentCandleDiffWithMax = diffWithMaxVal[0]
                print("Symbol ==", record[1], " DiffWithMin == ", currentCandleDiffWithMin, " DiffWithMax = ", currentCandleDiffWithMax)
                
                currentCandleDiffWithMinRatio = round((currentCandleDiffWithMin/currentCandleCloseVal)*100, 2)
                currentCandleDiffWithMaxRatio = round((currentCandleDiffWithMax/currentCandleCloseVal)*100,2)

                if currentCandleDiffWithMinRatio > cutoff:
                    tup =(record[1],str(currentCandleDiffWithMinRatio),str(currentCandleDiffWithMaxRatio),candles[0][5])
                    priority1List.append(tup)
                    highPriceList.append(tup)
                if currentCandleDiffWithMaxRatio > cutoff:
                    tup =(record[1],str(currentCandleDiffWithMinRatio),str(currentCandleDiffWithMaxRatio),candles[0][5])
                    priority1List.append(tup)
                    lowPriceList.append(tup)

        print("High Priced Stocks")
        #Utility.writeToExcel(Configuration.reportFolder+"recommendations"+"_"+timeframe+".xlsx", "HighPrice",highPriceList)
        #Utility.writeToExcel(Configuration.reportFolder+"recommendations"+"_"+timeframe+".xlsx", "LowPrice",lowPriceList)
        
        for s in highPriceList :
            print(s,sep="\n\n")
        
        print("Low Priced Stocks")
        for s in lowPriceList :
            print(s,sep="\n\n")
            #print(minVal, maxVal)
            #if (currentCandleDiffWithMinRatio > 10 or currentCandleDiffWithMaxRatio > 10) :
            #    print("---------------------------------",record["Symbol"]+" Date Range - "+str(fromDate)+" -- "+str(toDate) + "Min Ratio == "+str(currentCandleDiffWithMinRatio)+" Max Ratio == "+str(currentCandleDiffWithMaxRatio),"Diff from Min  "+str(diffWithMinVal), "Diff from Max  "+str(diffWithMaxVal), sep="\n\n")

    ##################################################

    def main():
        global s, u

        logged_in = False

        print('Welcome to Upstox API!\n')
        print('This is an interactive Python connector to help you understand how to get connected quickly')
        print('The source code for this connector is publicly available')
        print('To get started, please create an app on the Developer Console (developer.upstox.com)')
        print('Once you have created an app, keep your app credentials handy\n')

        stored_api_key = read_key_from_settings('api_key')
        stored_access_token = read_key_from_settings('access_token')
        if stored_access_token is not None and stored_api_key is not None:
            print('You already have a stored access token: [%s] paired with API key [%s]' % (stored_access_token, stored_api_key))
            print('Do you want to use the above credentials?')
            selection = input('Type N for no, any key for yes:  ')
            if selection.lower() != 'n':
                try:
                    u = Upstox(stored_api_key, stored_access_token)
                    logged_in = True
                except requests.HTTPError as e:
                    print('Sorry, there was an error [%s]. Let''s start over\n\n' % e)

        if logged_in is False:
            stored_api_key = read_key_from_settings('api_key')
            if stored_api_key is not None:
                api_key = input('What is your app''s API key [%s]:  ' %  stored_api_key)
                if api_key == '':
                    api_key = stored_api_key
            else:
                api_key = input('What is your app''s API key:  ')
            write_key_to_settings('api_key', api_key)

            stored_api_secret = read_key_from_settings('api_secret')
            if stored_api_secret is not None:
                api_secret = input('What is your app''s API secret [%s]:  ' %  stored_api_secret)
                if api_secret == '':
                    api_secret = stored_api_secret
            else:
                api_secret = input('What is your app''s API secret:  ')
            write_key_to_settings('api_secret', api_secret)

            stored_redirect_uri = read_key_from_settings('redirect_uri')
            if stored_redirect_uri is not None:
                redirect_uri = input('What is your app''s redirect_uri [%s]:  ' %  stored_redirect_uri)
                if redirect_uri == '':
                    redirect_uri = stored_redirect_uri
            else:
                redirect_uri = input('What is your app''s redirect_uri:  ')
            write_key_to_settings('redirect_uri', redirect_uri)

            s = Session(api_key)
            s.set_redirect_uri(redirect_uri)
            s.set_api_secret(api_secret)

            print('\n')

            print('Great! Now paste the following URL on your browser and type the code that you get in return')
            print('URL: %s\n' % s.get_login_url())

            input('Press the enter key to continue\n')

            code = input('What is the code you got from the browser:  ')

            s.set_code(code)
            try:
                access_token = s.retrieve_access_token()
            except SystemError as se:
                print('Uh oh, there seems to be something wrong. Error: [%s]' % se)
                return
            write_key_to_settings('access_token', access_token)
            u = Upstox(api_key, access_token)

        clear_screen()
        show_home_screen()
    '''
    def sentGetRequest(url, headers, requestParams):

        # Make a GET request with headers and parameters
        response = requests.get(url, headers=headers, params=requestParams)
        
        print("======================")

        return response.text
    '''
    def show_home_screen(self):
        # global s, u
        # global profile

        print('\n*** Welcome to Upstox API ***\n\n')
        print('1. Get Historic Price for all Symbols for all Timeframe\n')
        print('2. Get Intraday Price for all Symbols for intraday Timeframe  \n')
        print('3. Find 1 day Territories for all stocks and Load in DB\n')
        print('4. Find 75m Territories for all stocks and Load in DB\n')
        print('5. Find 15m Territories for all stocks and Load in DB\n')
        print('6. Find 5m Territories for all stocks and Load in DB\n')
        print('7. Find 5m Territories for one stock and Load in DB\n')
        print('8. Find 15m Territories for one stock and Load in DB\n')
        print('9. Get Historic Price for one Symbols for 5m Timeframe\n')
        print('10. Get Historic Price for all Symbols for one TimeFrame\n')

        selection = input('Select your option: \n')
        
        try:
            int(selection)
        except:
            self.clear_screen()
            self.show_home_screen()

        selection = int(selection)
        self.clear_screen()
        if selection == 1:
            self.get_historic_OHLC_from_upstox_for_sector()
            # pprint(profile)
        elif selection == 2:
            self.get_intraday_OHLC_from_upstox()
        elif selection == 3:
            self.find_territories_for_all_sectors()
        elif selection == 4:
            self.find_territories_for_all_sectors('minutes/75')
        elif selection == 5:
            self.find_territories_for_all_sectors('minutes/15')
        elif selection == 6:
            self.find_territories_for_all_sectors('minutes/5')
        #     if product is not None:
        #         pprint(u.get_live_feed(product, LiveFeedType.LTP))
        elif selection == 7:
            stock = input('Enter the Stock : \n')
            self.find_territories(stock, 'minutes/5')
        elif selection == 8:
            stock = input('Enter the Stock : \n')
            self.find_territories(stock, 'minutes/15')
        #     product = select_product()
        #     if product is not None:
        #         pprint(u.get_live_feed(product, LiveFeedType.Full))
        # elif selection == 8:
        #     socket_example()
        elif selection == 9:
            stock = input('Enter the Stock : \n')
            self.get_historic_OHLC_from_upstox_for_one_stock_one_timeframe(stock)
        elif selection == 10:
            candle_count = 200
            print("Type 1 for day")
            print("Type 2 for week")
            print("Type 3 for month")
            print("Type 4 for 75m")
            print("Type 5 for 15m")
            print("Type 6 for 5m")
            print("Type 7 for 1m")
            timeframe = 'days/1'

            choice = input('Enter the choice \n')

            try:
                int(choice)
                print("Choice == "+str(choice))
                choice = int(choice)
            except:
                self.clear_screen()
                self.show_home_screen()
            if choice == 1:
                timeframe = 'days/1'
                candle_count = 700
            elif choice == 2:
                timeframe = 'weeks/1'
                candle_count = 500
            elif choice == 3:
                timeframe = 'months/1'
                candle_count = 800

            elif choice == 4:
                timeframe = 'minutes/75'
                candle_count = 500
            elif choice == 5:
                timeframe = 'minutes/15'
                candle_count = 400
            elif choice == 6:
                timeframe = 'minutes/5'
            elif choice == 7:
                timeframe = 'minutes/1'
            else:
                timeframe = 'days/1'
            print("Inside home screen "+timeframe)
            HistoricDataManager().get_historic_OHLC_from_upstox_for_all_sector_one_timeframe(timeframe, candle_count)
        self.show_home_screen();


    def load_profile():
        global profile
        # load user profile to variable
        profile = u.get_profile()


    def select_product():
        global u
        exchange = select_exchange()
        product = None
        clear_screen()
        while exchange is not None:
            u.get_master_contract(exchange)
            product = find_product(exchange)
            clear_screen()
            if product is not None:
                break
            exchange = select_exchange()

        return product

    def find_product(exchange):
        found_product = False
        result = None

        while not found_product:
            query = input('Type the symbol that you are looking for. Type %s to go back:  ' % break_symbol)
            if query.lower() == break_symbol:
                found_product = True
                result = None
                break
            results = u.search_instruments(exchange, query)
            if len(results) == 0:
                print('No results found for [%s] in [%s] \n\n' % (query, exchange))
                break
            else:
                for index, result in enumerate(results):
                    if index > 9:
                        break
                    print ('%d. %s' % (index, result.symbol))
                selection = input('Please make your selection. Type %s to go back:  ' % break_symbol)

                if query.lower() == break_symbol:
                    found_product = False
                    result = None
                    break

                try:
                    selection = int(selection)
                except ValueError:
                    found_product = False
                    result = None
                    break

                if 0 <= selection <= 9 and len(results) >= selection + 1:
                    found_product = True
                    result = results[selection]
                    break

                found_product = False

        return result

    def select_exchange():
        global profile
        if profile is None:
            load_profile()

        back_to_home_screen = False
        valid_exchange_selected = False

        while not valid_exchange_selected:
            print('** Live quote streaming example **\n')
            for index, item in enumerate(profile[u'exchanges_enabled']):
                print ('%d. %s' % (index + 1, item))
            print ('9. Back')
            print('\n')

            selection = input('Select exchange: ')

            try:
                selection = int(selection)
            except ValueError:
                break

            if selection == 9:
                valid_exchange_selected = True
                back_to_home_screen = True
                break

            selected_index = selection - 1

            if 0 <= selected_index < len(profile[u'exchanges_enabled']):
                valid_exchange_selected = True
                break

        if back_to_home_screen:
            return None

        return profile[u'exchanges_enabled'][selected_index]


    def socket_example():
        print('Press Ctrl+C to return to the main screen\n')
        u.set_on_quote_update(event_handler_quote_update)
        u.get_master_contract('NSE_EQ')
        try:
            u.subscribe(u.get_instrument_by_symbol('NSE_EQ', 'TATASTEEL'), LiveFeedType.Full)
        except:
            pass
        try:
            u.subscribe(u.get_instrument_by_symbol('NSE_EQ', 'RELIANCE'), LiveFeedType.LTP)
        except:
            pass
        u.start_websocket(False)


    def event_handler_quote_update(message):
        pprint("Quote Update: %s" % str(message))

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def write_key_to_settings(key, value):
        filename = os.path.join(gettempdir(), 'interactive_api.json')
        try:
            file = open(filename, 'r')
        except IOError:
            data = {"api_key" : "", "api_secret" : "", "redirect_uri" : "", "access_token" : ""}
            with open(filename, 'w') as output_file:
                json.dump(data, output_file)
        file = open(filename, 'r')
        try:
            data = json.load(file)
        except:
            data = {}
        data[key] = value
        with open(filename, 'w') as output_file:
            json.dump(data, output_file)

    def read_key_from_settings(key):
        print("Dir = "+gettempdir())
        filename = os.path.join(gettempdir(), 'interactive_api.json')
        try:
            file = open(filename, 'r')
        except IOError:
            file = open(filename, 'w')
        file = open(filename, 'r')
        try:
            data = json.load(file)
            return data[key]
        except:
            pass
        return None

    def load_stocks_isin_symbol(self):
        instrument.load_stocks_isin_symbol()

    def get_close_price(self,symbol: str, table: str, stare_date: str, end_date: str = None):
        histDM = HistoricDataManager()
        close_price = histDM.getClosePrice(symbol,table, stare_date, end_date)

    def fetch_n_candles_close_prices_from_db(self, symbol: str, table: str, candle_count:int = 200):
        histDM = HistoricDataManager()
        close_price, dates  = histDM.fetch_n_candles_close_prices_from_db(symbol, table, candle_count)
        return close_price, dates

    def check_for_consolidation(self, candles_with_atr_ratio):
        # How many candles have range_atr_ration less than 1
        counter = 0
        for range_atr in candles_with_atr_ratio['range_atr_ratio']:
            if range_atr < 1:
                counter += 1
            else:
                break
        # print("No of consolidation candles == "+ str(counter))

        return counter

    def find_atr_for_all_sectors(self,timeframe:str = "days/1", no_of_candles:int = 50):
        # Get all sectors
        all_sectors = Instrument().fetch_all_sectors()

        atr_df = pd.DataFrame()
        consolidation_candle_count = pd.DataFrame(columns = ["Stock", "Consolidation Candle Count"])
        # Call find_atr_for_sector iterating through each sector
        for sector in all_sectors["Sector"]:
            atrs, consolidation_count = self.find_atr_for_sector(sector,timeframe, no_of_candles)
            consolidation_candle_count = pd.concat([consolidation_candle_count, consolidation_count], ignore_index=True)
            # Concatenate each returned df
            atr_df = pd.concat([atr_df, atrs], ignore_index=True)

        Utility.delete_file(Configuration.reportFolder+Configuration.report_file_name)

        Utility.write_dataframe_to_excel({
            "atr": atr_df,
            "consolidation_count": consolidation_candle_count
        }, Configuration.reportFolder + Configuration.report_file_name)
        return atr_df, consolidation_candle_count

    def find_atr_for_sector(self, sector: str = "IT", timeframe:str = "days/1", no_of_candles:int = 50):
        instruments = Instrument().get_sector_instruments(sector)

        data_frame = pd.DataFrame(columns = ["Sector","Stock", "Consolidation Candle Count"])
        atr_df = pd.DataFrame()
        for instrument in instruments:
            df, consolidation_candle_count = self.find_atr(instrument[1], timeframe, no_of_candles)
            data_frame.loc[len(data_frame)] = [sector, instrument[1],consolidation_candle_count]
            # Concatenate each returned df
            atr_df = pd.concat([atr_df, df], ignore_index=True)
        return atr_df, data_frame

    def find_atr(self, symbol:str = "INFY", timeframe:str = "days/1", no_of_candles:int = 100):
        table = Utility.getTableForTimeFrame(timeframe)
        stock_prices = app.fetch_n_candles_stock_prices_from_db(symbol, table, no_of_candles)
        df = RangeCalculator.find_ATR(stock_prices)
        consolidation_candle_count = self.check_for_consolidation(df)
        return df, consolidation_candle_count



    def fetch_n_candles_stock_prices_from_db(self, symbol: str, table: str, candle_count:int = 200):
        histDM = HistoricDataManager()
        stock_price  = histDM.fetch_n_candles_stock_prices_from_db(symbol, table, candle_count)
        return stock_price

    def find_territories(self,symbol: str = 'INFY', timeframe: str = 'days/1', no_of_candles:int = 100):
        result = app.find_atr(symbol, timeframe, no_of_candles)
        if result[0].empty:
            print("\n\nThere is no records for "+ symbol+ " in the timeframe table\n")
            result = {}
        else:
            modified_result = Utility.add_actual_open(result[0])
            Utility.add_actual_low_high(modified_result)
            Utility.add_A_minus_B(modified_result, "close", "actual_open", new_col_name='direction')
            # print(modified_result[
            #           ["datetime", "open", "close", "actual_open", "actual_high", "actual_low", 'atrvalue', "range",
            #            "direction"]].head(30))

            result = Utility.find_sellers_buyers_territory(modified_result)
            print(modified_result[
                      ["datetime", "open", "close", "actual_open", "actual_high", "actual_low", 'atrvalue', "range",
                       "direction"]].head(30))

            results = SupportResistance().analyze_structure_breaks(modified_result, window=2, lookahead=5)

            for r in results:
                print(r)
                # print(f"{r['type'].upper()} @ idx {r['level_index']} ₹{r['level_price']}: "
                #       f"{'BREACHED' if r['breached'] else 'NOT breached'} "
                #       f"{'breach ₹{'r['breach_price']} at {r['breach_time']}' if r['breached'] else ''} "
                #         f"{f'→ {r['follow_through_count']} candles, move ₹{r['cumulative_move']}' if r['breached'] else ''}")
        return result

    def find_territories_for_sector(self, sector: str = 'IT', timeframe:str = 'days/1', no_of_candles:int = 100):
        instruments = Instrument().get_sector_instruments(sector)
        print('\nfind_territories_for_sector === '+ sector +'\n\n Instruments == ')
        print(instruments)


        columns = ['Symbol','actual_open', 'close', 'actual_high', 'actual_low',
                   'guy_who_started_index', 'guy_who_started_date', 'territory_value','territory']

        df = pd.DataFrame(columns=columns)
        for instrument in instruments:
            result = self.find_territories(instrument[1], timeframe, no_of_candles)

            if len(result) == 0:
                print("\n\nSkipping Symbol === " + instrument[1])
            else:
                result['symbol'] = instrument[1]
                result['timeframe'] = timeframe

                df = pd.concat([pd.DataFrame([result]), df], ignore_index=True)


        # print("Final Result == ")
        # print(df)
        #df.to_excel(sector+".xlsx", sheet_name=sector,  index=False)
        return df

    def find_territories_for_all_sectors(self, timeframe:str = 'days/1', no_of_candles:int = 100):
        # Get all sectors
        all_sectors = Instrument().fetch_all_sectors()

        print("\n\n All Sectors == "+ str(len(all_sectors)))
        print(all_sectors)

        dictionary = {}

        # Call find_territories_for_sector iterating through each sector
        for sector in all_sectors["Sector"]:
            if sector != 'Index' and sector is not None:
                #if sector == 'FinancialServices':
                df = self.find_territories_for_sector(sector, timeframe, no_of_candles)
                if df.empty:
                    print("For the sector "+ sector + "df is empty")
                else:
                    df['sector'] = sector
                    dictionary[sector] = df
                    # Write all DataFrames to DB
                    df = df.rename(columns={"actual_open": "open", 'actual_high': 'high', 'actual_low': 'low',
                                            'guy_who_started_date': 'guy_who_started'})
                    Reports().insert_or_update_dataframe(df)






        # with pd.ExcelWriter(Configuration.reportFolder+'sectors_output.xlsx', engine='openpyxl') as writer:
        #     for sheet, data in dictionary.items():
        #         data.to_excel(writer, sheet_name=sheet, index=False)



if __name__ == "__main__":
    #myMain()
    app = App()
    app.show_home_screen()
    #app.find_territories_for_sector('Bank')
    #app.find_territories_for_all_sectors()

    #app.myMain("IT")
    #app.get_intraday_OHLC_from_upstox("INFY")
    #app.get_intraday_OHLC_from_upstox(None,"IT")
    #app.get_intraday_OHLC_from_upstox()

    #app.get_historic_OHLC_from_upstox_for_sector("HAL")
    # app.get_historic_OHLC_from_upstox_for_sector(None,"IT")
    #app.get_historic_OHLC_from_upstox_for_sector()

    #app.get_close_price("INFY","stocks_day","2025-03-01","2025-05-02")
    #app.get_close_price("INFY", "stocks_day", "2025-03-01")

    # close_prices, dates = app.fetch_n_candles_close_prices_from_db("INFY", "stocks_1h", 40)
    # slopes_2 = TrendAnalyzer.rolling_slope_trend(close_prices, 2)
    # slopes_3 = TrendAnalyzer.rolling_slope_trend(close_prices, 3)
    # slopes_4 = TrendAnalyzer.rolling_slope_trend(close_prices, 4)
    # slopes_5 = TrendAnalyzer.rolling_slope_trend(close_prices, 5)
    # slopes_6 = TrendAnalyzer.rolling_slope_trend(close_prices, 6)
    # slopes_7 = TrendAnalyzer.rolling_slope_trend(close_prices, 7)
    # slopes_8 = TrendAnalyzer.rolling_slope_trend(close_prices, 8)
    # slopes_9 = TrendAnalyzer.rolling_slope_trend(close_prices, 9)
    # slopes_10 = TrendAnalyzer.rolling_slope_trend(close_prices, 10)
    # for price, slope_2, slope_3, slope_4,slope_5, slope_6, slope_7, slope_8, slope_9, slope_10, date in zip(close_prices, slopes_2, slopes_3, slopes_4, slopes_5, slopes_6, slopes_7, slopes_8, slopes_9, slopes_10, dates):
    #     print(f"{date} - {price:05.2f} {slope_2:05.2f} {slope_3:05.2f} {slope_4:05.2f} {slope_5:05.2f} {slope_6:05.2f} {slope_7:05.2f} {slope_8:05.2f} {slope_9:05.2f} {slope_10:05.2f}")

    # stock_prices = app.fetch_n_candles_stock_prices_from_db("INFY", "stocks_week", 100)
    # df, consolidation_candle_count = app.find_atr("INFY","days/1",100)
    # print(df[0:15])
    # print("Consolidation candles count == "+str(consolidation_candle_count))

    # all_timeframes_tablemap = [["minutes/1", "stocks_1m"], ["minutes/5", "stocks_5m"], ["minutes/15", "stocks_15m"], ["minutes/75", "stocks_75m"],["hours/1", "stocks_1h"],["days/1", "stocks_day"], ["weeks/1", "stocks_week"], ["months/1", "stocks_month"]]
    #####################################################
    # result = app.find_atr(symbol= 'INFY',timeframe="months/1")
    # modified_result = Utility.add_actual_open(result[0])
    # Utility.add_actual_low_high(modified_result)
    # Utility.add_candle_body_to_wick_ratio(modified_result)
    # Utility.add_upper_wick_lower_wick(modified_result)
    # Utility.add_upper_lower_wick_body_ratio(modified_result)
    # Utility.add_A_minus_shiftedB(modified_result, "open", "close", "gap_up_down")
    # Utility.add_A_minus_B(modified_result, "close", "actual_open", new_col_name='direction')
    # print(modified_result.columns)
    # print(modified_result[["datetime","open","close","actual_open","actual_high","actual_low", 'atrvalue', "range", "direction"]].head(30))

    # Utility.find_sellers_buyers_territory(modified_result)
    # print(modified_result[["datetime", "open", "close", "actual_open", "actual_high", "actual_low", 'atrvalue', "range",
    #                        "direction"]].head(30))
    #####################################################

    # atr_details_df, consolidation_candle_count_df = app.find_atr_for_sector(sector = "IT", timeframe = "minutes/5", no_of_candles = 100)
    # Utility.write_dataframe_to_excel({
    #         "atr": atr_details_df,
    #         "consolidation_count": consolidation_candle_count_df
    #     }, Configuration.reportFolder + "sample.xlsx")
    # print("Consolidation Count DF")
    # print(consolidation_candle_count_df)
    #
    # print("Atrs DF")
    # print(atr_details_df.tail(15))
    # print(atr_details_df.head(15))

    # print(Instrument().fetch_all_sectors())
    #app.find_atr_for_all_sectors()

    # print("Date == "+ str(stock_prices))
    # ranges = RangeCalculator.compute_candle_ranges_desc_sorted(stock_prices)
    # for range in ranges:
    #     print(range)



    # Load the ISIN and Symbol from the file to DB
    #app.load_stocks_isin_symbol()

    #app.analyzeTrend("IRCTC", "2024-03-27", "2025-05-30")
    #app.analyzeTrend("INFY", "2024-03-27", "2025-05-30")
