from utility.config import Configuration
from database.stock_database import StockDatabase

_cached_db = None

def get_db():
    global _cached_db
    if _cached_db is None:

        _cached_db = StockDatabase(
            host=Configuration.host,
            user=Configuration.user,
            password=Configuration.password,
            database=Configuration.database
        )
    return _cached_db