import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def variant(type, src, length, offSig, offALMA):
    v2 = src.ewm(span=length, adjust=False).mean()
    if type == "DEMA":
        v3 = 2 * v2 - v2.ewm(span=length, adjust=False).mean()
        return v3
    else:
        v4 = 3 * (v2 - v2.ewm(span=length, adjust=False).mean()) + v2.ewm(span=length, adjust=False).mean().ewm(span=length, adjust=False).mean()
        return v4

def reso(series, use, res):
    if use:
        return series.resample(res).last().ffill()
    else:
        return series

def crossover(series1, series2):
    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

def crossunder(series1, series2):
    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))

# Parametreler
useRes = True
intRes = 7
basisType = "DEMA"
basisLen = 2
offsetSigma = 6
offsetALMA = 0.85
delayOffset = 0
tradeType = "BOTH"
ebar = 5000

# Veri yükleme
data = pd.read_csv("your_data.csv", index_col="Date", parse_dates=True)

# delayOffset uygulama
close = data["Close"].shift(delayOffset)
open_ = data["Open"].shift(delayOffset)

# Seri hesaplamaları
closeSeries = variant(basisType, close, basisLen, offsetSigma, offsetALMA)
openSeries = variant(basisType, open_, basisLen, offsetSigma, offsetALMA)

# Zaman dilimi ayarlama
stratRes = f'{intRes}D'  # Örneğin, 7 günlük zaman dilimi
closeSeriesAlt = reso(closeSeries, useRes, stratRes)
openSeriesAlt = reso(openSeries, useRes, stratRes)

# Sinyal hesaplamaları
xlong = crossover(closeSeriesAlt, openSeriesAlt)
xshort = crossunder(closeSeriesAlt, openSeriesAlt)

# Pozisyonlar
positions = pd.DataFrame(index=closeSeriesAlt.index)
positions['position'] = 0

for i in range(1, len(positions)):
    if (ebar == 0 or i <= ebar) and tradeType != "NONE":
        if xlong.iloc[i] and tradeType in ["BOTH", "LONG"]:
            positions['position'].iloc[i] = 1
        elif xshort.iloc[i] and tradeType in ["BOTH", "SHORT"]:
            positions['position'].iloc[i] = -1
        else:
            positions['position'].iloc[i] = positions['position'].iloc[i-1]
    else:
        positions['position'].iloc[i] = positions['position'].iloc[i-1]

# Görselleştirme
plt.figure(figsize=(14, 7))
plt.plot(data['Close'], label='Close Price')
plt.plot(closeSeriesAlt, label='Close Series')
plt.plot(openSeriesAlt, label='Open Series')
plt.legend()
plt.show()

# Sonuçların çıktılanması
print(positions.tail())
