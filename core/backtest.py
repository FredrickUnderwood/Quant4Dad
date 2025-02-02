from config.common_config import common_config
from dataclass import strategy
from dataclass import setting
from utils.functions import *
from utils.trade_log import TradeLogger
from data.collect_data import CollectData
import pandas as pd
import datetime
import os

def do_run_backtest(strategy: strategy.Strategy, setting: setting.Setting) -> dict:
    logger = TradeLogger()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stocks = strategy.stocks.split(',')
    stock_count = len(stocks)
    startdate = int(strategy.startdate)
    enddate = int(strategy.enddate)
    stock_data_list = []
    end_date_price_list = []
    for stock in stocks:
        data_path = base_dir + common_config.storage_base_path + stock + common_config.csv_extension
        df = pd.read_csv(data_path)
        start_index = df[df['trade_date'] >= startdate].index[0]
        # 回退50个tick，用于构造均线等数据
        start_index = max(start_index - 50, 0)
        end_index = df[df['trade_date'] <= enddate].index[-1]
        end_date_price_list.append(df.iloc[end_index]['close'].item())
        sliced_df = df.iloc[start_index:end_index + 1].reset_index(drop=True)
        sliced_df = sliced_df[['trade_date', 'open', 'high', 'low', 'close', 'vol']]
        stock_data_list.append(sliced_df)

    buy_factors_1 = strategy.buy_factors_1.split(',')
    buy_factors_2 = strategy.buy_factors_2.split(',')
    buy_relations = strategy.buy_relations.split(',')
    buy_amounts = strategy.buy_amounts.split(',')

    sell_factors_1 = strategy.sell_factors_1.split(',')
    sell_factors_2 = strategy.sell_factors_2.split(',')
    sell_relations = strategy.sell_relations.split(',')
    sell_amounts = strategy.sell_amounts.split(',')

    cash = float(setting.init_cash)
    df_position = pd.DataFrame({
        'stock': stocks,
        'cost': [0 for _ in range(stock_count)],
        'volume': [0 for _ in range(stock_count)]
    })

    cd = CollectData()
    trade_date_list = reversed(cd.get_trade_date(startdate, enddate))
    for index, trade_date in enumerate(trade_date_list):
        trade_date = int(trade_date)
        for stock, stock_data in zip(stocks, stock_data_list):
            for factor_1, factor_2, relation, amount in zip(sell_factors_1, sell_factors_2, sell_relations, sell_amounts):
                if get_decision(stock_data, trade_date, factor_1, factor_2, relation):
                    true_amount = get_true_sell_amount(df_position, stock, amount)
                    # 执行 sell
                    if true_amount > 0:
                        deal_price = float(stock_data[stock_data['trade_date'] == trade_date]['close'])
                        cash += true_amount * deal_price
                        df_position = refresh_df_position(df_position, stock, 'sell', true_amount, deal_price)
                        logger.log_trade(df_position, stock, '卖出', cash, deal_price, true_amount, trade_date)
            for factor_1, factor_2, relation, amount in zip(buy_factors_1, buy_factors_2, buy_relations, buy_amounts):
                if get_decision(stock_data, trade_date, factor_1, factor_2, relation):
                    current_index = stock_data[stock_data['trade_date'] >= trade_date].index[0]
                    try:
                        deal_price = float(stock_data.iloc[current_index + 1]['open'])
                    except IndexError:
                        break
                    true_amount = get_true_buy_amount(cash, amount, deal_price)
                    # 执行 buy
                    if true_amount > 0:
                        cash -= true_amount * deal_price
                        df_position = refresh_df_position(df_position, stock, 'buy', true_amount, deal_price)
                        logger.log_trade(df_position, stock, '买入', cash, deal_price, true_amount, trade_date)
    logger.log_result(df_position, float(setting.init_cash), cash, end_date_price_list, stocks)
    return logger.get_all_logs()
