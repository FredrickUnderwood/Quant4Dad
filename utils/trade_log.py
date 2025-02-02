import pandas as pd


def print_log(df_position: pd.DataFrame, stock: str, transaction_type: str, cash: float, deal_price: float, amount: int,
              trade_date: int):
    current_volume, current_cost = int(df_position[df_position['stock'] == stock]['volume']), \
        round(float(df_position[df_position['stock'] == stock]['cost']), 3)
    print(
        f"交易完成: 股票: {stock}, 日期: {trade_date}, 交易类型: {transaction_type}, 成交价格: {deal_price}, 成交量: {amount}, 当前成本: {current_cost}, 持仓量: {current_volume}, 余额: {cash}")

def print_result(start_date: int, end_date: int, df_position: pd.DataFrame, init_cash: float, current_cash: float, end_date_price_list: list[float], stock_list: list[str]):
    stock_value = 0
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>最终持仓>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for stock, stock_current_price in zip(stock_list, end_date_price_list):
        current_volume, current_cost = int(df_position[df_position['stock'] == stock]['volume']), \
            float(df_position[df_position['stock'] == stock]['cost'])
        current_value = stock_current_price * current_volume
        stock_value += current_value
        print(f"股票: {stock}, 成本: {round(current_cost, 3)}, 持仓量: {current_volume}, 市值: {round(current_value, 3)}")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>回测结果>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    earning_rate = round(((stock_value + current_cash) / init_cash - 1) * 100, 3)
    print(f"起始日期: {start_date}, 结束日期: {end_date}, 总市值: {stock_value + current_cash}, 可用资金: {current_cash}, 收益率: {earning_rate}%")