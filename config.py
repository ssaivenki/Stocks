
class Configuration:
    rootFolder = "C:/Users/saive/Sai/StockMarket/APICoding/"
    dataFolder = rootFolder+"data/"
    reportFolder = dataFolder+"Reports/"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJISjE1NzYiLCJqdGkiOiI2NTc1NTFlYjVkYzZlNTZlZGQ4MmM2ZjIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNBY3RpdmUiOnRydWUsInNjb3BlIjpbImludGVyYWN0aXZlIiwiaGlzdG9yaWNhbCJdLCJpYXQiOjE3MDIxODc0OTksImlzcyI6InVkYXBpLWdhdGV3YXktc2VydmljZSIsImV4cCI6MTcwMjI0NTYwMH0.mZ7_kHT8uv-9b1VoMC6v6m9Z8bz3SfYQQ5DKVB6MomQ" 

    headers = {"accept": "application/json", "Api-Version": "2.0", "Authorization": token }
    symbolsFileName = "symbolInfo.txt"
    timeframe_tablemap = [["minutes/1","stocks_1m"],["minutes/5","stocks_5m"],["minutes/15","stocks_15m"], ["hours/1","stocks_1h"], ["days/1","stocks_day"],["months/1","stocks_month"],["weeks/1","stocks_week"]]

    # Upstocks URL
    historical_url = "https://api.upstox.com/v3/historical-candle/"
    intraday_url = "https://api.upstox.com/v3/historical-candle/intraday/"

    # DB Credentials
    host = 'localhost'
    user = 'root'
    password = 'seqato123'
    database = 'stocks_db'