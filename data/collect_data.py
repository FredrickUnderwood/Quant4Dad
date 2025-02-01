import tushare as ts
import pandas as pd
import datetime
import os
from config.tushare_config import tushare_config
from config.common_config import common_config


class CollectData:


    def __init__(self):
        ts.set_token(tushare_config.token)
        self.pro = ts.pro_api()
        

    def collect_daily_data(self):
        api = 'daily'
        stocks = self.collect_all_stocks()
        start_date = '20100101'
        end_date = datetime.date.today().strftime(tushare_config.date_format)
        for index, row in stocks.iterrows():
            ts_code = row['ts_code']
            data_path = common_config.storage_base_path + ts_code[:6] + common_config.csv_extension
            if not os.path.exists(data_path):
                data = self.pro.query(api, ts_code = ts_code, start_date = start_date, end_date = end_date)
                data.to_csv(data_path, index=False)
            else:
                start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime(tushare_config.date_format)
                data = self.pro.query(api, ts_code = ts_code, start_date = start_date, end_date = end_date)
                origin_data = pd.read_csv(data_path)
                new_data = pd.concat([origin_data, data], axis=1)
                new_data.to_csv(data_path, index=False)



    def collect_minute_data(self):
        pass

    def collect_all_stocks(self):
        api = 'stock_basic'
        data = self.pro.query(api, fields='ts_code,name')
        return data

    def collect_all_funds(self):
        api = 'fund_basic'
        data = self.pro.query(api, market='E')
        return data

    def get_trade_date(self, start_date, end_date):
        api = 'trade_cal'
        data = self.pro.query(api, start_date=start_date, end_date=end_date)
        return data[data['is_open'] == 1]['cal_date'].tolist()