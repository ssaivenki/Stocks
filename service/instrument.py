from database.db_cache import get_db
from utility.config import Configuration
from utility.utils import Utility
import pandas as pd


class Instrument:
    def get_all_instruments(self):
        '''
        Get all the instruments available in the DB
        '''
        db = get_db()
        instruments = db.fetch_isin_symbol_from_db()
        return instruments

    def get_sector_instruments(self, sector: str):
        '''
        Get all the instruments available in the DB
        '''

        db = get_db()
        instruments = db.fetch_isin_symbol_from_db(None, sector)
        return instruments

    def get_symbol_instruments(self, symbol: str):
        '''
        Get all the instruments available in the DB
        '''
        db = get_db()
        instruments = db.fetch_isin_symbol_from_db(symbol)
        return instruments

    def load_stocks_isin_symbol(self):
        instruments = Utility.readFromFile(Configuration.dataFolder + Configuration.symbolsFileName)
        db = get_db()
        db.load_stocks_isin_symbol(instruments)

    def fetch_all_sectors(self):
        db = get_db()
        list = db.fetch_all_sectors()
        df = pd.DataFrame(list, columns=['Sector'])
        return df