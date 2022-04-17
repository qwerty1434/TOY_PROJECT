# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 14:50:49 2021

@author: 82104
"""

import pyupbit
import os, glob
import datetime
import pandas as pd


def rsi(data,period= 14):
    delta = data['close'].diff()
    ups,downs = delta.copy(), delta.copy()
    ups[ups<0] = 0
    downs[downs>0] = 0
    AU = ups.ewm(com = period-1,min_periods = period).mean()
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean()
    RS = AU/AD    
    return pd.Series(100-(100/(1+RS)),name = 'RSI')



#폴더이름
yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
yr = yesterday.year
mth = yesterday.month
dy = yesterday.day
dir_name = str(yr)+str("-")+str(mth)+str("-")+str(dy)

path = f"/1분봉_매일데이터/{dir_name}"



#폴더 만들기
if os.path.isdir(path):
    os.chdir(path)
else:
    os.mkdir(path)
    os.chdir(path)

#데이터 넣기
coin_list = pyupbit.get_tickers(fiat="KRW")
for coin in coin_list:   
    df = pyupbit.get_ohlcv(coin, interval="minute1",count = 1441,to= datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, 9, 1, 0)) #하루치 데이터
    df['coin'] = coin    
    df['rsi'] = rsi(df)
    df.to_csv(f"{coin}.csv")

#하나의 csv로 병합
all_files = glob.glob(os.path.join(path, "*.csv"))
df_from_each_file = (pd.read_csv(f, sep=',') for f in all_files)
df_merged   = pd.concat(df_from_each_file, ignore_index=True)
df_merged.to_csv( f"/1분봉_매일데이터/{dir_name}_merged.csv")
