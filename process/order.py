import logging
import os

from binance.um_futures import UMFutures
from dotenv import load_dotenv

load_dotenv()
URL=os.getenv("BASE_URL")
KEY=os.getenv("KEY")
SECRET=os.getenv("SECRET")

client = UMFutures(KEY, SECRET, base_url=URL)

def place_order(symbol, quantity, order_type, price=None):
  if order_type.lower() == 'buy':
    buy(symbol, quantity, price)
  elif order_type.lower() == 'sell':
    sell(symbol, quantity, price)

def buy(symbol, quantity, price=None):
  response = client.new_order(
    symbol=symbol,
    side="BUY",
    type="LIMIT",
    quantity=quantity,
    timeInForce="GTC",
    price=price,
  )
  logging.info(response)
  
def sell(symbol, quantity, price=None):
  response = client.new_order(
    symbol=symbol,
    side="SELL",
    type="LIMIT",
    quantity=quantity,
    timeInForce="GTC",
    price=price,
  )
  logging.info(response)