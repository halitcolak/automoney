from binance.um_futures import UMFutures
from order.order import place_order
import logging
import pandas as pd
import numpy as np
import time

client = UMFutures()

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

def trading_bot(symbol):
  position = None

  while True:
    data = get_historical_klines(symbol, '1h', '1 day ago UTC', 'now UTC')
    data = calculate_macd(data)

    macd = data['MACD'].iloc[-1]
    signal = data['Signal'].iloc[-1]

    if macd > signal and position != 'long':
      place_order(symbol, 1, 'buy', price=data['close'].iloc[-1])
      position = 'long'
      print(f"Alım yapıldı: {data['timestamp'].iloc[-1]}")

    elif macd < signal and position != 'short':
      place_order(symbol, 1, 'sell', price=data['close'].iloc[-1])
      position = 'short'
      print(f"Satış yapıldı: {data['timestamp'].iloc[-1]}")
    time.sleep(3600)

if __name__ == "__main__":
    trading_bot('BTCUSDT')
