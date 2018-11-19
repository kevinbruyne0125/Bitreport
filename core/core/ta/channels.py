import numpy as np
import talib #pylint: skip-file
import config

Config = config.BaseConfig()

def last_channel():
    NotImplemented

def save_channel():
    NotImplemented

def make_channel(data: dict):

    new_channel = channel(data)
    old_channel = last_channel()

    # Compare channel
    NotImplemented


def tokens(close, upper_band, lower_band, slope):
    margin = Config.MARGIN
    info = []
    p = ( close[-1] - lower_band[-1-margin] ) / (upper_band[-1-margin]-lower_band[-1-margin]) 

    # Price Tokens
    if p > 1:
        info.append('PRICE_BREAK_UP')
    elif p < 0:
        info.append('PRICE_BREAK_DOWN')
    elif p > 0.95:
        info.append('PRICE_ONBAND_UP')
    elif p < 0.05:
        info.append('PRICE_ONBAND_DOWN')
    else:
        info.append('PRICE_BETWEEN')

    n_last_points = 10
    if np.sum(close[-n_last_points:] > upper_band[-n_last_points-margin : -margin]) > 0 and close[-1] < upper_band[-1-margin]:
        info.append('FALSE_BREAK_UP')
    elif np.sum(close[-n_last_points:] < lower_band[-n_last_points-margin : -margin]) > 0 and close[-1] > lower_band[-1-margin]:
        info.append('FLASE_BREAK_DOWN')

    # Drirection Tokens
    if slope < -0.2:
        info.append('DIRECTION_DOWN')
    elif slope > 0.2:
        info.append('DIRECTION_UP')
    else:
        info.append('DIRECTION_HORIZONTAL')
    
    return info

def channel(close, x_dates, sma_type: int = 50):
    margin = Config.MARGIN
    start = Config.MAGIC_LIMIT
    limit = close.size
    x_dates = np.array(x_dates) / 10000 # to increase precision
    short_close = close[start:]

    sma = talib.SMA(close, timeperiod = sma_type)
    sma = (short_close - sma[start:]) / sma[start:]
    sma = np.where(sma >=0, 1., -1.)
    filter_value =5
    f1 = np.where(talib.SMA(sma, timeperiod = filter_value)[filter_value:] >= 0.0, 1., -1.)
    f2 = np.where(talib.SMA(f1, timeperiod = 2) == 0.0 , 1., 0.)
    points, = np.where(f2>0)
    ch_points = np.array([0] + (points+filter_value).tolist())

    
    # If price was below / above the SMA then ch_points could contain only 1 point
    if len(ch_points) < 2:
        if ch_points == []:
            s, e = 0, limit
        elif ch_points[0] < limit/2.0:
            s, e = ch_points[0], limit
        else:
            s, e = 0, ch_points[0]
    else:
        # Find longest channel
        lenghts = ch_points[1:] - ch_points[:-1]
        s_position = np.where(lenghts == np.max(lenghts))[0][0]
        s, e = ch_points[s_position], ch_points[s_position+1]
    
    # Calculate channel and slope
    x = x_dates[:-margin][s: e]
    y = short_close[s: e]
    print(x.size, y.size)

    lm = np.poly1d(np.polyfit(x,y, 1))
    std = np.std(short_close[s:e])     
    slope = lm[0]
    
    # Prepare channel
    up_channel= lm(x_dates) + 2 * std
    bottom_channel = lm(x_dates) - 2 * std
    
     # TOKENS
    info = tokens(short_close, up_channel, bottom_channel, slope)

    params = {'slope':slope, 'coef': lm[1]}

    return {'upper_band': up_channel.tolist(), 'lower_band': bottom_channel.tolist(), 'middle_band':[], 'info': info}
    