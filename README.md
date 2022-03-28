# 가상화폐 자동거래 시스템

# 주의
이 프로그램은 스스로 사고하고 학습하여 더 나은 구매를 진행하는 시스템이 아닙니다.
<br>
제가 명령한 방식으로 24시간동안 주식을 거래하는 `구매 대행인`과 같은 시스템입니다.

# 코드리뷰
  ### 비동기 방식으로 Sell과 Buy가 진행됩니다.

  * ## Sell
    ```python
     while True:
      if len(balances)>2:
         새롭게 구매된 종목은 check_lst에 넣고
         check_lst의 종목이 팔렸으면 done_lst에 넣는다
         if 현재가격이 -1%로 떨어졌다면:
            바로 시장가 판매
    ```


  * ## Buy
    ```python
     while True: 
      for i in coin_lst #모든 코인이름을 순회하면서
         coin = get_ohlcv() #분봉 데이터를 15개 가져온다
         coin의 BOP,MFI,Sto,RSI를 계산해서 coin의 column으로 추가한 뒤
         if BOP,MFI,Sto,RSI가 모두 특정 조건을 만족하면:
            ret = get_order #구매주문을 넣고
            await asyncio.sleep(15) #15초간 대기한다
            if int(float(result['remaining_volume'])) != 0 : #구매가 진행되지 않았으면
               ret = cancel_order(ret['uuid']) #구매주문을 넣어둔 걸 취소한다
            else:
               limit_order = sell_limit_order #곧바로 1% 예약주문을 걸어둠
    ```   

   * ## Upbit_tools.py
     ### 시스템 거래에 필요한 메서드를 정의해둔 파일 입니다.
     * asset(): 현재 보유 자산을 return 합니다
     * one_tick(price): 가격대별로 한 틱의 가격이 얼마인지 계산합니다
     * market_status(): '전일대비 가격이 상승한 종목의 개수 - 전일대비 가격이 하락한 종목의 개수'를 return 합니다 
     * sell_price(current_price,buy_price,under_k): 현재가격을 기준으로 1%의 수익을 내는 거래가능 가격을 return 합니다
   * ## tools.py
     ### BOP,MFI,Sto,RSI를 코드로 구현한 파일 입니다.

# 아이디어 스캐치
  * ## 주식이 아닌 가상화폐를 선택한 이유 
     * 잘 구현된 API 
     * 큰 변동성

  * ## 분산투자를 진행하지 않은 이유
   * 1%의 수익을 위해 너무 많은 거래가 필요하기 때문입니다
     * 가령 55%의 확률로 1%의 수익을, 나머지 45%의 확률로 -1%의 수익을 가져오는 알고리즘이 있고
     * 위 알고리즘으로 한번 거래할때마다 전체자산의 10%를 사용한다고 가정했을 때
     * 하나의 거래가 성공하면 전체 잔액의 0.1%의 수익을 올리는 것임
     * 1%의 수익과 1%의 손해가 동등하게 상세된다고 가정했을 때(실제로 손해의 힘이 더 큼: 1.01x0.99 = 0.9999) 수익의 개수가 10개 더 많아야 함
     * 그러면 100번의 거래를 해야 (+55-45) 1%의 수익이 달성됨
     * 근데만약 성공률이 51%다? 그러면 500번 거래해야 ((51-49)x5) 1%의 수익이 달성됨


  * ## 지정가로 거래하는 이유
     * 0.33%인 경우 // 존재하지 않지만 0.99%인 경우
     * 시장가 거래는 빠른 대신 한틱 낮게 거래될 가능성이 크다

  * ## -1%의 손해를 설정한 이유
     * 일단 손절이 없는건 말이 안됨
     * 99%의 확률로 x10의 수익을, 나머지 1%의 확률이 x0을 가져온다고 했을 때 무한히 많이 시행하면 결국 내 잔고는 0원이 된다
     * -1%의 기준은 임의로 내가 정한거지만 -2%가 되었을 때에는 너무많은 거래가 필요함

  * ## LIFE의 개념을 도입한 이유
    * 좋은날과 나쁜날이 있다는 가정 때문임 // 데이터로 봤을 때 그런게 

  * ## 데이터를 수집하는 이유
    * 구입시간에 따른 유의미 차이
    * 종목에따른 유의미차이
    * 
  * ## 구매 알고리즘
    * 완벽한 구매방법이 존재할 수 없다는 걸 인지하고 승리할 가능성이 높은 확률싸움에 들어가자.
    * 직접 구매한 데이터를 2차 분석해 이를 가공할 예정
    * rsi가 상승하는 시그널을 보고 사면 괜찮을까?



  * ## Result
### 21년
![1120-1231_25분단위](https://user-images.githubusercontent.com/25142537/151659656-bb496572-08c6-4186-a013-bf660435dc5e.png)

### 1월
![0101-0129_25분단위](https://user-images.githubusercontent.com/25142537/151659658-c31c9607-04ed-43e8-b4a1-fac63c563500.png)

### 2월
![2월 거래결과](https://user-images.githubusercontent.com/25142537/156164472-420a9f59-81ea-4055-a1ec-2ca13c386b88.png)


   * 시간대가 유의미 하다면 뭐 때문에 그런걸까?
     * 사람들의 일정한 루틴에 의해? (ex- 출근할 때 확인한다, 점심시간에 확인한다 등)
     * 세력이 활동하는 시간이다?
     * 내가 모르는 어떠한 인과에 의해?
     * 사실 아무런 관련이 없고 우연의 일치이다?
     * 우선 9시는 확실히 유의미하다고 느낌 (거래 경험을 통해)
     * 취침 전에 주문하는 사람들의 심리다?

* # 추가예정

* 시장이 안좋으면 거래 중지
* ~~특정 종목은 묻어두기~~
* 에러사항 대처
* ~~데이터 저장하는거 충돌~~
* ~~신규거래 검증~~
  * 신규종목은 상장시점에 api거래가 안됨
* rolling sell정리

* 서버에 올리기
* json으로 데이터 형식 변경하기
* db에 연결
  * 몽고디비? mysql? 서버관리는 java로 가능??  
* 안전성 향샹 - 지금 발생하는 에러는 뭐가있고 이건 어떻게 처리할 예정인지
  * it failed connection error에 대해  


* ## 기술적 분석 지표
  * BOP 
    * (종가 - 시가) / (고가 - 저가)
    * 상승세와 하락세를 나타내는 지표
  * RSI 
    * 상대강도지수, 매수세와 매도세를 파악하기 위한 지표
  * MFI
    * RSI 지표를 보조하기 위한 지표
