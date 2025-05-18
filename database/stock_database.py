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

    def close(self) -> object:
        """Close cursor and connection."""

        if self.conn:
            self.conn.close()
            self.conn = None

    def upsert_stock_price_data(self, records: List[List[Union[str, float, int]]], table_name):
        """
        Inserts or updates multiple stock price data records into the table.

        Each record should be a list:
        [symbol (str), date (str or datetime), open (float), high (float),
         low (float), close (float), volume (int), oi (int)]
        """
        try:
            print("\nInside upsert_stock_price_data --- \n\n"+table_name +"\n\n")
            print(records[0])
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

    def fetch_stock_price_from_db(self, table: str, symbol: str, start_date: str, end_date: str = None) -> List[Tuple]:
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
            if end_date == None:
                date_comparison = " date > %s "
            else:
                date_comparison = " date BETWEEN %s AND %s "
            query = f"""
            SELECT symbol, date, open, high, low, close, volume, oi
            FROM `{table}`
            WHERE symbol = %s AND `{date_comparison}`
            ORDER BY date DESC
            """
            if end_date == None:
                self.cursor.execute(query, (symbol, start_date))
            else:
                self.cursor.execute(query, (symbol, start_date, end_date))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            self.close()

    def load_stocks_isin_symbol(self, data):

        try:
            self.connect()
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                isin VARCHAR(50),
                symbol VARCHAR(20),
                sector VARCHAR(50),
                UNIQUE(isin,symbol)
            )
            """)

            # Prepare data as a list of tuples
            values = [(item["ISIN"], item["Symbol"], item.get("Sector", None)) for item in data]
            # Insert or update
            query = """
                INSERT INTO stocks (isin, symbol, sector)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    sector = VALUES(sector)
            """
            self.cursor.executemany(query, values)

            self.conn.commit()
            print(f"{self.cursor.rowcount} rows inserted/updated.")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
        finally:
            self.close()

    def fetch_stocks_isin_symbol(self, sector: str = None) -> List[Tuple]:
        """
        Fetch stock metadata (ISIN, Symbol, Sector) optionally filtered by sector.

        Parameters:
            sector (str, optional): Filter stocks by sector (e.g., 'Bank', 'IT')

        Returns:
            List of tuples containing (ISIN, Symbol, Sector)
        """
        try:
            self.connect()
            if sector:
                query = """
                SELECT isin, symbol, sector
                FROM stocks
                WHERE sector = %s
                ORDER BY symbol
                """
                self.cursor.execute(query, (sector,))
            else:
                query = """
                SELECT isin, symbol, sector
                FROM stocks
                ORDER BY symbol
                """
                self.cursor.execute(query)

            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            self.close()
