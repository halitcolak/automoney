import numpy as np
import pandas as pd


# Hareketli ortalama türlerinin hesaplanması
def sma(series, length):
    return series.rolling(window=length).mean()

def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def dema(series, length):
    ema1 = ema(series, length)
    ema2 = ema(ema1, length)
    return 2 * ema1 - ema2

def tema(series, length):
    ema1 = ema(series, length)
    ema2 = ema(ema1, length)
    ema3 = ema(ema2, length)
    return 3 * ema1 - 3 * ema2 + ema3

def wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(window=length).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)

def vwma(price, volume, length):
    return (price * volume).rolling(window=length).sum() / volume.rolling(window=length).sum()

def hull_ma(series, length):
    half_len = int(length / 2)
    sqrt_len = int(np.sqrt(length))
    return wma(2 * wma(series, half_len) - wma(series, length), sqrt_len)

def alma(series, length, offset=0.85, sigma=6):
    m = offset * (length - 1)
    s = length / sigma
    w = np.exp(-((np.arange(length) - m)**2) / (2 * s**2))
    return np.sum(series[-length:] * w) / np.sum(w)

# Close ve Open serilerinin hesaplanması
def variant(series, basis_type, length, offset_sigma=6, offset_alma=0.85):
    if basis_type == "EMA":
        return ema(series, length)
    elif basis_type == "DEMA":
        return dema(series, length)
    elif basis_type == "TEMA":
        return tema(series, length)
    elif basis_type == "WMA":
        return wma(series, length)
    elif basis_type == "VWMA":
        return vwma(series, series, length)
    elif basis_type == "HullMA":
        return hull_ma(series, length)
    elif basis_type == "ALMA":
        return alma(series, length, offset_alma, offset_sigma)
    else:
        return sma(series, length)

# Crossover ve Crossunder fonksiyonları
def crossover(series1, series2):
    return series1.shift(1) < series2.shift(1) and series1 > series2

def crossunder(series1, series2):
    return series1.shift(1) > series2.shift(1) and series1 < series2

def calculate_strategy2(df):
  # Zaman serilerinin tanımlanması (örn. Open ve Close)
  # df, verinin saklandığı DataFrame, df['close'] ve df['open'] sütunları olmalı
  df['close_series'] = variant(df['close'], 'DEMA', 2)
  df['open_series'] = variant(df['open'], 'DEMA', 2)

  # Long ve Short sinyalleri
  df['xlong'] = crossover(df['close_series'], df['open_series'])
  df['xshort'] = crossunder(df['close_series'], df['open_series'])

  # İşlem mantığı
  df['position'] = 0
  df['position'] = np.where(df['xlong'], 1, df['position'])
  df['position'] = np.where(df['xshort'], -1, df['position'])

  # İşlem açma/kapama ve kâr/zarar durdurma
  initial_cash = 100000
  cash = initial_cash
  position = 0
  for i in range(1, len(df)):
      if df['position'].iloc[i] == 1:  # Long pozisyon aç
          position = cash / df['close'].iloc[i]
          cash = 0
      elif df['position'].iloc[i] == -1 and position > 0:  # Long pozisyon kapat
          cash = position * df['close'].iloc[i]
          position = 0

  final_value = cash + position * df['close'].iloc[-1] if position > 0 else cash
  print("Final Portfolio Value:", final_value)


def calculate_strategy(df):
    df['close_series'] = dema(df['close'], 2)
    df['open_series'] = dema(df['open'], 2)

    df['xlong'] = (df['close_series'].shift(1) < df['open_series'].shift(1)) & (df['close_series'] > df['open_series'])
    df['xshort'] = (df['close_series'].shift(1) > df['open_series'].shift(1)) & (df['close_series'] < df['open_series'])

    return df