import pandas as pd
import mplfinance as mpf


def generate_k_plot(stock_data: pd.DataFrame):
    stock_data.index = stock_data.trade_date
    stock_data = stock_data.rename(index=pd.Timestamp)
    stock_data.drop(columns=['trade_date'], inplace=True)
    stock_data.columns = ['open', 'high', 'low', 'close', 'volume']

    custom_colors = mpf.make_marketcolors(
        up='red',  # 上涨的颜色
        down='cyan',  # 下跌的颜色
        wick='inherit',
        edge='inherit',
        volume="inherit"  # 成交量条颜色
    )
    style = mpf.make_mpf_style(base_mpl_style="seaborn", marketcolors=custom_colors)
    mpf.plot(stock_data, type='candle', volume=True, style=style, mav=(5, 10, 20, 30), figsize=[50, 30])