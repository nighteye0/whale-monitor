from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

signals_data = {
    'whale_signals': [],
    'memecoin_signals': [],
    'performance': {'total_trades': 0, 'win_rate': 0, 'total_profit': 0}
}

@app.route('/api/whale-signals', methods=['GET'])
def get_whale_signals():
    limit = request.args.get('limit', 50, type=int)
    return jsonify({'signals': signals_data['whale_signals'][-limit:], 'total': len(signals_data['whale_signals'])})

@app.route('/api/whale-signals', methods=['POST'])
def add_whale_signal():
    data = request.json
    signal = {
        'id': len(signals_data['whale_signals']) + 1,
        'timestamp': datetime.now().isoformat(),
        'symbol': data.get('symbol'),
        'price': data.get('price'),
        'action': data.get('action'),
        'confidence': data.get('confidence'),
        'whale_signal': data.get('whale_signal')
    }
    signals_data['whale_signals'].append(signal)
    if len(signals_data['whale_signals']) > 1000:
        signals_data['whale_signals'].pop(0)
    return jsonify({'status': 'added'}), 201

@app.route('/api/memecoin-signals', methods=['GET'])
def get_memecoin_signals():
    limit = request.args.get('limit', 50, type=int)
    sorted_signals = sorted(signals_data['memecoin_signals'], key=lambda x: x.get('score', 0), reverse=True)
    return jsonify({'signals': sorted_signals[-limit:], 'total': len(signals_data['memecoin_signals'])})

@app.route('/api/memecoin-signals', methods=['POST'])
def add_memecoin_signal():
    data = request.json
    signal = {
        'id': len(signals_data['memecoin_signals']) + 1,
        'timestamp': datetime.now().isoformat(),
        'symbol': data.get('symbol'),
        'score': data.get('score'),
        'risk_level': data.get('risk_level')
    }
    signals_data['memecoin_signals'].append(signal)
    if len(signals_data['memecoin_signals']) > 500:
        signals_data['memecoin_signals'].pop(0)
    return jsonify({'status': 'added'}), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    whale_signals = signals_data['whale_signals']
    buy_count = len([s for s in whale_signals if s.get('action') == 'BUY'])
    return jsonify({'whale_signals': {'total': len(whale_signals), 'buy': buy_count}, 'memecoin_signals': {'total': len(signals_data['memecoin_signals'])}})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 API Server Started on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
