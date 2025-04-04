from abc import ABC, abstractmethod #, property
from utilities.utils import fullpath, checkpath
import pandas as pd
from decimal import getcontext, Decimal

getcontext().prec = 16 

class BaseStrategy(ABC):
    """ Setting base strategy with expected signature """

    @abstractmethod
    def calculate_weights(self):
        pass

    def strategy_path(self,module):
        folder_path = fullpath("data", "strategy", module)
        checkpath(folder_path)
        return fullpath(folder_path,self.current_date+".csv")

    def market_path(self,module):
        folder_path = fullpath("data", "market", module)
        checkpath(folder_path)
        return fullpath(folder_path,self.current_date+".csv")
    
class CapWeight(BaseStrategy):
    """ Implements cap weighted indices """

    def __init__(self, current_date):
        self.current_date = str(current_date)
        self.inception_date = str(20231231)
        self.module = "caps"

    def prepare_strategy(self):

        strategy_type = dict()
        strategy_type["type"] = "characteristic"

        strategy_data = pd.read_csv(self.market_path("caps"))

        prior_weights = None
        if self.current_date != self.inception_date:
            prior_weights = self.strategy_path("caps")

        return strategy_type, strategy_data, prior_weights

    def calculate_weights(self):
        [strategy_type, strategy_data, prior_weights] = self.prepare_strategy()
        strategy_data["MarketCap"].apply(Decimal)
        total_market_cap = sum(strategy_data["MarketCap"])
        
        strategy_data["Weights"] = strategy_data["MarketCap"].apply(lambda x: x/total_market_cap)
        
        new_weights = strategy_data.loc[:,["Symbol","Weights"]]
        new_weights.to_csv(self.strategy_path(module=self.module), index=False)

        return new_weights