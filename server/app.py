from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dataclass.strategy import Strategy, insert, get_by_id, get_all_strategies
from dataclass.setting import Setting
from core.backtest import do_run_backtest
from data.collect_data import CollectData
import json
import os

# 获取当前文件所在目录的父目录
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 设置模板目录为项目根目录下的 templates
app = Flask(__name__, 
    template_folder=os.path.join(base_dir, 'templates'))
CORS(app)  # 启用跨域支持

@app.route('/create_strategy')
def create_strategy_page():
    return render_template('create_strategy.html')

@app.route('/api/strategy/create', methods=['POST'])
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
            sell_amounts=data['sell_amounts']
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
        strategy = get_by_id(strategy_id)
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


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    try:
        strategies = get_all_strategies()
        return jsonify({
            "success": True,
            "data": strategies
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