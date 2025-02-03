import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from dataclass.strategy import Strategy, insert, get_user_strategies, get_user_strategies_with_pagination
from dataclass.setting import Setting
from dataclass.user import User, verify_user, create_user, get_user_by_id
from core.backtest import do_run_backtest
from data.collect_data import CollectData
import json
from datetime import timedelta

# 获取当前文件所在目录的父目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 设置模板目录为项目根目录下的 templates
app = Flask(__name__, 
    template_folder=os.path.join(base_dir, 'templates'))
app.secret_key = 'your-secret-key'  # 请更改为随机的密钥

# 修改 Session 配置
app.config.update(
    SESSION_COOKIE_SAMESITE=None,    # 允许跨站点 Cookie
    SESSION_COOKIE_SECURE=False,      # 允许 HTTP
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_COOKIE_DOMAIN=None,       # 允许所有域名
    SESSION_COOKIE_PATH='/'           # 设置 Cookie 路径
)

# CORS 配置
CORS(app, 
     supports_credentials=True,
     origins=['*'],                   # 允许所有来源
     allow_headers=['*'],             # 允许所有头部
     expose_headers=['*'],            # 暴露所有头部
     methods=['GET', 'POST', 'OPTIONS'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = verify_user(data['username'], data['password'])
    if user:
        login_user(user)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "用户名或密码错误"})

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create_strategy')
@login_required
def create_strategy_page():
    return render_template('create_strategy.html')

@app.route('/api/strategy/create', methods=['POST'])
@login_required
def create_strategy():
    try:
        data = request.json
        strategy = Strategy(
            startdate=data['startdate'],
            enddate=data['enddate'],
            stocks=data['stocks'],
            buy_factors_1=data['buy_factors_1'],
            buy_factors_2=data['buy_factors_2'],
            buy_relations=data['buy_relations'],
            sell_factors_1=data['sell_factors_1'],
            sell_factors_2=data['sell_factors_2'],
            sell_relations=data['sell_relations'],
            buy_amounts=data['buy_amounts'],
            sell_amounts=data['sell_amounts'],
            user_id=current_user.id
        )
        insert(strategy)
        return jsonify({"message": "策略创建成功", "success": True})
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 500

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    try:
        data = request.json
        strategy_id = data['strategy_id']
        strategy = get_user_strategies(current_user.id, strategy_id)
        init_cash = data['init_cash']
        setting = Setting(init_cash)
        result = do_run_backtest(strategy, setting)
        return jsonify({
            "message": "回测执行成功",
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"message": str(e), "success": False}), 500

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    try:
        data = CollectData().collect_all_stocks()
        return jsonify({
            "success": True,
            "data": data.to_dict('records')  # 将DataFrame转换为字典列表
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/backtest')
def backtest_page():
    return render_template('backtest.html')

@app.route('/api/strategies/<int:page>', methods=['GET'])
@login_required
def get_strategies(page):
    try:
        page_size = 12
        strategies, total = get_user_strategies_with_pagination(current_user.id, page, page_size)
        return jsonify({
            "success": True,
            "data": {
                "strategies": strategies,
                "total": total,
                "current_page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/sync_data', methods=['POST'])
def sync_data():
    try:
        cd = CollectData()
        cd.collect_daily_data()
        return jsonify({
            "success": True,
            "message": "数据同步成功"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')