import numpy as np
import pandas as pd

def BOP(data): 
    BOP_data = (data['close'] - data['open'])/(data['high']-data['low'])
    return BOP_data


def MFI(data,period=14):
    typical_price = (data['close']+data['high']+data['low'])/3
    money_flow = typical_price*data['volume']
    positive_flow = []
    negative_flow = []
    for i in range(1,len(typical_price)):
        if typical_price[i] > typical_price[i-1]:
            positive_flow.append(money_flow[i])
            negative_flow.append(0)
        elif typical_price[i] < typical_price[i-1]:
            negative_flow.append(money_flow[i])#money_flow[i-1]?
            positive_flow.append(0)
        else:
            positive_flow.append(0)
            negative_flow.append(0)
    positive_mf = []
    negative_mf = []
    for i in range(period-1,len(positive_flow)):
        positive_mf.append(sum(positive_flow[i+1-period : i+1]))
    for i in range(period-1,len(negative_flow)):
        num = sum(negative_flow[i+1-period : i+1])        
        negative_mf.append(0.0001 if num==0 else num)
    #mfi = 100 * np.array(positive_mf) / (np.array(positive_mf) + np.array(negative_mf))
    mfi = 100 - 100 / (1 +  (np.array(positive_mf)/np.array(negative_mf)))
    return [float('Nan')]*period+list(mfi)


def Stochastic_Fast_K(data,n=14):
    fast_k = ((data['close'] - data['low'].rolling(n).min()) / (data['high'].rolling(n).max() - data['low'].rolling(n).min()))*100
    return fast_k

def RSI(data,period= 14):
    delta = data['close'].diff()
    ups,downs = delta.copy(), delta.copy()
    ups[ups<0] = 0
    downs[downs>0] = 0
    AU = ups.ewm(com = period-1,min_periods = period).mean()
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean()
    RS = AU/AD    
    return pd.Series(100-(100/(1+RS)),name = 'RSI')
