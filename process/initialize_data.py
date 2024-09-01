import os
from collections import deque

import pandas as pd
from binance.um_futures import UMFutures
from dotenv import load_dotenv

load_dotenv()
URL=os.getenv("BASE_URL")
client = UMFutures()

def initialize_data(symbol, interval="5m", limit=1000):
  data_queue = deque(maxlen=5000)
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
  return data_queue