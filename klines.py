import json
import logging
import pprint
from collections import deque

import numpy as np
import pandas as pd
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import \
    UMFuturesWebsocketClient

from order import place_order
from strategy import calculate_strategy

config_logging(logging, logging.DEBUG)
data_queue = deque(maxlen=5000)

def message_handler(_, message):
  json_message = json.loads(message)
  if 'k' in json_message:
    kline = json_message['k']
    data_queue.append({
      'time': pd.to_datetime(kline['t'], unit='ms'),
      'open': float(kline['o']),
      'high': float(kline['h']),
      'low': float(kline['l']),
      'close': float(kline['c']),
      'volume': float(kline['v'])
    })
    df = pd.DataFrame(list(data_queue))
    df = calculate_strategy(df)

    if not df.empty:
      last_row = df.iloc[-1]
      if last_row['xlong']:
        place_order("BTCUSDT", 1, "buy", kline["c"])
        print("Long sinyali tespit edildi")
      elif last_row['xshort']:
        place_order("BTCUSDT", 1, "sell", kline["c"])
        print("Short sinyali tespit edildi")

    #pprint.pprint(kline)

def on_open(ws):
  print('opened connection')

def on_close(ws):
  print('closed connection')

def start_websocket(symbol, interval="1d"):
  my_client = UMFuturesWebsocketClient(
    on_open=on_open,
    on_close=on_close,
    on_message=message_handler,
    stream_url='wss://stream.binancefuture.com'
  )
  my_client.kline(symbol=symbol, interval=interval)
  return my_client

if __name__ == "__main__":
  start_websocket('BTCUSDT')
