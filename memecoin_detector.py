import requests
import numpy as np
from datetime import datetime

class MemecoinDetector:
    def __init__(self, binance_client, telegram_token=None, telegram_chat_id=None):
        self.client = binance_client
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
    
    def analyze_volatility(self, symbol):
        try:
            klines = self.client.get_klines(symbol=symbol, interval='1h', limit=24)
            if not klines:
                return None
            prices = np.array([float(k[4]) for k in klines])
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns) * 100
            return {'hourly_volatility': round(volatility, 2), 'is_memecoin': volatility > 10, 'level': 'EXTREME' if volatility > 20 else 'VERY_HIGH' if volatility > 10 else 'HIGH'}
        except:
            return None
    
    def detect_pump_dumps(self, symbol):
        try:
            klines = self.client.get_klines(symbol=symbol, interval='1m', limit=100)
            if not klines:
                return None
            prices = np.array([float(k[4]) for k in klines])
            max_price = np.max(prices[-20:])
            min_price = np.min(prices[-20:])
            pump_percentage = ((max_price - min_price) / min_price) * 100
            return {'pump_detected': pump_percentage > 50, 'pump_percentage': round(pump_percentage, 2)}
        except:
            return None
    
    def check_liquidity(self, symbol):
        try:
            response = requests.get(f'https://api.dexscreener.com/latest/dex/search?q={symbol}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('pairs'):
                    pair = data['pairs'][0]
                    liquidity = pair.get('liquidity', {}).get('usd', 0)
                    return {'liquidity': round(liquidity, 0)}
        except:
            pass
        return None
    
    def score_memecoin(self, symbol):
        scores = {}
        vol = self.analyze_volatility(symbol)
        scores['volatility'] = 30 if vol and vol['is_memecoin'] else 0
        
        pump = self.detect_pump_dumps(symbol)
        scores['pump'] = 5 if pump and pump['pump_detected'] else 0
        
        liq = self.check_liquidity(symbol)
        scores['liquidity'] = 0 if liq and liq['liquidity'] < 50000 else 0
        
        total_score = sum(scores.values())
        
        return {
            'symbol': symbol,
            'total_score': total_score,
            'is_memecoin': total_score > 50,
            'volatility': vol,
            'pump': pump,
            'liquidity': liq,
            'risk': 'EXTREME' if total_score > 80 else 'HIGH' if total_score > 50 else 'MEDIUM'
        }
    
    def print_analysis(self, result):
        print("\n" + "="*70)
        print(f"MEMECOIN ANALYSIS: {result['symbol']}")
        print("="*70)
        print(f"Score: {result['total_score']}/100")
        print(f"Risk: {result['risk']}")
        if result['volatility']:
            print(f"Volatility: {result['volatility']['hourly_volatility']}%")
        if result['pump']:
            print(f"Pump: {result['pump']['pump_percentage']}%")
        if result['liquidity']:
            print(f"Liquidity: ${result['liquidity']['liquidity']}")
        print("="*70 + "\n")
