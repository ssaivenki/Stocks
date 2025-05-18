CREATE TABLE report_territory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20),
    sector VARCHAR(50),
    timeframe VARCHAR(20),
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    guy_who_started TIMESTAMP,
    territory_value FLOAT,
    territory VARCHAR(20),
    UNIQUE(symbol,timeframe)
);