import logging

from binance.lib.utils import config_logging
from binance.um_futures import UMFutures

config_logging(logging, logging.DEBUG)

URL="https://testnet.binancefuture.com"
KEY="f95087fa4aeeaedc68d261715861969c8752f1665b8365c673824522860df98d"
SECRET="5f2f9ec7780bf5b1f27aaef4ca56143b1a4692271d32f0e8317e4da26024d364"

client = UMFutures(KEY, SECRET, base_url=URL)

def place_order(symbol, quantity, order_type, price=None):
  print(symbol, quantity, order_type, price)
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
