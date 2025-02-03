from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import declarative_base
from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysql.connector

from config.common_config import common_config
from config.db_config import db_config

# 创建 SQLAlchemy 的基类
Base = declarative_base()


# 定义 Strategy 表模型
@dataclass
class Strategy(Base):
    __tablename__ = 'strategy'

    id: int = Column(BigInteger, primary_key=True)  # 主键
    startdate: str = Column(String(50), nullable=False)  # 开始日期
    enddate: str = Column(String(50), nullable=False)  # 结束日期
    stocks: str = Column(String(255))  # 股票代码列表
    buy_factors_1: str = Column(String(1024))  # 买入因子1
    buy_factors_2: str = Column(String(1024))  # 买入因子2
    buy_relations: str = Column(String(255))  # 买入条件关系
    sell_factors_1: str = Column(String(1024))  # 卖出因子1
    sell_factors_2: str = Column(String(1024))  # 卖出因子2
    sell_relations: str = Column(String(255))  # 卖出条件关系
    buy_amounts: str = Column(String(255))  # 买入仓位
    sell_amounts: str = Column(String(255))  # 卖出仓位
    user_id: int = Column(BigInteger, nullable=False)  # 用户ID

    def __repr__(self):
        return f"<Strategy(id={self.id}, startdate='{self.startdate}', enddate='{self.enddate}')>"


def init_session():
    engine = create_engine(common_config.database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def insert(strategy: Strategy) -> int:
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO strategy (user_id, startdate, enddate, stocks, buy_factors_1, buy_factors_2, buy_relations, buy_amounts, sell_factors_1, sell_factors_2, sell_relations, sell_amounts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            strategy.user_id,
            strategy.startdate,
            strategy.enddate,
            strategy.stocks,
            strategy.buy_factors_1,
            strategy.buy_factors_2,
            strategy.buy_relations,
            strategy.buy_amounts,
            strategy.sell_factors_1,
            strategy.sell_factors_2,
            strategy.sell_relations,
            strategy.sell_amounts
        ))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_by_id(id):
    session = init_session()
    return session.query(Strategy).filter_by(id=id).first()


def get_user_strategies(user_id, strategy_id=None):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        if strategy_id is not None:
            # 获取特定用户的特定策略
            cursor.execute("SELECT * FROM strategy WHERE user_id = %s AND id = %s", (user_id, strategy_id))
            data = cursor.fetchone()
            if data:
                strategy = Strategy(
                    startdate=data['startdate'],
                    enddate=data['enddate'],
                    stocks=data['stocks'],
                    buy_factors_1=data['buy_factors_1'],
                    buy_factors_2=data['buy_factors_2'],
                    buy_relations=data['buy_relations'],
                    buy_amounts=data['buy_amounts'],
                    sell_factors_1=data['sell_factors_1'],
                    sell_factors_2=data['sell_factors_2'],
                    sell_relations=data['sell_relations'],
                    sell_amounts=data['sell_amounts'],
                    user_id=data['user_id']
                )
                strategy.id = data['id']
                return strategy
            return None
        else:
            # 获取用户的所有策略
            cursor.execute("SELECT * FROM strategy WHERE user_id = %s", (user_id,))
            data_list = cursor.fetchall()
            strategies = []
            for data in data_list:
                strategy = Strategy(
                    startdate=data['startdate'],
                    enddate=data['enddate'],
                    stocks=data['stocks'],
                    buy_factors_1=data['buy_factors_1'],
                    buy_factors_2=data['buy_factors_2'],
                    buy_relations=data['buy_relations'],
                    buy_amounts=data['buy_amounts'],
                    sell_factors_1=data['sell_factors_1'],
                    sell_factors_2=data['sell_factors_2'],
                    sell_relations=data['sell_relations'],
                    sell_amounts=data['sell_amounts'],
                    user_id=data['user_id']
                )
                strategy.id = data['id']
                strategies.append(strategy)
            return strategies
    finally:
        cursor.close()
        conn.close()


def get_user_strategies_with_pagination(user_id, page=1, page_size=12):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) as total FROM strategy WHERE user_id = %s", (user_id,))
        total = cursor.fetchone()['total']
        
        # 获取分页数据
        offset = (page - 1) * page_size
        cursor.execute("""
            SELECT * FROM strategy 
            WHERE user_id = %s 
            ORDER BY id DESC 
            LIMIT %s OFFSET %s
        """, (user_id, page_size, offset))
        data_list = cursor.fetchall()
        
        strategies = []
        for data in data_list:
            strategy = Strategy(
                startdate=data['startdate'],
                enddate=data['enddate'],
                stocks=data['stocks'],
                buy_factors_1=data['buy_factors_1'],
                buy_factors_2=data['buy_factors_2'],
                buy_relations=data['buy_relations'],
                buy_amounts=data['buy_amounts'],
                sell_factors_1=data['sell_factors_1'],
                sell_factors_2=data['sell_factors_2'],
                sell_relations=data['sell_relations'],
                sell_amounts=data['sell_amounts'],
                user_id=data['user_id']
            )
            strategy.id = data['id']
            strategies.append(strategy)
        return strategies, total
    finally:
        cursor.close()
        conn.close()