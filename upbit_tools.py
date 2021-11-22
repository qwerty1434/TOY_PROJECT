# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 17:33:31 2021

@author: 82104
"""

import pyupbit

def asset():
    txt = 'C:/Users/82104/Desktop/upbit아이디비밀번호.txt'
    f = open(txt, 'r')
    lines = f.readlines()
    f.close()
    
    access_key = lines[0].replace('\n','')
    secret_key = lines[1].replace('\n','')
    upbit = pyupbit.Upbit(access_key, secret_key)

    asset = 0
    for i in upbit.get_balances():
        if i['currency'] == 'KRW':            
            asset +=float(i['balance']) 
            #asset +=float(i['locked'])
        else:
            asset +=float(max(i['balance'],i['locked'])) * float(i['avg_buy_price'])#현재가격이 아니라 구매가격이라 좀 차이가 남
    return asset


def one_tick(price):
    if 1<=price<10:
        one_tick = 0.01
    elif 10<=price<100:
        one_tick = 0.1
    elif 100<=price<1000:
        one_tick =1
    elif 1000<=price<10000:
        one_tick = 5
    elif 10000<=price<100000:
        one_tick = 10
    elif 100000<=price<1000000:
        one_tick = 100
    elif 1000000<=price:
        one_tick = 1000
    elif price<1:
        one_tick = 0.001
    return one_tick



def market_status():
    import requests
    coin_list = pyupbit.get_tickers(fiat="KRW")
    today_market_status = 0
    for coin in coin_list:
        uri = f'https://api.upbit.com/v1/ticker?markets={coin}'
        response = requests.get(uri).json()
        if response[0]['change'] == 'FAll':
            today_market_status -=1
        elif response[0]['change'] == 'RISE':
            today_market_status +=1
    return today_market_status



def sell_price(current_price,buy_price,under_k):
    #1<=x<10:소숫점 둘째자리(0.01)
    #10<=x<100:소숫점 첫째자리(0.1)
    #100~1000:일의자리(1)
    #1000~10000:5원(5)
    #10000~100000:10원
    #10만~100만:100원
    #100만~:1000원
    if 1<=current_price<10:
        limit_order_price = round(buy_price*under_k,2)
    elif 10<=current_price<100:
        limit_order_price = round(buy_price*under_k,1)
    elif 100<=current_price<1000:
        limit_order_price = round(buy_price*under_k,0)
    elif 1000<=current_price<10000:
        limit_order_price = round(buy_price*under_k*2,-1)/2
    elif 10000<=current_price<100000:
        limit_order_price = round(buy_price*under_k,-1)
    elif 100000<=current_price<1000000:
        limit_order_price = round(buy_price*under_k,-2)
    elif 1000000<=current_price:
        limit_order_price = round(buy_price*under_k,-3)
    return limit_order_price