import json
import asyncio
import numpy as np
from datetime import datetime
from collections import deque
from typing import Dict, List
import logging
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from dotenv import load_dotenv

load_dotenv()

class Qwen3WhaleMonitor:
    def __init__(self, api_key, api_secret, symbols):
        self.client = Client(api_key, api_secret)
        self.symbols = symbols
        self.ollama_host = "http://localhost:11434"
        self.ollama_model = "qwen3:8b"
        print(f"✅ Qwen3WhaleMonitor initialized")
        print(f"Model: Qwen3 8B")
        print(f"Monitoring {len(symbols)} symbols")
    
    async def start_monitoring(self):
        print("Whale monitoring started with Qwen3 8B!")
        while True:
            for symbol in self.symbols:
                try:
                    print(f"\n🐋 Analyzing {symbol} with Qwen3 8B...")
                    await asyncio.sleep(60)
                except Exception as e:
                    print(f"Error: {e}")

async def main():
    api_key = os.getenv('BINANCE_API_KEY', 'your_key')
    api_secret = os.getenv('BINANCE_API_SECRET', 'your_secret')
    
    monitor = Qwen3WhaleMonitor(api_key, api_secret, ['BTCUSDT', 'ETHUSDT'])
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
