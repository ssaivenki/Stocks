import mysql.connector
from typing import List, Union, Tuple
import pandas as pd


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
        """Ensure the connection is active and initialize the cursor."""
        try:
            if not self.conn or not self.conn.is_connected():
                self.conn = mysql.connector.connect(
                    **self.config,
                    connection_timeout=5,
                    use_pure=True,
                    unix_socket=None
                )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            self.conn = None
            self.cursor = None
        except Exception as ex:
            print("General Error:", ex)
            self.conn = None
            self.cursor = None


    def close(self) -> object:
        """Close cursor and connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
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
            # print("\nInside upsert_stock_price_data --- \n\n"+table_name +"\n\n")
            # print(records[0])
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
                query = f"""
                SELECT symbol, date, open, high, low, close, volume, oi
                FROM `{table}`
                WHERE symbol = %s AND  date > %s 
                ORDER BY date DESC
                """
                self.cursor.execute(query, (symbol, start_date))
            else:
                query = f"""
                SELECT symbol, date, open, high, low, close, volume, oi
                FROM `{table}`
                WHERE symbol = %s AND  date BETWEEN %s AND %s 
                ORDER BY date DESC
                """
                self.cursor.execute(query, (symbol, start_date, end_date))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            self.close()

    def fetch_n_candles_stock_prices_from_db(self, table: str, symbol: str, candle_count:int = 200) -> List[Tuple]:
        """
        Fetch up to 20 stock data records for a given symbol where date is strictly after start_date.

        Parameters:
            table (str): From which table to fetch
            symbol (str): Stock symbol
            candle_count (int): Number of records (candles) to retrieve

        Returns:
            List of tuples containing up to candle_count rows of stock data.
        """
        try:
            self.connect()
            query = f"""
            SELECT symbol, date, open, high, low, close, volume, oi
            FROM `{table}`
            WHERE symbol = %s 
            ORDER BY date DESC
            LIMIT %s
            """
            self.cursor.execute(query, (symbol, candle_count))
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

    def fetch_isin_symbol_from_db(self, symbol: str = None, sector: str = None) -> List[Tuple]:
        """
        Fetch stock metadata (ISIN, Symbol, Sector) optionally filtered by sector.

        Parameters:
            sector (str, optional): Filter stocks by sector (e.g., 'Bank', 'IT')

        Returns:
            List of tuples containing (ISIN, Symbol, Sector)
            :param sector:
            :param symbol:
        """
        try:
            # print("fetch_isin_symbol_from_db")
            # print("Sector == "+str(sector))
            # print("Symbol == "+str(symbol))
            self.connect()
            if symbol:
                # print("Symbol Handling")
                query = """
                SELECT isin, symbol, sector
                FROM stocks
                WHERE symbol = %s
                ORDER BY symbol
                """
                self.cursor.execute(query, (symbol,))
            else:
                # print("Sector or All Handling")

                if sector:
                    # print("Sector Handling")
                    query = """
                    SELECT isin, symbol, sector
                    FROM stocks
                    WHERE sector = %s
                    ORDER BY symbol
                    """
                    self.cursor.execute(query, (sector,))
                else:
                    # print("All Handling")
                    query = """
                    SELECT isin, symbol, sector
                    FROM stocks
                    ORDER BY symbol
                    """
                    self.cursor.execute(query)
            # print("Returning from here")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            # print("Finally")
            self.close()

    def fetch_all_sectors(self):
        try:
            self.connect()

            query = """
            SELECT distinct(sector)
            FROM stocks
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []
        finally:
            self.close()

    def insert_or_update_dataframe(self, df: pd.DataFrame):
        try:
            self.connect()

            insert_query = """
            INSERT INTO report_territory (
                symbol, sector, timeframe, open, high, low, close,
                guy_who_started, territory_value, territory, available_territory
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                sector = VALUES(sector),
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                guy_who_started = VALUES(guy_who_started),
                territory_value = VALUES(territory_value),
                territory = VALUES(territory),
                available_territory = VALUES(available_territory)
            """

            data_to_insert = [
                (
                    row['symbol'], row['sector'], row['timeframe'],
                    row['open'], row['high'], row['low'], row['close'],
                    row['guy_who_started'].to_pydatetime() if hasattr(row['guy_who_started'], 'to_pydatetime') else row['guy_who_started'],
                    row['territory_value'], row['territory'], row['available_territory']
                )
                for _, row in df.iterrows()
            ]

            self.cursor.executemany(insert_query, data_to_insert)
            self.conn.commit()
            print(f"{self.cursor.rowcount} rows inserted or updated.")

        except mysql.connector.Error as err:
            print("MySQL Error:", err)

        except Exception as e:
            print("Unexpected error:", e)

        finally:
            self.cursor.close()
