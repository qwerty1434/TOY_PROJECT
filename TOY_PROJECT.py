# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 11:10:39 2022

@author: qwerty1434
"""

import asyncio 
import pyupbit
import datetime
import sys

sys.path.append('C:/Users/82104/Desktop/system_trading')
from tools import BOP,MFI,Stochastic_Fast_K,RSI
from upbit_tools import asset,one_tick,sell_price


# 로그인
txt = 'upbit아이디비밀번호.txt'
f = open(txt, 'r')
lines = f.readlines()
f.close()

access_key = lines[0].replace('\n','')
secret_key = lines[1].replace('\n','')
upbit = pyupbit.Upbit(access_key, secret_key)


test_token = True    
if test_token:
    token_type = "테스트"
else:
    token_type = "실전"
life = [0,0,0,0]
coin_list = pyupbit.get_tickers(fiat="KRW") # 시장에서 거래되는 코인의 종류

#지금은 완료목록과 관리해야 할 목록을 배열로 관리 -> 그 이유는 접속이 끊겼다가 다시 들어왔을 때 이전거래를 기억하지 못하기 때문에
done_list = []
check_list = []

q = upbit.get_balances()


for i in q[1:]:
    if i['currency'] == 'APENFT': # APENFT은 거래불가 코인이라 제외
        continue        
    if len(upbit.get_order('KRW-'+i['currency'])) == 0: # 빈 값을 가져오는 경우
        continue
    check_list.append(upbit.get_order('KRW-'+i['currency'])[0]['uuid']) # 지금 주문되어 있는 종목을 check_lst에 등록

async def buy():
    global life
    global limit_order
    global test_token
    global q
    global token_type
    
    while True:
        z = datetime.datetime.now()
        now_time = z.hour*60+z.minute
        
        # 실제구매시간
        if (1225<=now_time<=1250):
            test_token = False
        # 데이터 수집 시간
        else:
            test_token = True
            
            
        if test_token:
            today_buy_price = 7000#Test용
        else:
            today_buy_price = int(float(q[0]['balance']))*(1-(5/10000)) - 100 # 수수료를 제외한 전액거래, 100원은 오차조정을 위해 넣은 것
            print("전액(" + str(today_buy_price)+"원)으로 구매 진행중")

        if float(q[0]['balance'])<10000:
            print("현금이 부족합니다")
            await asyncio.sleep(600)
            continue
            
        for i in coin_list:
            coin = pyupbit.get_ohlcv(i,interval ='minute1',count=16) # count를 너무 적게하면 rsi를 구할수가 없다
            if coin is None:
                continue

            # 서로간의 관계를 바탕으로 한 추가적인 계산을 염두해 데이터 column에 추가하는 방식 활용              
            coin['BOP'] = BOP(coin)
            coin['MFI'] = MFI(coin)
            coin['Sto'] = Stochastic_Fast_K(coin)
            coin['RSI'] = RSI(coin)

            if coin.iloc[-1]['BOP'] >=1 and coin.iloc[-1]['MFI'] < 20 and coin.iloc[-1]['Sto'] <20 and coin.iloc[-1]['RSI'] <30 and coin.iloc[-2]['RSI'] < coin.iloc[-1]['RSI']:
                print(i+'는 '+str(coin['close'][-1]) +'원을 기준으로 과매도 상태이며 현재 가격은 ' + str(pyupbit.get_current_price(i)) +'원, 1분 전 저점은'+ str(coin['low'][-1]))

                price = float(pyupbit.get_current_price(i)) # 현재가격으로 구매 시도


                count = (today_buy_price)/price #price * count = today_buy_price, today_buy_price만큼 구매하기 위한 count개수

                if test_token:
                    ret = upbit.buy_market_order(i, today_buy_price) # 시장가 구매
                else:
                    ret = upbit.buy_limit_order(i,price,count) # 종목,가격,개수 // 지정가 구매

                print(i+"코인을 "+str(price)+'가격에 '+str(count)+"개 구입 시도")        

                # 해당종목 주문을 걸어두고 15초간 대기 -> 15초안에 구매안되면 취소
                await asyncio.sleep(15)
                print(ret)

                if 'error' in ret.keys():
                    print("에러발생: "+ret)
                    continue

                result = upbit.get_order(ret['uuid']) # 구매결과를 담은 변수

                # 지정가
                if result['ord_type'] == 'limit':
                    if int(float(result['remaining_volume'])) != 0 : # 하나도 구매하지 못한 경우
                        print("구매취소")
                        ret = upbit.cancel_order(ret['uuid'])
                    else: # 일부 또는 전체 구매 성공
                        print("구매성공(지정가)")
                        #구매와 동시에 1% 지정가 주문 걸어두기
                        limit_order = upbit.sell_limit_order(result['market'],sell_price(float(result['price'])*1.01,float(result['price']),1.01),result['volume'])
                # 시장가
                else: #시장가는 반드시 구매가 성공하기 때문에 ifelse로 체크할 필요 없음
                    print("구매성공(시장가)")
                    limit_order = upbit.sell_limit_order(result['market'],sell_price(float(result['trades'][0]['price'])*1.01,float(result['trades'][0]['price']),1.01),result['executed_volume'])

        await asyncio.sleep(10)
        
        if life[-1] < life[-2] < life[-3] <life[-4]: # 3번연속 거래에 실패하면 더 이상 당일은 거래하지 않음     
            a = asset()
            print("You Lose Today\'s Trade. Your Balance is ",a)                 
            test_token = True
        
        print("buy loop is ok",datetime.datetime.now(),life,"현재는 "+token_type+" 입니다")
        


def sell_process(revenue=1.01):
    global created_at
    global life
    global q
    today = datetime.datetime.now() - datetime.timedelta(hours=9)     
    yr = today.year
    mth = today.month
    dy = today.day
    file_name = str(yr)+str("-")+str(mth)+str("-")+str(dy)       
    
    # 9시에 life reset
    if today.hour == 0 and today.minute == 0:
        life = [0,0,0,0]
    

    try: # 새롭게 limit_order가 들어온 경우, limit_order가 없을 수 있기 대문에 try-catch
        # check_list에도 없고 done_list에도 없다 -> 방금 막 구매한 종목이구나 -> check_list에 넣자 // 왜 구매시점에 안넣고 지금 넣냐 -> 프로그램이 종료되었다 다시 실행할 때를 대비        
        if limit_order['uuid'] not in check_list and limit_order['uuid'] not in done_list:
            check_list.append(limit_order['uuid'])
    except:
        pass
            
    # 체크리스트 확인
    for x in check_list:
        # check_list의 종목 중 팔렸는데(state == done) 아직 done_list에 들어가있지 않으면
        if upbit.get_order(x)['state'] == 'done' and x not in done_list: 
            check_list.remove(x) # 체크리스트에서 제거
            done_list.append(x) # 완료리스트에 추가
            
            buy_time = datetime.datetime.strptime(upbit.get_order(x)['created_at'].replace('T',' ').replace('+09:00','').replace('\n','')+'.00000','%Y-%m-%d %H:%M:%S.%f')                    

            if 1225<=buy_time.hour*60+buy_time.minute<=1250:                                    
                life.append(life[-1]+1)
            
            f= open(f'C:/Users/82104/DEsktop/거래결과/{file_name}.txt','a')
            data = f"\n{today+datetime.timedelta(hours=9)} - 익절 - "+str(upbit.get_order(x))

            f.write(data)
            f.close()
 
    
    current_price = pyupbit.get_current_price('KRW-'+i['currency']) # 현재가격

    # 익절
    if (float(i['avg_buy_price'])*1.01+one_tick(float(i['avg_buy_price'])) <= current_price): #1.01+1틱을 설정한 이유: 보수적인 구매전략
        ret = upbit.sell_market_order('KRW-'+i['currency'],i['balance'])
        if 'error' in ret.keys():
            print(ret)
            pass
        else:
            try:
                buy_time = datetime.datetime.strptime(upbit.get_order(x)['created_at'].replace('T',' ').replace('+09:00','').replace('\n','')+'.00000','%Y-%m-%d %H:%M:%S.%f')                    
                if 1225<=buy_time.hour*60+buy_time.minute<=1250:                                    
                    life.append(life[-1]+1)
            except:
                pass
            f= open(f'C:/Users/82104/DEsktop/거래결과/{file_name}.txt','a')
            data = f"\n{today+datetime.timedelta(hours=9)} - 익절 - "+str(upbit.get_order(ret['uuid']))
                       
            f.write(data)
            f.close()
       
        
    # 손절
    if (current_price <= float(i['avg_buy_price'])*0.99+one_tick(float(i['avg_buy_price']))):    
        # 예약주문 있으면 취소
        try:
            ret = upbit.get_order("KRW-"+i['currency'])
            created_at = ret[0]['created_at']
            if ret:
                upbit.cancel_order(ret[0]['uuid']) # 이전주문 취소
                check_list.remove(ret[0]['uuid'])
                done_list.append(ret[0]['uuid'])                    
        except:
            pass
        
        ret = upbit.sell_market_order('KRW-'+i['currency'],i['balance']) # 시장가로 판매            
        
        if 'error' in ret.keys():
            print(ret)
            pass
        else:            
            # 실전거래시간에 구매한 종목을 손절했다면 life 감소
            buy_time = datetime.datetime.strptime(upbit.get_order(ret['uuid'])['created_at'].replace('T',' ').replace('+09:00','').replace('\n','')+'.00000','%Y-%m-%d %H:%M:%S.%f')                
            if 1225<=buy_time.hour*60+buy_time.minute<=1250:                                    
                life.append(life[-1]-1)
            f= open(f'C:/Users/82104/DEsktop/거래결과/{file_name}.txt','a')         
            data = f"\n{today+datetime.timedelta(hours=9)} - 손절 - "+str(upbit.get_order(ret['uuid']))
            
            f.write(data)
            f.close()
    


async def sell():
    global token_type
    while True:
        if len(upbit.get_balances()) > 2: # 판매할 종목이 존재할 때만 실행
            sell_process()        
        await asyncio.sleep(2)
        
        print("sell loop is ok",datetime.datetime.now(),life,"현재는 "+token_type+" 입니다")



# 비동기
async def main():
    print("오늘의 거래를 시작하겠습니다.")
    await asyncio.gather(
        buy(),
        sell(),
        )

asyncio.run(main())

