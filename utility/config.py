
class Configuration:
    rootFolder = "C:/Users/saive/Sai/StockMarket/APICoding/"
    dataFolder = rootFolder+"data/"

    reportFolder = dataFolder+"Reports/"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJISjE1NzYiLCJqdGkiOiI2NTc1NTFlYjVkYzZlNTZlZGQ4MmM2ZjIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNBY3RpdmUiOnRydWUsInNjb3BlIjpbImludGVyYWN0aXZlIiwiaGlzdG9yaWNhbCJdLCJpYXQiOjE3MDIxODc0OTksImlzcyI6InVkYXBpLWdhdGV3YXktc2VydmljZSIsImV4cCI6MTcwMjI0NTYwMH0.mZ7_kHT8uv-9b1VoMC6v6m9Z8bz3SfYQQ5DKVB6MomQ" 

    headers = {"accept": "application/json", "Api-Version": "2.0", "Authorization": token }
    symbolsFileName = "symbolInfo.txt"
    report_file_name = "reports.xlsx"

    timeframe_tablemap_for_historic_data = [["minutes/75", "stocks_75m"],["hours/1", "stocks_1h"],["days/1", "stocks_day"], ["weeks/1", "stocks_week"], ["months/1", "stocks_month"]]
    timeframe_tablemap_for_intraday = [["minutes/1", "stocks_1m"], ["minutes/5", "stocks_5m"], ["minutes/15", "stocks_15m"],["hours/1", "stocks_1h"], ["minutes/75", "stocks_75m"]]

    all_timeframes_tablemap = [["minutes/1", "stocks_1m"], ["minutes/5", "stocks_5m"], ["minutes/15", "stocks_15m"], ["minutes/75", "stocks_75m"],["hours/1", "stocks_1h"],["days/1", "stocks_day"], ["weeks/1", "stocks_week"], ["months/1", "stocks_month"]]
    #all_timeframes_tablemap =[["minutes/75", "stocks_75m"]]

    candle_checking_conditions = ["previous_high_less_than_current_close"]

    # Upstocks URL
    historical_url = "https://api.upstox.com/v3/historical-candle/"
    intraday_url = "https://api.upstox.com/v3/historical-candle/intraday/"

    # DB Credentials
    host = '127.0.0.1'
    user = 'root'
    password = 'seqato123'
    database = 'stocks_db'