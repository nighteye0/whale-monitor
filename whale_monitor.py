"""
QWEN3 8B WHALE MONITOR WITH TELEGRAM ALERTS + API
Get real-time signals on your phone AND website!
"""

import json
import asyncio
import numpy as np
from datetime import datetime
import logging
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

API_URL = 'http://localhost:5001/api'

class Qwen3WhaleMonitor:
    def __init__(self, api_key: str, api_secret: str, symbols: list):
        self.client = Client(api_key, api_secret)
        self.symbols = symbols
        self.ollama_host = "http://localhost:11434"
        self.ollama_model = "qwen3:8b"
        
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.last_alert = {}
        
        print("="*70)
        print("🚀 QWEN3 8B WHALE MONITOR WITH TELEGRAM + API")
        print("="*70)
        print(f"Model: Qwen3 8B")
        print(f"Monitoring: {len(symbols)} tokens")
        print(f"API: {API_URL}")
        if self.telegram_token and self.telegram_chat_id:
            print(f"📱 Telegram: ✅ ENABLED")
        else:
            print(f"📱 Telegram: ❌ DISABLED")
        print("="*70 + "\n")
        
        if self.telegram_token and self.telegram_chat_id:
            self.send_startup_message()
    
    def send_startup_message(self):
        """Send startup notification"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            message = f"""✅ <b>Whale Monitor Started</b>

🐋 <b>Monitoring:</b> {len(self.symbols)} tokens
🤖 <b>Model:</b> Qwen3 8B
📊 <b>API:</b> {API_URL}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Ready to detect whale activity!"""
            
            response = requests.post(url, json={
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=10)
            
            if response.status_code == 200:
                print("✅ Startup message sent to Telegram\n")
        except Exception as e:
            print(f"⚠️  Startup message error: {e}\n")
    
    def send_telegram_alert(self, message: str, symbol: str = ""):
        """Send alert to Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
        
        key = f"{symbol}_last_alert"
        now = datetime.now().timestamp()
        
        if key in self.last_alert:
            if now - self.last_alert[key] < 300:
                return False
        
        self.last_alert[key] = now
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            response = requests.post(url, json={
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram alert sent for {symbol}")
                return True
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def send_to_api(self, signal):
        """Send signal to API server"""
        try:
            requests.post(f'{API_URL}/whale-signals', json=signal, timeout=5)
        except:
            pass
    
    def get_current_price(self, symbol: str) -> dict:
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            klines = self.client.get_klines(symbol=symbol, interval='1d', limit=2)
            if len(klines) >= 2:
                prev = float(klines[0][4])
                change = ((price - prev) / prev) * 100
            else:
                change = 0
            
            return {'price': price, 'change_24h': round(change, 2)}
        except:
            return {'price': 0, 'change_24h': 0}
    
    def analyze_orderbook(self, symbol: str) -> dict:
        try:
            ob = self.client.get_order_book(symbol=symbol, limit=50)
            bid_vol = sum(float(b[1]) for b in ob['bids'])
            ask_vol = sum(float(a[1]) for a in ob['asks'])
            ratio = bid_vol / ask_vol if ask_vol > 0 else 0
            
            if ratio > 1.2:
                signal = 'WHALE_BUY'
            elif ratio < 0.83:
                signal = 'WHALE_SELL'
            else:
                signal = 'BALANCED'
            
            return {'bid_ask_ratio': round(ratio, 3), 'signal': signal}
        except:
            return {'signal': 'N/A'}
    
    def analyze_volume(self, symbol: str) -> dict:
        try:
            klines = self.client.get_klines(symbol=symbol, interval='1m', limit=50)
            if not klines or len(klines) < 20:
                return {'signal': 'N/A'}
            
            vols = np.array([float(k[7]) for k in klines])
            ratio = vols[-1] / np.mean(vols[-20:])
            
            return {
                'spike_ratio': round(ratio, 2),
                'signal': 'VOLUME_SPIKE' if ratio > 2.0 else 'NORMAL'
            }
        except:
            return {'signal': 'N/A'}
    
    def analyze_momentum(self, symbol: str) -> dict:
        try:
            klines = self.client.get_klines(symbol=symbol, interval='5m', limit=50)
            if not klines or len(klines) < 12:
                return {'signal': 'N/A'}
            
            closes = np.array([float(k[4]) for k in klines])
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50
            
            if rsi > 70:
                signal = 'STRONG_UP'
            elif rsi < 30:
                signal = 'STRONG_DOWN'
            else:
                signal = 'NEUTRAL'
            
            return {'rsi': round(rsi, 2), 'signal': signal}
        except:
            return {'signal': 'N/A'}
    
    def get_qwen3_analysis(self, symbol: str, data: dict, price: dict) -> dict:
        prompt = f"""Analyze {symbol}:
PRICE: ${price['price']:,.2f} (24h: {price['change_24h']:+.2f}%)
Orderbook: {data['orderbook'].get('signal')}
Volume: {data['volume'].get('signal')}
Momentum: {data['momentum'].get('signal')}

Recommend BUY/SELL/HOLD. Format:
ACTION: BUY
CONFIDENCE: 0.75"""
        
        try:
            r = requests.post(f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2
                },
                timeout=30)
            
            if r.status_code == 200:
                resp = r.json()['response']
                action = 'HOLD'
                conf = 0.5
                
                if 'BUY' in resp.upper():
                    action = 'BUY'
                elif 'SELL' in resp.upper():
                    action = 'SELL'
                
                for line in resp.split('\n'):
                    if 'CONFIDENCE:' in line.upper():
                        try:
                            conf = float(line.split(':')[-1].strip())
                        except:
                            pass
                
                return {
                    'action': action,
                    'confidence': min(1.0, max(0.0, conf))
                }
            
            return {'action': 'HOLD', 'confidence': 0.5}
        except:
            return {'action': 'HOLD', 'confidence': 0.5}
    
    def generate_signal(self, symbol: str):
        print(f"\n{'='*70}")
        print(f"🐋 {symbol}")
        print(f"{'='*70}")
        
        price = self.get_current_price(symbol)
        print(f"💰 ${price['price']:,.2f} ({price['change_24h']:+.2f}% 24h)")
        
        data = {
            'orderbook': self.analyze_orderbook(symbol),
            'volume': self.analyze_volume(symbol),
            'momentum': self.analyze_momentum(symbol)
        }
        
        print(f"🔍 Orderbook: {data['orderbook'].get('signal')} | "
              f"Volume: {data['volume'].get('signal')} | "
              f"Momentum: {data['momentum'].get('signal')}")
        
        print(f"💭 Qwen3 analyzing...")
        ai = self.get_qwen3_analysis(symbol, data, price)
        
        print(f"📊 {ai['action']} ({ai['confidence']:.0%} confidence)")
        
        # Send to API
        self.send_to_api({
            'symbol': symbol,
            'price': price['price'],
            'change_24h': price['change_24h'],
            'action': ai['action'],
            'confidence': ai['confidence'],
            'whale_signal': data['orderbook'].get('signal')
        })
        
        if ai['confidence'] >= 0.70 and ai['action'] != 'HOLD':
            emoji = "🚀" if ai['action'] == 'BUY' else "📉"
            message = f"""{emoji} <b>WHALE ALERT: {symbol}</b>

<b>Price:</b> ${price['price']:,.2f}
<b>24h Change:</b> {price['change_24h']:+.2f}%

<b>Signal:</b> <code>{ai['action']}</code>
<b>Confidence:</b> {ai['confidence']:.0%}

<b>Signals:</b>
- Orderbook: {data['orderbook'].get('signal')}
- Volume: {data['volume'].get('signal')}
- Momentum: {data['momentum'].get('signal')}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.send_telegram_alert(message, symbol)
        
        return {'symbol': symbol, 'action': ai['action'], 'confidence': ai['confidence']}
    
    async def start_monitoring(self, interval: int = 60):
        print(f"Monitoring every {interval}s...\n")
        try:
            while True:
                for symbol in self.symbols:
                    try:
                        self.generate_signal(symbol)
                    except Exception as e:
                        print(f"Error: {e}")
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n✅ Stopped")

async def main():
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')
    
    if not api_key or 'your_' in api_key:
        api_key = "demo"
        api_secret = "demo"
    
    try:
        monitor = Qwen3WhaleMonitor(api_key, api_secret, ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
        await monitor.start_monitoring(interval=60)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
