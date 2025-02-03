import pandas as pd
import numpy as np

def calculate_moving_average(data, current_date, period):

    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame")

    if 'trade_date' not in data.columns or 'close' not in data.columns:
        raise ValueError("Data must contain 'trade_date' and 'close' columns")

    if period < 1:
        raise ValueError("Period must be a positive integer")

    try:
        current_index = data[data['trade_date'] >= current_date].index[0]
    except IndexError:
        raise ValueError(f"Date {current_date} not found in the data")

    start_index = max(0, current_index - period + 1)

    moving_average = data['close'].iloc[start_index: current_index + 1].mean()

    return moving_average


def calculate_pct_change(data, current_date, period):

    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame")

    if 'trade_date' not in data.columns or 'close' not in data.columns:
        raise ValueError("Data must contain 'trade_date' and 'close' columns")

    if period < 1:
        raise ValueError("Period must be a positive integer")

    try:
        current_index = data[data['trade_date'] >= current_date].index[0]
    except IndexError:
        raise ValueError(f"Date {current_date} not found in the data")

    start_index = max(0, current_index - period + 1)

    close_prices = data['close'].iloc[start_index: current_index + 1]

    if len(close_prices) < 2:
        return 0
    start_price = close_prices.iloc[0]
    end_price = close_prices.iloc[-1]
    pct_change = ((end_price - start_price) / start_price) * 100

    return pct_change
