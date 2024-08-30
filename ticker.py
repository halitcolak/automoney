import logging

from binance.lib.utils import config_logging
from binance.um_futures import UMFutures

config_logging(logging, logging.DEBUG)

um_futures_client = UMFutures()
logging.info(um_futures_client.continuous_klines("BTCUSDT", "PERPETUAL", "5m", **{"limit": 1000}))