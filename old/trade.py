# trade_bot.py

from binance.client import Client
from binance_f import RequestClient
from binance_f.model.constant import *
from prophet import Prophet
import pandas as pd
import datetime

# Binance API anahtarları
api_key = 'f95087fa4aeeaedc68d261715861969c8752f1665b8365c673824522860df98d'
api_secret = '5f2f9ec7780bf5b1f27aaef4ca56143b1a4692271d32f0e8317e4da26024d364'

# Binance Futures API'ye bağlanma
client = RequestClient(api_key=api_key, secret_key=api_secret)

def get_historical_klines(symbol, interval, start_str, end_str):
    # Geçmiş fiyat verilerini al
    klines = client.get_klines(symbol=symbol, interval=interval, startTime=start_str, endTime=end_str)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['close'] = data['close'].astype(float)
    return data[['timestamp', 'close']]

def predict_price(data):
    # Prophet ile fiyat tahmini
    data = data.rename(columns={'timestamp': 'ds', 'close': 'y'})
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']]

def place_order(symbol, quantity, order_type, price=None):
    # Alım/Satım emri gönder
    if order_type == 'buy':
        order = client.post_order(symbol=symbol, side=OrderSide.BUY, ordertype=OrderType.LIMIT, 
                                  timeInForce=TimeInForce.GTC, quantity=quantity, price=price)
    elif order_type == 'sell':
        order = client.post_order(symbol=symbol, side=OrderSide.SELL, ordertype=OrderType.LIMIT, 
                                  timeInForce=TimeInForce.GTC, quantity=quantity, price=price)
    return order

def trading_bot(symbol):
    # Botun çalıştığı ana döngü
    while True:
        data = get_historical_klines(symbol, '1h', '1 day ago UTC', 'now UTC')
        forecast = predict_price(data)
        next_predicted_price = forecast['yhat'].iloc[-1]

        # Şu anki fiyatı al
        current_price = float(client.get_symbol_price_ticker(symbol=symbol).price)

        # Alım/Satım stratejisi
        if next_predicted_price > current_price:
            place_order(symbol, 0.001, 'buy', price=current_price)
        elif next_predicted_price < current_price:
            place_order(symbol, 0.001, 'sell', price=current_price)

        # 1 saat bekle
        time.sleep(3600)

if __name__ == "__main__":
    trading_bot('BTCUSDT')
