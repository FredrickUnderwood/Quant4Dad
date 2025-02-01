from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import declarative_base
from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.common_config import common_config

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

    def __repr__(self):
        return f"<Strategy(id={self.id}, startdate='{self.startdate}', enddate='{self.enddate}')>"


def init_session():
    engine = create_engine(common_config.database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def insert(strategy: Strategy):
    session = init_session();
    session.add(strategy)
    session.commit()


def get_by_id(id):
    session = init_session()
    return session.query(Strategy).filter_by(id=id).first()
