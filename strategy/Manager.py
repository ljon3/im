from abc import ABC, abstractmethod #, property
from utilities.utils import fullpath, checkpath
from utilities.utils import last_day, last_working_day, validate_date
from utilities.utils import get_datestr, get_datetime
import pandas as pd
from decimal import getcontext, Decimal

getcontext().prec = 16 

class BaseStrategy(ABC):
    """ Setting base strategy with expected signature """

    @abstractmethod
    def calculate_weights(self):
        pass

    def path_strategy(self,module):
        folder_path = fullpath("data", "strategy", module)
        checkpath(folder_path)
        return fullpath(folder_path)

    def path_market(self,module):
        folder_path = fullpath("data", "market", module)
        checkpath(folder_path)
        return fullpath(folder_path)
    
class CapWeight(BaseStrategy):
    """ Implements cap weighted indices """

    def __init__(self, current_date):
        self.inception_date = validate_date("2020-12-31")
        self.current_date = validate_date(current_date)
        self.last_day = last_day(self.current_date)
        self.last_working_day = last_working_day(self.current_date)
        self.module = "caps"
        self.strategy_type = dict()
        self.strategy_type["type"] = "characteristic"

    def prepare_strategy(self):

        # get market data
        path_data_market = fullpath( self.path_market("caps"), 
                                     get_datestr(self.current_date)+".csv" )
        data_market = pd.read_csv(path_data_market)

        # quarters data - to compare weights with previous quarters
        quarters = pd.read_csv(fullpath("data","quarters.txt"), names=["qtr"],  skiprows=1)
        quarters["qtr"] = quarters["qtr"].apply(lambda x: validate_date(x))

        # get prior_weights
        idx = validate_date(self.current_date) > quarters["qtr"]
        if any(idx):
            previous_quarter = max(quarters.loc[idx, "qtr"])
            prior_weights = pd.read_csv(fullpath( self.path_strategy("caps"), 
                                                  get_datestr(previous_quarter)+".csv" ))

        return data_market, prior_weights

    def calculate_weights(self):

        # get current market data and prior weights
        [data_market, prior_weights] = self.prepare_strategy()
        
        # Using Decimal to work calculate with precision
        data_market["MarketCap"].apply(Decimal)
        total_market_cap = sum(data_market["MarketCap"])
        
        # calculating weights
        data_market["Weights"] = data_market["MarketCap"].apply(lambda x: x/total_market_cap)
        

        path_new_weights = fullpath(self.path_strategy(self.module), 
                                    get_datestr(self.last_day)+".csv")
        new_weights = data_market.loc[:,["Symbol","Weights"]]
        new_weights.to_csv(path_new_weights, index=False)

        df_weights = pd.merge(prior_weights, new_weights, on="Symbol", suffixes=('_old', '_new'))

        return prior_weights, new_weights, df_weights