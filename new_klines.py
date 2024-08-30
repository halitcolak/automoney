import argparse
import json
import logging
import pprint
from collections import deque

import pandas as pd
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import \
    UMFuturesWebsocketClient

from new_strategy import apply_strategy
from order import place_order

URL="https://testnet.binancefuture.com"
first = True

config_logging(logging, logging.DEBUG)
data_queue = deque(maxlen=5000)

def initialize_data(symbol, interval="5m", limit=1000):
  client = UMFutures(base_url=URL)
  klines = client.continuous_klines(symbol, "PERPETUAL", interval, **{"limit": limit})
  for kline in klines:
    data_queue.append({
      'Open Time': pd.to_datetime(kline[0], unit='ms'),
      'Open': float(kline[1]),
      'High': float(kline[2]),
      'Low': float(kline[3]),
      'Close': float(kline[4]),
      'Volume': float(kline[5]),
      'Close Time': pd.to_datetime(kline[6], unit='ms')
    })
  data_queue.pop()

def message_handler(_, message):
  global first
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
    
def on_open(ws):
  print('opened connection')

def on_close(ws):
  print('closed connection')

def start_websocket(symbol, interval="5m"):
  my_client = UMFuturesWebsocketClient(
    on_open=on_open,
    on_close=on_close,
    on_message=message_handler,
    stream_url='wss://stream.binancefuture.com'
  )
  my_client.kline(symbol=symbol, interval=interval)
  return my_client

def main():
  global first
  parser = argparse.ArgumentParser(description="Uygulama açıklaması.")
  parser.add_argument("--symbol", type=str, help="İşlem yapmak istediğiniz sembol.")
  parser.add_argument("--interval", type=str, help="İşlem yapmak istediğiniz zaman dilimini seçiniz.")
  parser.add_argument("--position", type=str, help="Açık pozisyonunuzu belirtiniz.")
  
  args = parser.parse_args()
  first = True if args.position == 'True' else False
  initialize_data(args.symbol, args.interval)
  start_websocket(args.symbol, args.interval)

if __name__ == "__main__":
  main()