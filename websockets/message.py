import json
import os
from collections import deque

import pandas as pd
from binance.websocket.um_futures.websocket_client import \
    UMFuturesWebsocketClient
from dotenv import load_dotenv

from config import Config
from process.initialize_data import initialize_data
from websockets.close import on_close
from websockets.open import on_open

load_dotenv()
WS_URL=os.getenv("WS_URL")
data_queue = deque(maxlen=5000)

def start_websocket():
  global data_queue
  data_queue = initialize_data(Config.symbol, Config.interval)

  my_client = UMFuturesWebsocketClient(
    on_open=on_open,
    on_close=on_close,
    on_message=message_handler,
    stream_url=WS_URL
  )
  my_client.kline(symbol=Config.symbol, interval=Config.interval)
  return my_client

def message_handler(_, message):
  df = pd.DataFrame(data_queue)
  json_message = json.loads(message)
  if 'k' in json_message:
    kline = json_message['k']
    if kline["x"] == True:
      data_queue.append({
        'Open Time': pd.to_datetime(kline['t'], unit='ms'),
        'Open': float(kline['o']),
        'High': float(kline['h']),
        'Low': float(kline['l']),
        'Close': float(kline['c']),
        'Volume': float(kline['v']),
        'Close Time': pd.to_datetime(kline['T'], unit='ms')
      })
  print(df)

"""
def message_handler(message):
  data_queue = initialize_data("BTCUSDT", data_queue)
  df = pd.DataFrame(data_queue)
  json_message = json.loads(message)
  if 'k' in json_message:
    kline = json_message['k']
    if kline["x"] == True:
      data_queue.append({
        'Open Time': pd.to_datetime(kline['t'], unit='ms'),
        'Open': float(kline['o']),
        'High': float(kline['h']),
        'Low': float(kline['l']),
        'Close': float(kline['c']),
        'Volume': float(kline['v']),
        'Close Time': pd.to_datetime(kline['T'], unit='ms')
      })
      df = pd.DataFrame(data_queue)
      strategy = apply_strategy(df)
      latest_row = strategy.tail(1).iloc[0]
      if latest_row['xlong']:
        if first:
          place_order(kline["s"], 1, "sell", kline["c"])
        place_order(kline["s"], 1, "buy", kline["c"])
        first = True
      elif latest_row['xshort']:
        if first:
          place_order(kline["s"], 1, "buy", kline["c"])
        place_order(kline["s"], 1, "sell", kline["c"])
        first = True
"""