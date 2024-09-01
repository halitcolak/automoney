import numpy as np
import pandas as pd


def moving_average(src, length, type='DEMA', offsetSigma=6, offsetALMA=0.85):
    if type == 'DEMA':
        ema = src.ewm(span=length, adjust=False).mean()
        dema = 2 * ema - ema.ewm(span=length, adjust=False).mean()
        return dema
    # Add other moving average types here based on the Pine Script
    return src.rolling(window=length).mean()  # Default to SMA

def apply_strategy(data, basisType='DEMA', basisLen=2, offsetSigma=6, offsetALMA=0.85):
    data['closeSeries'] = moving_average(data['Close'], basisLen, type=basisType, offsetSigma=offsetSigma, offsetALMA=offsetALMA)
    data['openSeries'] = moving_average(data['Open'], basisLen, type=basisType, offsetSigma=offsetSigma, offsetALMA=offsetALMA)
    
    # Generate crossover signals
    data['xlong'] = (data['closeSeries'] > data['openSeries']) & (data['closeSeries'].shift(1) <= data['openSeries'].shift(1))
    data['xshort'] = (data['closeSeries'] < data['openSeries']) & (data['closeSeries'].shift(1) >= data['openSeries'].shift(1))
    
    # Example of entering and exiting trades
    data['position'] = np.where(data['xlong'], 1, np.where(data['xshort'], -1, np.nan))
    data['position'] = data['position'].ffill().fillna(0)  # Use ffill() directly to forward-fill positions
    
    # Optional: Add stop-loss and take-profit logic here
    
    return data
