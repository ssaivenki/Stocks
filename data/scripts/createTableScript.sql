-- Minute-level data
CREATE TABLE stocks_1m (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- 5-minute data
CREATE TABLE stocks_5m (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- 15-minute data
CREATE TABLE stocks_15m (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- Hourly data
CREATE TABLE stocks_1h (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- Daily data
CREATE TABLE stocks_day (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- Weekly data
CREATE TABLE stocks_week (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);

-- Monthly data
CREATE TABLE stocks_month (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume INT,
    oi INT,
    UNIQUE(symbol, date)
);


CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isin VARCHAR(50),
    symbol VARCHAR(20),
    sector VARCHAR(50),
    UNIQUE(isin,symbol)
);