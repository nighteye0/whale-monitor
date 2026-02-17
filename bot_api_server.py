from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize Binance client
api_key = os.getenv('BINANCE_API_KEY', 'demo')
api_secret = os.getenv('BINANCE_API_SECRET', 'demo')
client = Client(api_key, api_secret)

signals_data = {
    'whale_signals': [],
    'memecoin_signals': [],
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

@app.route('/api/chart/<symbol>', methods=['GET'])
def get_chart(symbol):
    """Get price history for charts"""
    try:
        interval = request.args.get('interval', '1m')
        limit = request.args.get('limit', 50, type=int)
        
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        
        data = []
        for k in klines:
            data.append({
                'time': int(k[0]),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[7]),
                'timestamp': datetime.fromtimestamp(int(k[0])/1000).isoformat()
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'signals': len(signals_data['whale_signals'])})

if __name__ == '__main__':
    print("🚀 API Server on http://localhost:5001 with Charts Support")
    app.run(host='0.0.0.0', port=5001, debug=False)
