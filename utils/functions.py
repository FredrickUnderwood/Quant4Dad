import pandas as pd

from utils.indicators import *


def get_factor_value(data, current_date, factor):
    if 'ma' in factor:
        window = int(factor[3:])  # 提取窗口大小，如 'ma_5' -> 5
        return calculate_moving_average(data, current_date, window)
    elif 'pc' in factor:
        window = int(factor[3:])  # 提取窗口大小，如 'pc_10' -> 10
        return calculate_pct_change(data, current_date, window)
    else:
        window = int(factor[3:])
        current_date_index = data[data['trade_date'] >= current_date].index[0]
        target_index = max(current_date_index - window, 0)
        try:
            return float(data.iloc[target_index]['close'])
        except IndexError:
            return None


def get_decision(data, current_date, factor_1, factor_2, relation):
    value_1 = get_factor_value(data, current_date, factor_1)
    value_2 = get_factor_value(data, current_date, factor_2)

    if value_1 is None or value_2 is None:
        return False

    if relation == 'gt':
        return value_1 > value_2
    elif relation == 'lt':
        return value_1 < value_2
    else:
        raise ValueError(f"不支持的关系类型: {relation}")


def refresh_df_position(df_position, stock, transaction_type, amount, deal_price):
    origin_cost = df_position[df_position['stock'] == stock]['cost']
    origin_volume = df_position[df_position['stock'] == stock]['volume']
    if transaction_type == 'sell':
        if int(origin_volume) - int(amount) != 0:
            new_cost = (origin_cost * origin_volume - deal_price * amount) / (origin_volume - amount)
        else:
            new_cost = 0
        new_volume = origin_volume - amount
    else:
        new_cost = (origin_cost * origin_volume + deal_price * amount) / (origin_volume + amount)
        new_volume = origin_volume + amount
    df_position_updated = df_position.copy()
    df_position_updated.loc[df_position_updated['stock'] == stock, 'cost'] = new_cost
    df_position_updated.loc[df_position_updated['stock'] == stock, 'volume'] = new_volume
    return df_position_updated


def get_true_sell_amount(df_position, stock, amount):
    current_volume = df_position[df_position['stock'] == stock]['volume']
    if not '%' in amount:
        if int(amount) <= int(current_volume):
            return int(amount)
        else:
            # 清仓
            return int(current_volume)

    else:
        rate = float(amount[:-2]) / 100
        sell_amount = int(current_volume * rate // 100) * 100
        if sell_amount != 0:
            return sell_amount
        else:
            # 清仓
            return current_volume


def get_true_buy_amount(cash, amount, close):
    if not '%' in amount:
        if int(amount) * close <= cash:
            return int(amount)
        else:
            # all in
            return int((cash / close) // 100) * 100
    else:
        rate = float(amount[:-2]) / 100
        buy_amount = int((cash * rate / close) // 100) * 100
        return buy_amount
