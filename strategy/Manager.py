from abc import ABC, abstractmethod #, property
from utilities.utils import fullpath, checkpath
from utilities.utils import last_day, last_working_day, validate_date
from utilities.utils import get_datestr, get_datetime
import pandas as pd
import numpy as np
from decimal import getcontext, Decimal
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf


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
    
    def prepare_strategy(self):

        # get market data
        path_data_market = fullpath( self.path_market(self.module), 
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
        else: 
            prior_weights = None # pd.DataFrame(np.zeros(shape=data_market.shape[0]), columns=data_market.columns)

        return data_market, prior_weights    
    
class CapWeight(BaseStrategy):

    """ Implements cap weighted indices """

    def __init__(self, current_date):
        self.inception_date = validate_date("2020-12-31")
        self.current_date = validate_date(current_date)
        self.last_day = last_day(self.current_date)
        self.last_working_day = last_working_day(self.current_date)
        self.module = "caps"

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

        return prior_weights, df_weights

class MaxSharpeRatioPortfolio(BaseStrategy):

    """ Implements cap weighted indices """

    def __init__(self, current_date):
        self.inception_date = validate_date("2020-12-31")
        self.current_date = validate_date(current_date)
        self.last_day = last_day(self.current_date)
        self.last_working_day = last_working_day(self.current_date)
        self.module = "prices"
        self.risk_free_rate = 0.035


    def calculate_weights(self):

        # get current market data and prior weights
        [data_market, prior_weights] = self.prepare_strategy()

        # Cast Date to datetime format
        data_market["Date"] = pd.to_datetime(data_market["Date"])

        # build a DF that has all dates to ffill and get end of month values
        start_date,end_date = data_market.iloc[[0,-1]]['Date'].values

        all_dates = pd.date_range(start=start_date, end=end_date)
        df_data_market_all_dates = pd.DataFrame(all_dates, columns=["Dates"])

        df_data_market_all = pd.merge(data_market, df_data_market_all_dates, left_on="Date", right_on="Dates", how="right")
        df_data_market_all.drop("Date", axis=1, inplace=True)

        # fwd fill data to avoid na
        df_data_market_all.ffill(axis=0,inplace=True)

        # get month ends
        idx = df_data_market_all.Dates.dt.is_month_end
        df_data_market_all = df_data_market_all.loc[idx]
        df_data_market_all.drop("Dates", axis=1, inplace=True)

        # get returns from prices
        df_returns = df_data_market_all.pct_change()
        expected_returns = df_returns.mean()


        # covariance calculations
        self.df_sample_cov_matrix = df_returns.cov()
        cov = LedoitWolf().fit(df_returns.dropna())
        self.df_LedoitWolf_cov_matrix = pd.DataFrame(cov.covariance_, index=df_returns.columns, columns=df_returns.columns)

        # max sharpe ratio optim - objective function
        def max_sharpe_ratio(weights, cov_matrix):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.dot(weights.transpose(), np.dot(cov_matrix, weights)) ** 1/2
            msr = (portfolio_return - self.risk_free_rate/12) / portfolio_volatility
            return -msr 

        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        bounds = tuple((0, 1) for _ in range(len(expected_returns)))
        initial_weights = np.array([1 / len(expected_returns)] * len(expected_returns))
        result_sample = minimize(max_sharpe_ratio, initial_weights, args=(self.df_sample_cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)
        result_lw = minimize(max_sharpe_ratio, initial_weights, args=(self.df_LedoitWolf_cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)

        df_weights = pd.DataFrame({
            'Asset': df_data_market_all.columns,
            'Weight_Sample': result_sample.x,
            'Weight_LW': result_lw.x,
        })

        df_weights["Weight_Sample"] = df_weights["Weight_Sample"].apply(lambda x: 0 if x < 1e-6 else x)
        df_weights["Weight_LW"] = df_weights["Weight_LW"].apply(lambda x: 0 if x < 1e-6 else x)

        df_to_write = df_weights.loc[:,["Asset","Weight_LW"]]
        df_to_write.columns = ["Symbol","Weights"]
        df_to_write.to_csv(fullpath( self.path_strategy("msr"), 
                                                  get_datestr(self.current_date)+".csv" ), index=False)

        return prior_weights, df_weights
    
        # # Using Decimal to work calculate with precision
        # data_market["MarketCap"].apply(Decimal)
        # total_market_cap = sum(data_market["MarketCap"])
        
        # # calculating weights
        # data_market["Weights"] = data_market["MarketCap"].apply(lambda x: x/total_market_cap)
        

        # path_new_weights = fullpath(self.path_strategy(self.module), 
        #                             get_datestr(self.last_day)+".csv")
        # new_weights = data_market.loc[:,["Symbol","Weights"]]
        # new_weights.to_csv(path_new_weights, index=False)

        # df_weights = pd.merge(prior_weights, new_weights, on="Symbol", suffixes=('_old', '_new'))

        # return prior_weights, new_weights, df_weights