import mysql.connector
from typing import List, Union, Tuple


class StockDatabase:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish a database connection."""
        if not self.conn:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()

    def close(self):
        """Close cursor and connection."""

        if self.conn:
            self.conn.close()
            self.conn = None

    def upsert_stock_data(self, records: List[List[Union[str, float, int]]],table_name):
        """
        Inserts or updates multiple stock data records into the 'stocks_1m' table.

        Each record should be a list:
        [symbol (str), date (str or datetime), open (float), high (float),
         low (float), close (float), volume (int), oi (int)]
        """
        try:
            self.connect()
            query = f"""
            INSERT INTO `{table_name}` (symbol, date, open, high, low, close, volume, oi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                oi = VALUES(oi);
            """
            self.cursor.executemany(query, records)
            self.conn.commit()
            print(f"{self.cursor.rowcount} rows inserted/updated.")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
        finally:
            self.close()

    def fetch_stock_data(self, table: str, symbol: str, start_date: str, end_date: str) -> List[Tuple]:
        """
        Fetch stock data for a given symbol and date range.

        Parameters:
            table (str): From which table to fetch
            symbol (str): Stock symbol
            start_date (str): Start date in 'YYYY-MM-DD HH:MM:SS' format
            end_date (str): End date in 'YYYY-MM-DD HH:MM:SS' format

        Returns:
            List of tuples containing rows of stock data.
        """
        try:
            self.connect()
            query = f"""
            SELECT symbol, date, open, high, low, close, volume, oi
            FROM `{table}`
            WHERE symbol = %s AND date BETWEEN %s AND %s
            ORDER BY date DESC
            """
            self.cursor.execute(query, (symbol, start_date, end_date))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            self.close()
