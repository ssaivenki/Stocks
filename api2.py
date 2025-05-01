
from upstox_api.api import *
from datetime import datetime, timedelta
from pprint import pprint
import os, sys
from tempfile import gettempdir
import requests
import json
import os
from fetch_historic_data import HistoricDataManager
from utils import Utility
from config import Configuration
from db_cache import get_db
from trend_analyzer import TrendAnalyzer


class App:
    try: input = raw_input
    except NameError: pass

    u = None
    s = None

    break_symbol = '@'

    profile = None
    #rootFolder = "/home/seqlap29/Sai/Projects/upstox/new/"
    #rootFolder = "C:/Users/saive/Sai/StockMarket/APICoding/"
    #dataFolder = rootFolder+"data/"
    #reportFolder = dataFolder+"Reports/"
    #token = "Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJISjE1NzYiLCJqdGkiOiI2NTc1NTFlYjVkYzZlNTZlZGQ4MmM2ZjIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNBY3RpdmUiOnRydWUsInNjb3BlIjpbImludGVyYWN0aXZlIiwiaGlzdG9yaWNhbCJdLCJpYXQiOjE3MDIxODc0OTksImlzcyI6InVkYXBpLWdhdGV3YXktc2VydmljZSIsImV4cCI6MTcwMjI0NTYwMH0.mZ7_kHT8uv-9b1VoMC6v6m9Z8bz3SfYQQ5DKVB6MomQ" 

    #headers = {"accept": "application/json", "Api-Version": "2.0", "Authorization": token }

    #allHistoricCandles ={}
    '''
    def readFromFile1(fileName,noOfRecords):
        try:
            with open(fileName, "r") as f:
                my_dict = json.load(f)
                retValue = {}
                for symbol in my_dict:
                    listOfValues = (my_dict[symbol])[0:noOfRecords]
                    my_dict[symbol] = listOfValues
                    print("Inside readFromFile with noOfRecords = ",len(listOfValues))

                return my_dict
        except FileNotFoundError:
            print("File - "+fileName+" not found")

    #Reading from a file
    def readFromFile(fileName):
        try:
            with open(fileName, "r") as f:
                my_dict = json.load(f)
                return my_dict
        except FileNotFoundError:
            print("File - "+fileName+" not found")
        

    #Writing to a File
    def writeToFile(fileName, data):
        with open(fileName, "w") as f:
            json.dump(data, f)

    def writeToCSVFile(fileName, data):
        with open(fileName, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def writeToExcel(fileName, sheetName, data):
        # Check if file exists
        if os.path.exists(fileName):
            # If exists, load the workbook
            wb = load_workbook(fileName)
            print(f"Opened existing file: {fileName}")

        else:
            # If not exists, create a new workbook
            wb = Workbook()
            print(f"Created new file: {fileName}")
        
        # Get list of all sheet names
        sheets = wb.sheetnames

        # Check if a sheet exists

        if sheetName in sheets:
            sheet = wb[sheetName]
        else:
            sheet = wb.create_sheet(title=sheetName)    
        # Write data starting at row 1
        for row_idx, row_data in enumerate(data, start=1):
            for col_idx, value in enumerate(row_data, start=1):
                sheet.cell(row=row_idx, column=col_idx, value=value)
        wb.save(fileName)

    def getHistoricDataFromUpstoxForOneSymbol(symbol, headers,reqParams,timeframe,toDate,fromDate):
        url = "https://api-v2.upstox.com/historical-candle/"
        url = url +symbol+"/"+timeframe+"/"+toDate+"/"+fromDate
        responseJson = sentGetRequest(url,headers,reqParams)

        dataJson = json.loads(responseJson)
        if ( dataJson["status"] == 'error'):
            print(dataJson)
            if (dataJson["errors"][0]['errorCode'] == 'UDAPI10005'):
                time.sleep(15)
                return getHistoricDataFromUpstoxForOneSymbol(symbol,headers,reqParams,timeframe,toDate,fromDate,noOfCandles)
        else:
            candles = dataJson["data"]["candles"]
            return candles

    def getHistoricDataFromUpstox(headers,reqParams,timeframe,toDate,fromDate,forceUpdate,noOfCandles):
        # Force Reading from Upstox

        if (forceUpdate == "1"):
            instruments = readFromFile(rootFolder+"data/symbolInfo.txt")
            historicCandles = {}
        

            for record in instruments:
                ISIN = record["ISIN"]      
                print(ISIN+"_"+record["Symbol"])
            
                candles = getHistoricDataFromUpstoxForOneSymbol(ISIN, headers,reqParams,timeframe,toDate,fromDate)
                if (candles != None):
                    historicCandles[ISIN] = candles
            writeToFile(dataFolder+"HistoricData_"+timeframe+".txt",historicCandles)
            allHistoricCandles["HistoricData_"+timeframe] = historicCandles
            return historicCandles
        # If we have it in the cache, then take it from there
        # Else if we have it in File, then take it from there
        # Else go to the Upstox
        else:
            try:
                historicCandles = allHistoricCandles["HistoricData_"+timeframe]
                if (allHistoricCandles != None):
                    return historicCandles
            except:

                historicCandles = readFromFile1(dataFolder+"HistoricData_"+timeframe+".txt",noOfCandles)
                if (historicCandles != None):
                    allHistoricCandles["HistoricData_"+timeframe] = historicCandles
                    return historicCandles
                else:
                    return getHistoricDataFromUpstox(headers,reqParams,timeframe,toDate,fromDate,1,noOfCandles)



    #Historical data - Check if it is locally available. If not get from upstox
    def getHistoricData(headers,reqParams,symbol,timeframe,toDate,fromDate,forceUpdate,noOfCandles):
        historicCandles = getHistoricDataFromUpstox(headers,reqParams,timeframe,toDate,fromDate,forceUpdate,noOfCandles)
        if symbol in historicCandles:
            return historicCandles[symbol]
        else:
            return None
        


    # Intraday Candle OHLC
    def getIntradayOHLC(headers,reqParams,symbol,timeframe):
        url = "https://api.upstox.com/v3/historical-candle/intraday/"

        timeframe = "minutes/5"

        url = url+symbol+"/"+timeframe
        responseJson = sentGetRequest(url,headers,reqParams)
        
        dictionary = json.loads(responseJson)

        print(dictionary)

        if (dictionary['status'] == 'error'):
            print(dictionary)
        else:
            candles = dictionary["data"]["candles"]
            return candles
    '''
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
        timeframe = "day"
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
    
    def test(self):
        reqParams = {}
        
        forceUpdate, cutoff, noOfDays, timeframe, noOfCandles = self.initializeParams()

        instruments = Utility.readFromFile(Configuration.dataFolder + Configuration.symbolsFileName)
        intradayCandles = {}
        histDM = HistoricDataManager()
        for record in instruments:
            ISIN = record["ISIN"]
            symbol = record["Symbol"]
            print(ISIN + "_" +symbol)
            histDM.getIntradayOHLC(Configuration.headers,reqParams,ISIN,symbol)

    def analyzeTrend(self, table: str, symbol: str,start_date:str,end_date:str):
        db = get_db()
        stock_data = db.fetch_stock_data(table,symbol, start_date, end_date)
        print(stock_data)
        close_price = [item[5] for item in stock_data]

        close_slopes_10 = TrendAnalyzer.rolling_slope_trend(close_price,10)
        print(close_slopes_10)

        TrendAnalyzer.plot_best_fit_line(close_price[:10], "close_price_10")
        TrendAnalyzer.plot_best_fit_line(close_slopes_10[:30], "close_slopes_10")

        open_price = [item[2] for item in stock_data]
        open_slopes_10 = TrendAnalyzer.rolling_slope_trend(open_price, 10)
        print("\n open_slopes_10\n")
        print(open_slopes_10)
        close_slopes_20 = TrendAnalyzer.rolling_slope_trend(close_price,20)
        print("\n close_slopes_20\n")
        print(close_slopes_20)
        close_slopes_50 = TrendAnalyzer.rolling_slope_trend(close_price, 50)
        print("\n close_slopes_50\n")
        print(close_slopes_50)
        close_slopes_200 = TrendAnalyzer.rolling_slope_trend(close_price, 200)
        print("\n close_slopes_200\n")
        print(close_slopes_200)

    def myMain(self):
        #findBreakOutOrDownForAllInstruments()
        

        reqParams = {}
        forceUpdate, cutoff, noOfDays, timeframe, noOfCandles = self.initializeParams()

        toDate = date.today()
        toDate = toDate + timedelta(days = 1)
        fromDate = toDate - timedelta(days = int(noOfDays))

        # Read the instruments from the file
        instruments = Utility.readFromFile(Configuration.dataFolder + Configuration.symbolsFileName)
        priority1List = []
        lowPriceList = []
        highPriceList = []
        for record in instruments:
            print("Processing for instrument "+record["Symbol"])
            ISIN = record["ISIN"]

            histDM = HistoricDataManager()
            candles = histDM.getHistoricData(Configuration.headers,reqParams,ISIN,timeframe,str(toDate),str(fromDate),forceUpdate,noOfCandles)

            if candles is None:
                # Skip the Symbol processing
                print("Skipping the processing of Symbol ", record["Symbol"])
            else:
                # symbol = record["Symbol"]
                # tableName = Utility.getTableForTimeFrame(timeframe)
                # histDM.writeCandlesToDB(candles, tableName, symbol)
                totalCandlesCount: int = len(candles)
                print("Candle Count == ", totalCandlesCount, "From Date = ", fromDate, "To Date == ", toDate)
                
                # If sector key is present in the symbolInfo for this record, then write to the sector file
                if "Sector" in record:
                    # Write to the sector file sheet name should be the Symbol
                    header = ["Date","Open","High","Low","Close","Volume","OI"]
                    Utility.writeToExcel(Configuration.reportFolder+record["Sector"]+"_"+timeframe+".xlsx", record["Symbol"],[header]+candles)

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
                print("Symbol ==", record["Symbol"], " DiffWithMin == ", currentCandleDiffWithMin, " DiffWithMax = ", currentCandleDiffWithMax)
                
                currentCandleDiffWithMinRatio = round((currentCandleDiffWithMin/currentCandleCloseVal)*100, 2)
                currentCandleDiffWithMaxRatio = round((currentCandleDiffWithMax/currentCandleCloseVal)*100,2)

                if currentCandleDiffWithMinRatio > cutoff:
                    tup =(record["Symbol"],str(currentCandleDiffWithMinRatio),str(currentCandleDiffWithMaxRatio),candles[0][5])
                    priority1List.append(tup)
                    highPriceList.append(tup)
                if currentCandleDiffWithMaxRatio > cutoff:
                    tup =(record["Symbol"],str(currentCandleDiffWithMinRatio),str(currentCandleDiffWithMaxRatio),candles[0][5])
                    priority1List.append(tup)
                    lowPriceList.append(tup)

        print("High Priced Stocks")
        Utility.writeToExcel(Configuration.reportFolder+"recommendations"+"_"+timeframe+".xlsx", "HighPrice",highPriceList)
        Utility.writeToExcel(Configuration.reportFolder+"recommendations"+"_"+timeframe+".xlsx", "LowPrice",lowPriceList)
        
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
    def show_home_screen():
        global s, u
        global profile

        print('\n*** Welcome to Upstox API ***\n\n')
        print('1. Get Profile\n')
        print('2. Get Balance\n')
        print('3. Get Positions\n')
        print('4. Get Holdings\n')
        print('5. Get Order History\n')
        print('6. Get LTP Quote\n')
        print('7. Get Full Quote\n')
        print('8. Show socket example\n')
        print('9. Quit\n')
        selection = input('Select your option: \n')
        
        try:
            int(selection)
        except:
            clear_screen()
            show_home_screen()

        selection = int(selection)
        clear_screen()
        if selection == 1:
            load_profile()
            pprint(profile)
        elif selection == 2:
            pprint(u.get_balance())
        elif selection == 3:
            pprint(u.get_positions())
        elif selection == 4:
            pprint(u.get_holdings())
        elif selection == 5:
            pprint(u.get_order_history())
        elif selection == 6:
            product = select_product()
            if product is not None:
                pprint(u.get_live_feed(product, LiveFeedType.LTP))
        elif selection == 7:
            product = select_product()
            if product is not None:
                pprint(u.get_live_feed(product, LiveFeedType.Full))
        elif selection == 8:
            socket_example()
        elif selection == 9:
            sys.exit(0)
        show_home_screen();


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

    def clear_screen():
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



if __name__ == "__main__":
    #myMain()
    app = App()
    #app.myMain()
    #app.test()

    app.analyzeTrend("stocks_day", "INFY", "2024-03-27", "2025-05-01")
    app.analyzeTrend("stocks_day", "HDFCBANK", "2024-03-27", "2025-05-01")
