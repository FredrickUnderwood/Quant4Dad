import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.widgets import MultiCursor

# 设置中文字体
try:
    # 尝试使用微软雅黑
    font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
except:
    try:
        # 尝试使用宋体
        font = FontProperties(fname=r"C:\Windows\Fonts\simsun.ttc")
    except:
        print("警告: 无法加载中文字体，图表中的中文可能显示为方块")
        font = None

def plot_trading_signals(df, trades, stock_code, save_path=None):
    """
    生成带有交易信号的K线图
    
    参数:
    df: DataFrame, 包含OHLCV数据
    trades: DataFrame, 包含交易记录，至少包含['trade_date', 'type', 'price']列
    stock_code: str, 股票代码
    save_path: str, 可选，图片保存路径
    """
    plt.rcParams['font.family'] = ['Microsoft YaHei', 'SimSun', 'sans-serif']
    if font is not None:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 确保日期格式正确
    df = df.copy()
    df['trade_date'] = pd.to_datetime(df['trade_date'].astype(str))
    df.set_index('trade_date', inplace=True)
    
    # 准备K线图数据
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'vol': 'Volume'  # 修改这里以匹配实际的列名
    })
    
    # 确保所有必需的列都存在
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f'缺少必需的列 {col}。当前列: {df.columns.tolist()}')
    
    # 准备交易标记
    buy_signals = trades[trades['type'] == '买入'].copy()
    sell_signals = trades[trades['type'] == '卖出'].copy()
    
    # 转换交易日期格式
    buy_signals.loc[:, 'trade_date'] = pd.to_datetime(buy_signals['trade_date'].astype(str))
    sell_signals.loc[:, 'trade_date'] = pd.to_datetime(sell_signals['trade_date'].astype(str))
    
    # 创建买入卖出标记
    apds = []
    
    # 创建与df索引等长的空Series
    signal_template = pd.Series(np.nan, index=df.index)
    
    # 添加买入标记
    if not buy_signals.empty:
        buy_series = signal_template.copy()
        buy_dates = buy_signals.set_index('trade_date')
        valid_dates = buy_dates.index.intersection(df.index)
        buy_series[valid_dates] = buy_dates.loc[valid_dates, 'price']
        apds.append(mpf.make_addplot(buy_series, type='scatter',
                                   marker='^', markersize=50,
                                   color='red'))
    
    # 添加卖出标记
    if not sell_signals.empty:
        sell_series = signal_template.copy()
        sell_dates = sell_signals.set_index('trade_date')
        valid_dates = sell_dates.index.intersection(df.index)
        sell_series[valid_dates] = sell_dates.loc[valid_dates, 'price']
        apds.append(mpf.make_addplot(sell_series, type='scatter',
                                   marker='v', markersize=50,
                                   color='green'))
    
    # 设置图表样式
        # 设置图表样式
        style = mpf.make_mpf_style(
            base_mpf_style='charles',
            gridstyle='',
            y_on_right=False,
            marketcolors=mpf.make_marketcolors(
                up='none',  # 上涨空心
                down='cyan',  # 下跌青色
                edge={
                    'up': 'red',  # 上涨边框红色
                    'down': 'cyan'  # 下跌边框青色
                },
                wick='inherit',
                volume={
                    'up': 'red',
                    'down': 'cyan'
                },
                candle={'width': 0.6}  # 调整蜡烛宽度
            ),
            edgecolor='black',
            facecolor='white',
            figcolor='white',
            rc={
                'axes.edgecolor': 'black',
                'axes.linewidth': 1.5,
                'axes.grid': True,
                'grid.linestyle': '--',
                'grid.alpha': 0.3
            }
        )

    try:
        # 创建交互式图表
        kwargs = dict(
            type='candle',
            style=style,
            volume=True,
            figsize=(30, 20),
            addplot=apds if apds else None,
            returnfig=True,
            title=f'\n{stock_code} Trading Signal Chart',
            panel_ratios=(3, 1),
            scale_padding=0.1,
            xrotation=45,  # 旋转 x 轴标签
            tight_layout=True  # 紧凑布局
        )

        # 绘制K线图
        fig, axes = mpf.plot(
            df,
            **kwargs
        )
        
        # 添加图例
        ax1 = axes[0]
        ax1.scatter([], [], marker='^', color='red', s=50, label='Buy')
        ax1.scatter([], [], marker='v', color='green', s=50, label='Sell')
        ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='black')
        
        # 添加十字光标
        multi = MultiCursor(fig.canvas, axes, color='black', lw=1, horizOn=True, vertOn=True)
        
        # 启用缩放和平移
        ax1.set_zorder(axes[1].get_zorder() + 1)  # 确保K线图在上层
        ax1.patch.set_visible(False)           # 使K线图背景透明
        
        # 为每个子图添加边框
        for ax in axes:
            ax.set_frame_on(True)
            for spine in ['top', 'bottom', 'left', 'right']:
                ax.spines[spine].set_visible(True)
                ax.spines[spine].set_linewidth(1.5)
                ax.spines[spine].set_color('black')
        
        # 调整子图之间的间距
        plt.subplots_adjust(hspace=0.1)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5, facecolor='white', edgecolor='black')
            plt.close()
        else:
            plt.show()
            
    except Exception as e:
        print(f"绘制图表时出错: {str(e)}")
        print(f"数据形状: {df.shape}")
        print(f"交易标记数量: {len(apds) if apds else 0}")

def generate_trading_charts(df_list, trade_records_list, stock_codes, output_dir='trading_charts'):
    """
    为多只股票生成交易K线图
    
    参数:
    df_list: list of DataFrames, 每个DataFrame包含一只股票的OHLCV数据
    trade_records_list: list of DataFrames, 每个DataFrame包含一只股票的交易记录
    stock_codes: list of str, 股票代码列表
    output_dir: str, 图片输出目录
    """
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for df, trades, stock_code in zip(df_list, trade_records_list, stock_codes):
        try:
            save_path = os.path.join(output_dir, f'{stock_code}_trading_chart.png')
            # 对于交互式图表，我们不保存，直接显示
            plot_trading_signals(df, trades, stock_code, None)
            print(f"正在显示{stock_code}的交易图表...")
        except Exception as e:
            print(f"生成{stock_code}的交易图表时出错: {str(e)}")
            print(f"数据列: {df.columns.tolist()}")
            print(f"数据形状: {df.shape}")
            if not trades.empty:
                print(f"交易记录形状: {trades.shape}")
                print(f"交易日期范围: {trades['trade_date'].min()} 到 {trades['trade_date'].max()}")