# import universe 
# requires access to data folder and a date for accessing universe file
import os
import pandas as pd
import requests
from utilities.utils import fullpath, checkpath

class Universe:

    def __init__(self, current_date):
        self.current_date = str(current_date)
        self.start_date = "2020-12-31"
        self.end_date = f"{self.current_date[:4]}-{self.current_date[4:6]}-{self.current_date[6:]}"
        self.interval = "1d"

    def universe_path(self,module):
        folder_path = fullpath("data", "universe", module)
        checkpath(folder_path)
        return fullpath(folder_path,self.current_date+".csv")
    
    def get_raw_universe(self):
        universe_path = fullpath("data","universe","raw",self.current_date+".csv")
        self.universe = pd.read_csv(universe_path, skiprows=[0,1])

        isin_codes = list( self.universe.iloc[:, 0] )

        def get_symbol_for_isin(isin):
            url = 'https://query1.finance.yahoo.com/v1/finance/search'
            headers = { 'User-Agent': 'lj'}
            params = dict(q=isin)
            resp = requests.get(url=url, headers=headers, params=params)
            data = resp.json()
            if 'quotes' in data and len(data['quotes']) > 0:
                return data['quotes'][0]['symbol']
            else:
                return None

        symbol_list = list()
        for i in isin_codes:
            isin = i
            symbol = get_symbol_for_isin(isin)
            symbol_list.append(symbol)

        self.universe['symbol'] = symbol_list

        return self.universe    