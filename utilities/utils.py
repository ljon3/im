import os
import pandas as pd
import re

def fullpath(*args):
    # returns os independent file path choosing the right file separator
    return os.path.join( *args )

def checkpath(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)           

def last_working_day(input_date):
    # For a given date in YYYYMMDD format, 
    # finds the last working day of the month
    
    if isinstance(input_date, str):
        input_date = "".join(re.findall(r"\d+", input_date))
        try:
            date = pd.to_datetime(input_date,format="%Y%m%d")
        except ValueError:
            print("Date format should be YYYYMMDD")

    last_day_of_month = date + pd.offsets.MonthEnd(0)

    if last_day_of_month.weekday() in [5, 6]:  # 5 = Saturday, 6 = Sunday
        last_working_day = last_day_of_month - pd.offsets.Week(weekday=4)  # 4 = Friday
    else:
        last_working_day = last_day_of_month

    return last_working_day.date()