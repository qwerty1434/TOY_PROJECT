
import asyncio 
import pyupbit
import pandas as pd
import time
import datetime
import math
import sys
import numpy as np

import sys
sys.path.append('//path')
from tools import BOP,MFI,Stochastic_Fast_K,RSI
from upbit_tools import asset,one_tick,market_status,sell_price

import requests
from bs4 import BeautifulSoup


#로그인
txt = 'upbit아이디비밀번호.txt'
f = open(txt, 'r')
lines = f.readlines()
f.close()

access_key = lines[0].replace('\n','')
secret_key = lines[1].replace('\n','')
upbit = pyupbit.Upbit(access_key, secret_key)

test_token = True
    
life = [0,0]

#시장에서 거래되는 코인의 종류(이름들)
coin_list = pyupbit.get_tickers(fiat="KRW") #일봉기준 rsi가 70을 초과하면 리스트에서 제외한다?

done_list = []
check_list = []

q = upbit.get_balances()
for i in q[1:]:
    if i['currency'] == 'APENFT': #PENFT제외
        continue        
    if len(upbit.get_order('KRW-'+i['currency'])) == 0:
        continue
    check_list.append(upbit.get_order('KRW-'+i['currency'])[0]['uuid'])



def sell_process(revenue=1.01):
    global created_at #왜 이거 global이 필요?
    global life
    today = datetime.datetime.now() - datetime.timedelta(hours=9)     
    yr = today.year
    mth = today.month
    dy = today.day
    file_name = str(yr)+str("-")+str(mth)+str("-")+str(dy)       
    global check_list
    global done_list
    today = datetime.datetime.now() - datetime.timedelta(hours=9)     
    
    #9시에 life reset
    if today.hour == 0 and today.minute == 0:
        life = [0,0]
    
        

    q = upbit.get_balances()
    for i in q[1:]: #KRW은 제외
        if i['currency'] == 'APENFT': #PENFT제외
            continue        
        
        try:
            if limit_order['uuid'] not in check_list and limit_order['uuid'] not in done_list:
                check_list.append(limit_order['uuid'])
                
            
            for x in check_list:
                if upbit.get_order(x)['state'] == 'done' and x not in done_list:
                    done_list.append(x)                
                    life.append(life[-1]+1)
                    check_list.remove(x)
            
        except:
            pass
        
        current_price = pyupbit.get_current_price('KRW-'+i['currency']) #현재가격
        
        if (float(i['avg_buy_price'])*1.01+one_tick(float(i['avg_buy_price'])) <= current_price):
            ret = upbit.sell_market_order('KRW-'+i['currency'],i['balance'])#시장가로 판매 -> 판매가격이 얼마인지 모르나?
            if 'error' in ret.keys():
                print(ret)
                pass
            else:
                life.append(life[-1]+1)
           
            
            
        if (current_price <= float(i['avg_buy_price'])*0.99+one_tick(float(i['avg_buy_price']))):    
            try:
                #예약주문 있으면 취소                
                ret = upbit.get_order("KRW-"+i['currency'])
                created_at = ret[0]['created_at']
                if ret:
                    #여기 ret의 날짜를 data로 가져간다?
                    upbit.cancel_order(ret[0]['uuid'])  #이전주문 취소
                    check_list.remove(ret[0]['uuid'])
                    done_list.append(ret[0]['uuid'])
                    
            except:
                pass
            ret = upbit.sell_market_order('KRW-'+i['currency'],i['balance'])#시장가로 판매            
            if 'error' in ret.keys():
                print(ret)
                pass
            else:
                life.append(life[-1]-1)
                f.close()



async def buy():
    global life
    global limit_order
    global test_token
    
    while True:
        q = upbit.get_balances()
        
        if test_token:
            today_buy_price = 7000#Test용
        else:
            today_buy_price = int(float(q[0]['balance']))*(1-(5/10000)) - 100 #수수료 제외        
        
        if float(q[0]['balance'])<10000:
            print("현금이 부족합니다")
            await asyncio.sleep(60)
        else:
                
            for i in coin_list:
                coin = pyupbit.get_ohlcv(i,interval ='minute1',count=16)#count를 너무 적게하면 rsi를 구할수가 없다
                if coin is None:
                    continue
                coin['BOP'] = BOP(coin)
                coin['MFI'] = MFI(coin)
                coin['Sto'] = Stochastic_Fast_K(coin)
                coin['RSI'] = RSI(coin)
    
                if coin.iloc[-1]['BOP'] >=1 and coin.iloc[-1]['MFI'] < 20 and coin.iloc[-1]['Sto'] <20 and coin.iloc[-1]['RSI'] <30 and coin.iloc[-2]['RSI'] < coin.iloc[-1]['RSI']:
        
                    print(i+'는 '+str(coin['close'][-1]) +'원을 기준으로 과매도 상태이며 현재 가격은 ' + str(pyupbit.get_current_price(i)) +'원, 1분 전 저점은'+ str(coin['low'][-1]))
                    
                    price = min(float(coin['low'][-1]),float(pyupbit.get_current_price(i)))
                    
                    if price> today_buy_price:
                        count = (today_buy_price)/price #price * count = today_buy_price, today_buy_price만큼 구매
                    else:                
                        count = today_buy_price/price
                        
                    if test_token:
                        ret = upbit.buy_market_order(i, today_buy_price)#시장가 -> 이러면 동일종목을 여러개 사지 않는게 필요해보임
                    else:
                        ret = upbit.buy_limit_order(i,price,count)#종목,가격,개수 // 지정가
                    
                    print(i+"코인을 "+str(price)+'가격에 '+str(count)+"개 구입 시도")        
                    
                    await asyncio.sleep(15)
                    print(ret)
                    if 'error' in ret.keys():
                        print(ret)
                        continue
                    
                    result = upbit.get_order(ret['uuid'])

                    try:
                        #지정가
                        if result['ord_type'] == 'limit':
                            if int(float(result['remaining_volume'])) != 0 :
                                print("구매취소")
                                ret = upbit.cancel_order(ret['uuid'])
                            else:                        
                                print("구매성공")
                                #구매와 동시에 1% 지정가 주문 걸어두기
                                limit_order = upbit.sell_limit_order(result['market'],sell_price(float(result['price'])*1.01,float(result['price']),1.01),result['volume'])
                                
                                pass
                        #시장가
                        else:
                            print("구매성공(시장가)")
                            limit_order = upbit.sell_limit_order(result['market'],sell_price(float(result['trades'][0]['price'])*1.01,float(result['trades'][0]['price']),1.01),result['executed_volume'])
                                                                                     

                    except:
                        pass
                    
                            
                            
        await asyncio.sleep(10)
        
        if life[-1] == -1 and (life[-2] == 0):
            
            a = asset()
            print("You Lose Today\'s Game. Your Balance is ",a)         
            
            #다음날 8시59분까지 잠자기
            tomorrow = datetime.datetime.now()+datetime.timedelta(hours =24)        
            sleep_time = datetime.datetime(tomorrow.date().year,tomorrow.date().month,tomorrow.date().day,9,0,0) - datetime.datetime.now()
            life = [0,0]
            test_token = True
            await asyncio.sleep(sleep_time.seconds-60)
            
    
        elif ((life[-1] == 1) and (life[-2] == 2)):
            
            a = asset()
            print("You Win Today\'s Game. Your Balance is ",a)
            
            #다음날 8시59분까지 잠자기
            tomorrow = datetime.datetime.now()+datetime.timedelta(hours =24)        
            sleep_time = datetime.datetime(tomorrow.date().year,tomorrow.date().month,tomorrow.date().day,9,0,0) - datetime.datetime.now()
            life = [0,0]
            test_token = True
            await asyncio.sleep(sleep_time.seconds-60)
            



        print("buy loop is ok",datetime.datetime.now(),life)
        
        



async def sell():
    while True:
        if len(upbit.get_balances()) > 2:
            sell_process()        
        await asyncio.sleep(2)
        print("sell loop is ok",datetime.datetime.now(),life)







async def main():
    one = buy()
    two = sell()
    await asyncio.gather(
        one,
        two,
        )
asyncio.run(main())

