import talib
import numpy as np
from core.services import internal
from operator import itemgetter

###################     TAlib indicators    ###################

def BB(data, start, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    m =10000
    close = m * data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)

    upperband = upperband/m
    middleband = middleband/m
    lowerband = lowerband/m

    return {'upperband' : upperband.tolist()[start:],
            'middleband':middleband.tolist()[start:],
            'lowerband':lowerband.tolist()[start:]}



def MACD(data, start, fastperiod=12, slowperiod=26, signalperiod=9 ):
    macd, signal, hist = talib.MACD(data['close'], fastperiod, slowperiod, signalperiod)
    #
    # print('data ask macd :', data['close'].size)
    # print(len(data['date'].tolist()[slowperiod+7:]), 'macd', macd.tolist()[slowperiod:])

    # to avoid NaN values skip 7 first values...
    return {'macd' : macd.tolist()[start:],
            'signal':signal.tolist()[start:],
            'hist':hist.tolist()[start:]}


def RSI(data, start, timeperiod=14):
    real = talib.RSI(data['close'], timeperiod)

    # print('data ask rsi:', data['close'].size)
    # print(len(data['date'].tolist()[timeperiod:]), len(real.tolist()[timeperiod:]))

    return {'rsi':real.tolist()[start:]} #,'date': data['date'].tolist()[start:]}


def STOCH(data, start, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'],
                               fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
    return {'slowk': slowk.tolist()[start:], 'slowd': slowd.tolist()[start:]}


def STOCHRSI(data, start, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
    fastk, fastd = talib.STOCHRSI(data['close'], timeperiod, fastk_period, fastd_period, fastd_matype)
    return {'fastk': fastk.tolist()[start:], 'fastd': fastd.tolist()[start:]}


def MOM(data, start, timeperiod=10):
    real = talib.MOM(data['close'], timeperiod)
    return {'mom': real.tolist()[start:]}


def ADX(data, start, timeperiod=14):
    real = talib.ADX(data['high'], data['low'], data['close'], timeperiod)
    return {'adx': real.tolist()[start:]}


def AROON(data, start, timeperiod=14):
    aroondown, aroonup = talib.AROON(data['high'], data['low'], timeperiod)
    return {'down': aroondown.tolist()[start:], 'up': aroonup.tolist()[start:]}


def SMA(data, start):

    periods = [10, 20 ,50]
    names = ['fast', 'medium','slow']
    dict = {}

    for i in range(len(periods)):
        real = talib.SMA(data['close'], periods[i])
        dict[names[i]] = real.tolist()[start:]

    return dict


def EMA(data, start):
    periods = [10, 20, 50]
    names = ['fast', 'medium', 'slow']
    dict = {}

    for i in range(len(periods)):
        real = talib.EMA(data['close'], periods[i])
        dict[names[i]] = real.tolist()[start:]

    return dict


def SAR(data, start):
    real = talib.SAR(data['high'], data['low'],acceleration=0.02, maximum=0.2)

    return {'sar': real.tolist()[start:]}

######### HILBERT transformations ##########

def HT(data, start):
    close = data['close']
    real = talib.HT_TRENDLINE(close)

    return {'ht': real.tolist()[start:]}


def HTmode(data, start):
    close = data['close']
    real = talib.HT_TRENDMODE(close)

    return {'htmode': real.tolist()[start:]}


def HTphasor(data, start):
    # There are two outputs of HT_SINE Sine and LeadSine.
    # Crossover of these lines anticipate turning point during cycle mode.
    # When prices are trending then Sine and LeadSine lines do not cross.

    close = data['close']
    inphase, quadrature = talib.HT_PHASOR(close)

    return {'inphase': inphase.tolist()[start:], 'quadrature':quadrature.tolist()[start:]}


def HTphase(data, start):
    # Its transition from 360 to 0 degree can be used to detect start of a new cycle when price is in cyclic mode.
    # Departure from constant rate change of phase can be used to detect end of a cycle mode.

    close = data['close']
    real = talib.HT_DCPHASE(close)

    return {'htphase': real.tolist()[start:]}


def HTperiod(data, start):
    close = data['close']
    real = talib.HT_DCPERIOD(close)

    return {'htperiod': real.tolist()[start:]}


def HTsin(data, start):
    # A clear, unequivocal cycle mode indicator can be generated by plotting the Sine of
    # the measured phase angle advanced by 45 degrees. This leading signal crosses the
    # sinewave 1/8th of a cycle BEFORE the peaks and valleys of the cyclic turning points,
    # enabling you to make your trading decision in time to profit from the entire amplitude
    # swing of the cycle. A significant additional advantage is that the two indicator lines
    # don't cross except at cyclic turning points, avoiding the false whipsaw signals of most
    # "oscillators" when the market is in a Trend Mode. The two lines don't cross because the
    # phase rate of change is nearly zero in a trend mode. Since the phase is not changing,
    # the two lines separated by 45 degrees in phase never get the opportunity to cross.

    close = data['close']
    sine, leadsine = talib.HT_SINE(close)

    return {'sine':sine.tolist()[start:], 'leadsine': leadsine.tolist()[start:]}


###################   Bitreport indicators   ###################

# Elliott Wave Oscillator:
def EWO(data, start, fast = 5, slow = 35):
    close = data['close']
    real = talib.EMA(close, fast) - talib.EMA(close, slow)
    return {'ewo': real.tolist()[start:]}


# Keltner channels:
def KC(data,start):
    # Keltner Channels
    # Middle Line: 20-day exponential moving average
    # Upper Channel Line: 20-day EMA + (2 x ATR(10))
    # Lower Channel Line: 20-day EMA - (2 x ATR(10))
    close = data['close']
    high = data['high']
    low = data['low']

    mid = talib.SMA(close, 20)
    upperch = mid + (2 * talib.ATR(high, low, close, 10))
    lowerch = mid - (2 * talib.ATR(high, low, close, 10))
    
    return {'middleband': mid.tolist()[start:], 'upperband': upperch.tolist()[start:], 'lowerband':lowerch.tolist()[start:]}


# Tom Demark Sequential
def TDS(data, start):
    close = data['close']
    low = data['low']
    high = data['high']
    m, n = 9, 4
    #m2, n2 = 13, 2

    # TD Sequential based on TD Setup 9,4
    # https://www.ethz.ch/content/dam/ethz/special-interest/mtec/chair-of-entrepreneurial-risks-dam/documents/dissertation/LISSANDRIN_demark_thesis_final.pdf
    start_point = n
    td_list_type = []
    while start_point < close.size:
        # Check perfect buy:
        if (low[start_point] < low[start_point - 3] and low[start_point] < low[start_point - 2]) or (
                        low[start_point - 1] < low[start_point - 4] and low[start_point - 1] < low[
                        start_point - 3]):
            td_list_type.append('pbuy')

        # Check buy:
        elif close[start_point] < close[start_point - n]:
            td_list_type.append('buy')

        # Check perfect sell
        elif (high[start_point] > high[start_point - 3] and high[start_point] > high[start_point - 2]) or (
                        high[start_point - 1] > high[start_point - 4] and high[start_point - 1] > high[
                        start_point - 3]):
            td_list_type.append('psell')

        # Check sell
        elif close[start_point] > close[start_point - n]:
            td_list_type.append('sell')
        start_point += 1

    td_list_type = [0]*n + td_list_type

    return {'tds':td_list_type[start:]}


# Ichimoku Cloud:
def ICM(data, start):
    open, high, low, close=data['open'], data['high'], data['low'], data['close']
    len = close.size

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    n1=9
    #TODO: czy tu ma być [0] czy [None] ?
    conversion_line = [0]*n1
    for i in range(n1, len):
        conversion_line.append((np.max(high[i-n1:i]) + np.min(low[i-n1:i]))/2)
    conversion_line = np.array(conversion_line)

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    n2=26
    base_line = [0]*n2
    for i in range(n2, len):
         base_line.append((np.max(high[i-n2:i]) + np.min(low[i-n2:i]))/2)

    base_line = np.array(base_line)

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    leading_spanA = (conversion_line+base_line) /2

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    n3 = 52
    leading_spanB = [0]*n3
    for i in range(n3, len):
        leading_spanB.append((np.max(high[i-n3:i]) + np.min(low[i-n3:i]))/2)

    leading_spanB = np.array(leading_spanB)

    # Chikou Span (Lagging Span): Close plotted 26 days in the past
    n4 = 26
    lagging_span =[]
    for i in range(0, len-n4):
        lagging_span.append(close[i+n4])
    lagging_span = np.array(lagging_span)


    return {'conversion line': conversion_line.tolist()[start:],
            'base line': base_line.tolist()[start:],
            'leading span A': leading_spanA.tolist()[start-n2:],
            'leading span B': leading_spanB.tolist()[start-n2:],
            'lagging span': lagging_span.tolist()[start:]}


# Linear indicator
def LIN(data, start, period = 20):
    close = data['close']

    indicator_values = [0] * period
    for i in range(period,close.size):
        probe_data = close[i-period : i]
        a = talib.LINEARREG_SLOPE(probe_data, period)[-1]
        b = talib.LINEARREG_INTERCEPT(probe_data, period)[-1]
        indicator_values.append(a*period+b)

    return {'lin':indicator_values[start:]}


# Linear oscillator
def LINO(data, start, period=20):
    close = data['close']

    a = talib.LINEARREG_SLOPE(close, period)
    a = np.degrees(np.arctan(a))

    return {'lino': a.tolist()[start:]}


# Correlation Oscillator
def CORRO(data, start, oscillator='RSI', period=20):
    close = data['close']

    oscillator_values = getattr(talib, oscillator)(close)

    corr_list= [0]*period
    for i in range(period, close.size):
        corr_list.append(np.corrcoef(close[i-period:i], oscillator_values[i-period:i])[0][1])

    return {'corro': corr_list[start:]}


def MOON(data, start):
    dates = data['date']
    phase_list = []

    for moment in dates:
        p = internal.what_phase(moment)
        phase_list.append(p[0])

    return {'labels': phase_list[start:], 'timestamps': dates[start:]}

################################################################


##################### TEMPORARY - must be deleted after channel implementation #############################
def channel(data, start, percent=80, margin=26):
    magic_limit = start
    close, open, high, low = data['close'], data['open'], data['high'], data['low']
    avg = (close+open)/2

    length = int(percent/100 * close.size)

    probe_data = avg[:length]
    a = talib.LINEARREG_SLOPE(probe_data, length)[-1]
    b = talib.LINEARREG_INTERCEPT(probe_data, length)[-1]

    std = talib.STDDEV(avg, timeperiod=close.size, nbdev=1)[-1]

    up_channel, bottom_channel , channel= [], [], []
    for i in range(close.size+margin):
        up_channel.append(i*a+b+std)
        bottom_channel.append(i * a + b - std)
        channel.append(i * a + b)


    return {'upperband': up_channel[magic_limit:], 'middleband': channel[magic_limit:],'lowerband':bottom_channel[magic_limit:]}


def parabola(data, start, percent=70, margin=26):
    magic_limit = start
    open = data['open']
    close = data['close']

    avg = (open+close)/2

    # mini = talib.MININDEX(close, open.size)[-1]
    # maxi = talib.MAXINDEX(close, open.size)[-1]

    start = 0 # min(mini,maxi)
    end = int(percent/100*close.size) # max(mini,maxi)+1

    x = np.array(range(start, end))
    longer_x = np.array(range(close.size+margin))

    y = avg[start : end]

    # creates parabola polynomial
    poly = np.poly1d(np.polyfit(x, y, 2))

    vector = 0 # poly(start) - open[start]
    std = talib.STDDEV(y, timeperiod=y.size, nbdev=2)[-1]

    z, zp, zm = [], [], []
    for point in longer_x:
        z.append(poly(point)-vector)
        zm.append(poly(point) - vector-std)
        zp.append(poly(point) - vector+std)

    return {'middleband': z[magic_limit:], 'upperband': zp[magic_limit:], 'lowerband':zm[magic_limit:]}


def linear(data, start, period = 30, stdl=10, offset=0):
    close = data['close']
    magic_limit = start

    indicator_values = [0] * (period+offset)
    up_channel, bottom_channel = [0] * (period+offset), [0] * (period+offset)

    for i in range(period,close.size):
        probe_data = close[i-period : i]
        a = talib.LINEARREG_SLOPE(probe_data, period)[-1]
        b = talib.LINEARREG_INTERCEPT(probe_data, period)[-1]
        y = a*(period+offset)+ b
        std = talib.STDDEV(probe_data, timeperiod=stdl, nbdev=2)[-1]

        indicator_values.append(y)
        up_channel.append(y + std)
        bottom_channel.append(y - std)

    return {'upperband': up_channel[magic_limit:], 'middleband':indicator_values[magic_limit:], 'lowerband': bottom_channel[magic_limit:]}


def wedge(data, start, margin=26):
    full_size = data['close'].size
    close = data['close'][start:]
    close_size = close.size

    point1 = talib.MAXINDEX(close, timeperiod=close_size)[-1]
    #min_index = talib.MININDEX(close, timeperiod=close_size)[-1]

    # From max_index calculate alpha for points (max_index, close(max_index)), (i, close(i))
    a_list =[]
    for i in range(point1+1, close_size-3):
        a = (close[i] - close[point1]) / (i - point1)
        b = close[i] - a * i

        a1 = (close[i] - close[point1]) / (i - point1)
        a2 = (close[i+2] - close[point1]) / (i+2 - point1)
        a3 = (close[i] - close[point1]) / (i - point1)
        if a2 < 0.6*a:
            a_list.append((i,a,b))

    break_tuple1 = max(a_list, key=itemgetter(1))
    upper_a = break_tuple1[1]
    upper_b = break_tuple1[2]
    point2 = break_tuple1[0]

    point3 = point1 + talib.MININDEX(close[point1:point2], timeperiod=point2-point1)[-1]

    a_list = []
    for i in range(point2 + 1, close_size):
        a = (close[i] - close[point3]) / (i - point3)
        b = close[i] - a * i
        a_list.append((i, a, b))

    break_tuple2 = min(a_list, key=itemgetter(1))
    lower_a = break_tuple2[1]
    lower_b = break_tuple2[2]
    point4 = break_tuple2[0]

    # check if the wedge make sense:
    up_start_value = upper_a * close[point1] + upper_b
    down_start_value = lower_a * close[point1] + lower_b

    up_end_value = upper_a * close[point4] + upper_b
    down_end_value = lower_a * close[point4] +lower_b


    if up_start_value-down_start_value < up_end_value - down_end_value:
        upper_band = [None]*(start + point1-1)
        middle_band = [None]*(full_size+margin)
        lower_band = [None]*(start + point1-1)

        for i in range(point1,close_size+margin+1):
            upper_band.append(upper_a*i + upper_b)
            lower_band.append(lower_a*i + lower_b)
    else:
        upper_band = [None] * (full_size + margin)
        middle_band = [None] * (full_size + margin)
        lower_band = [None] * (full_size + margin)

    return {'upperband': upper_band[start:],
            'middleband': middle_band[start:],
            'lowerband': lower_band[start:]}


#############################################################################################################