from binance.cm_futures import CMFutures as Client
from binance.lib.utils import config_logging
from binance.error import ClientError
import logging
import pandas as pd
import numpy as np
import time

config_logging(logging, logging.DEBUG)

# Binance API anahtarları
api_key = 'f95087fa4aeeaedc68d261715861969c8752f1665b8365c673824522860df98d'
api_secret = '5f2f9ec7780bf5b1f27aaef4ca56143b1a4692271d32f0e8317e4da26024d364'

# Binance Futures API'ye bağlanma
client = Client(api_key, api_secret, base_url="https://testnet.binancefuture.com/")

def get_historical_klines(symbol, interval, start_str, end_str):
    klines = client.klines(symbol, interval=interval)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['close'] = data['close'].astype(float)
    return data[['timestamp', 'close']]

def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    data['EMA_short'] = data['close'].ewm(span=short_period, adjust=False).mean()
    data['EMA_long'] = data['close'].ewm(span=long_period, adjust=False).mean()
    data['MACD'] = data['EMA_short'] - data['EMA_long']
    data['Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal']
    return data

def place_order(symbol, quantity, order_type, price=None):
    if order_type == 'buy':
        response = client.new_order(
          symbol=symbol,
          side="BUY",
          type="LIMIT",
          quantity=quantity,
          timeInForce="GTC",
          price=price,
        )
        logging.info(response)
    elif order_type == 'sell':
        response = client.new_order(
          symbol=symbol,
          side="SELL",
          type="LIMIT",
          quantity=quantity,
          timeInForce="GTC",
          price=price,
        )
        logging.info(response)
    return order

def trading_bot(symbol):
    position = None

    while True:
        data = get_historical_klines(symbol, '1h', '1 day ago UTC', 'now UTC')
        data = calculate_macd(data)

        macd = data['MACD'].iloc[-1]
        signal = data['Signal'].iloc[-1]

        # MACD Alım/Satım sinyalleri
        if macd > signal and position != 'long':
            place_order(symbol, 0.001, 'buy', price=data['close'].iloc[-1])
            position = 'long'
            print(f"Alım yapıldı: {data['timestamp'].iloc[-1]}")

        elif macd < signal and position != 'short':
            place_order(symbol, 0.001, 'sell', price=data['close'].iloc[-1])
            position = 'short'
            print(f"Satış yapıldı: {data['timestamp'].iloc[-1]}")

        # 1 saat bekle
        time.sleep(3600)

if __name__ == "__main__":
    trading_bot('BTCUSDT')
