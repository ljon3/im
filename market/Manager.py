import os
import pandas as pd
import yfinance as yf
from utilities.utils import fullpath, checkpath

class Market:
    # Market class manages the daily market data
    # Brings in data from Yahoo Finance
    # stores it under the path data/market/{date}

    def __init__(self, current_date):
        self.current_date = str(current_date)
        self.start_date = "2020-12-31"
        self.end_date = f"{self.current_date[:4]}-{self.current_date[4:6]}-{self.current_date[6:]}"
        self.interval = "1d"

    def market_path(self,module):
        folder_path = fullpath("data", "market", module)
        checkpath(folder_path)
        return fullpath(folder_path,self.current_date+".csv")

    def get_universe(self):
        universe_path = fullpath("data","universe","processed",self.current_date+".csv")
        self.universe = pd.read_csv(universe_path)
        return self.universe
    
    def get_prices(self):
        
        # get recent universe
        self.get_universe()
        
        symbols = list(self.universe.loc[:, "symbol"])
        market_data = yf.download(symbols, start=self.start_date, end=self.end_date, interval=self.interval, group_by="column") 
        market_data = market_data.xs("Close", level=0, axis=1)
        market_data.to_csv(self.market_path(module="prices"))
        return market_data
    
    def get_caps(self):

        # get recent universe
        self.get_universe()

        symbols = list(self.universe.loc[:, "symbol"])

        market_caps = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                market_cap = stock.info.get("marketCap")  # Get market capitalization
                market_caps[symbol] = market_cap if market_cap else "N/A"
            except Exception as e:
                market_caps[symbol] = f"Error: {e}"

        df_market_caps = pd.DataFrame(list(market_caps.items()), columns=["Symbol", "MarketCap"])
        df_market_caps.to_csv(self.market_path(module="caps"), index=False)
        return df_market_caps

