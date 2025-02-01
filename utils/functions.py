from utils.indicators import *


def get_factor_value(data, current_date, factor):
    if 'ma' in factor:
        window = int(factor[3:])  # 提取窗口大小，如 'ma_5' -> 5
        return calculate_moving_average(data, current_date, window)
    elif 'pc' in factor:
        window = int(factor[3:])  # 提取窗口大小，如 'pc_10' -> 10
        return calculate_pct_change(data, current_date, window)
    else:
        try:
            return float(data.loc[data['trade_date'] == current_date, 'close'].iloc[0])
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
        new_cost = (origin_cost * origin_volume - deal_price * amount) / (origin_volume - amount)
        new_volume = origin_volume - amount
    else:
        new_cost = (origin_cost * origin_volume + deal_price * amount) / (origin_volume + amount)
        new_volume = origin_volume + amount
    df_position_updated = df_position.copy()
    df_position_updated.loc[df_position_updated['stock'] == stock, ['cost', 'volume']] = [
        new_cost, new_volume
    ]
    return df_position_updated


def get_true_amount(df_position, stock, amount):
    current_volume = df_position[df_position['stock'] == stock]['volume']
    if not '%' in amount:
        if amount <= current_volume:
            return int(amount)
        else:
            # 清仓
            return current_volume

    else:
        rate = float(amount[:-2]) / 100
        sell_amount = int(current_volume * rate // 100) * 100
        if sell_amount != 0:
            return sell_amount
        else:
            # 清仓
            return current_volume
