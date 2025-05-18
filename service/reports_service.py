
import pandas as pd

# from database.stock_database import StockDatabase
# from utility.utils import Utility
# from utility.config import Configuration
from database.db_cache import get_db

class Reports:

    def insert_or_update_dataframe(self, df: pd.DataFrame):
        db = get_db()
        db.insert_or_update_dataframe(df)


