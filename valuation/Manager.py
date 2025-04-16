from decimal import getcontext, Decimal
import pandas as pd
import numpy as np 
from datetime import datetime

class Valuation:

    def __init__(self, current_date):
        self.current_date = str(current_date)

    def valuation_path(self,module):
        folder_path = fullpath("data", "valuation", module)
        checkpath(folder_path)
        return fullpath(folder_path,self.current_date+".csv")
    
    def calculate_num_shares_on_rebalance_day(self):
        weights_path = fullpath("data","strategy","caps",self.current_date+".csv")
        price_path = fullpath("data", "market", "prices",self.current_date+".csv")
        ptf_size = 1e9

        weights = pd.read_csv(weights_path)
        prices = pd.read_csv(price_path)
        
        prices['Date'] = pd.to_datetime(prices['Date'])
        prices['Date'] = prices['Date'].dt.date

        price_qtr_end = prices[prices.Date == last_working_day("20231231")].drop("Date", axis=1).transpose()
        price_qtr_end = price_qtr_end.reset_index()
        price_qtr_end.columns = ["Symbol", "Prices"]        

        df_prices_weights = pd.merge(price_qtr_end, weights, left_on="Symbol", right_on="Symbol")
        df_prices_weights["DollarWeight"] = df_prices_weights["Weights"].apply(lambda x: ptf_size*x )
        df_prices_weights["NumShares"] = df_prices_weights["DollarWeight"].values / df_prices_weights["Prices"].values    

        df_prices_weights["NumShares"] = np.floor( df_prices_weights["DollarWeight"] / df_prices_weights["Prices"] )
        cash = (ptf_size - sum(df_prices_weights["NumShares"]*df_prices_weights["Prices"]))

        df_cash = pd.DataFrame({"Symbol": "cash", "Prices": 1, "Weights": cash/ptf_size, "DollarWeight": cash, "NumShares": cash }, index=range(1))
        df_asset_table = pd.concat([df_prices_weights, df_cash])

        return df_asset_table  
    

if __name__ == "__main__":
    from utilities.utils import fullpath, checkpath, last_working_day
    value = Valuation(20231231)
    df = value.calculate_num_shares_on_rebalance_day()
    print(df)