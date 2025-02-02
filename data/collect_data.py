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
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def collect_daily_data(self):
        api = 'daily'
        stocks = self.collect_all_stocks()
        end_date = datetime.datetime.today().strftime(tushare_config.date_format)  # 当前日期
        for index, row in stocks.iterrows():
            ts_code = row['ts_code']
            data_path = self.base_dir + common_config.storage_base_path + ts_code[:6] + common_config.csv_extension
            if not os.path.exists(data_path):
                # 如果文件不存在，从起始日期下载到今天
                data = self.pro.query(api, ts_code=ts_code, start_date=tushare_config.start_date, end_date=end_date)
                data = data.sort_values(by='trade_date', ascending=True)  # 按时间升序排序
                data.to_csv(data_path, index=False)
            else:
                # 如果文件存在，先读取现有数据
                origin_data = pd.read_csv(data_path)
                # 获取最后一个交易日的日期
                last_trade_date_str = str(origin_data['trade_date'].max())
                # 将最后一个日期字符串转换为日期对象
                last_trade_date = datetime.datetime.strptime(last_trade_date_str, tushare_config.date_format).date()
                # 确定新的起始日期（最后一个日期的下一天）
                start_date = last_trade_date + datetime.timedelta(days=1)
                # 如果新的起始日期大于当前日期，则不需要更新
                if start_date > datetime.datetime.now().date():
                    print(f"No new data for {ts_code}")
                    continue
                start_date_str = start_date.strftime(tushare_config.date_format)
                print(f"Collecting data for {ts_code} from {start_date_str} to {end_date}")
                # 获取新数据
                new_data = self.pro.query(api, ts_code=ts_code, start_date=start_date_str, end_date=end_date)
                if not new_data.empty:
                    # 合并新旧数据
                    new_data = pd.concat([origin_data, new_data], axis=0)
                    # 按时间升序排序
                    new_data = new_data.sort_values(by='trade_date', ascending=True)
                    # 去除重复的交易日记录
                    new_data.drop_duplicates(subset=['trade_date'], keep='last', inplace=True)
                    # 保存更新后的数据
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
