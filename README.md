## 소개
### 들어가기 전에
해당 프로젝트는 주어진 로직을 처리해 가상화폐를 자동으로 거래하는 시스템을 개발한 내용입니다.
이는 러닝을 통해 더 나은 구매를 진행하는 알고리즘이 아니며, 로직대로 24시간 
가상화폐를 거래하는 구매 대행인과 같음을 알려드립니다.

해당 프로젝트는 upbit api를 통해 제작되었습니다.
*	<a href="https://docs.upbit.com/reference/">업비트 api 공식문서</a>
*	<a href="https://github.com/sharebook-kr/pyupbit">업비트 api 활용 기본</a>


### 목표 
*	51% 이상의 확률로 성공 시 1%의 수익을, 실패 시 1%의 손해를 보는 거래
*	Daily 1% 수익거래

### 거래 방식
*	RSI, BOP, MFI 기술적 분석 지표로 과매도 상태를 판단해 구매를 진행합니다.
	*	RSI
    	*	일정 기간동안의 가격변화 추세를 통해 과매수와 과매도를 판단
    *	BOP
	    *	(종가 - 시가) / (고가 - 저가)
        *	상승세와 하락세를 나타내는 지표
    *	MFI
    	*	RSI에 거래량을 함께 활용한 지표
    
#### 해당 지표를 선정한 이유
*	구현하기 쉬워서 선정했습니다.



## 로직 설명
### 1. 비동기거래
*	buy로직과 sell로직이 비동기처리로 동시에 진행됩니다.
### 2. buy로직
*	모든 종목의 현재가격을 받아옵니다.
*	모든 종목을 반복문으로 순회하면서 구매조건을 만족하는지 검사합니다.
*	구매조건을 만족하면 현재 가격으로 지정가 주문을 넣고 15초간 대기합니다.
    *	구매에 성공했다면 곧바로 현재가격보다 1% 더 높은 가격의 예약 매도주문을 걸어둡니다.
    *	구매에 실패했다면 지정가 주문을 취소합니다.

### 3. Sell로직
*	checklist와 donelist 구매한 종목들이 관리됩니다.
	*	checklist는 주문내역이 담겨 있습니다.
*	판매는 두 가지 방법으로 이뤄집니다.
	*	첫째, 구매 시 걸어두었던 예약 매도주문이 체결된 경우입니다.
    	checklist의 주문내역 status가 done으로 변경된 걸 통해 확인할 수 있습니다. 해당 주문을 checklist에서 제거합니다.
    *	둘째, 가격이 하락해 손절을 실행하는 경우입니다.
    	구매 시 걸어두었던 예약주문을 취소하고 시장가로 해당 종목을 즉시 처분합니다.

### 4. test와 real
데이터 수집 목적의 테스트 거래와 실전 거래로 나뉩니다.

#### 테스트 거래
*	7000원으로 시장가 구매를 진행합니다.

#### 실전 거래
*	계좌 내 모든 예수금으로 지정가 구매를 진행합니다.
*	현재는 8시 25분부터 8시 50분까지만 실전거래로 종목을 거래합니다.
*	추후 24시간 실전거래를 진행할 예정이며, 이때 LIFE를 통해 성적이 좋지 않으면 테스트 거래로 변환됩니다.


### 부가 파일
#### upbit_tools.py 
*	잔액을 구하는 메서드, 금액에 따른 거래단위(틱)를 구하는 메서드, n%의 거래금액을 계산하는 메서드가 구현되어 있습니다.

#### tools.py
*	BOP,MFI,RSI가 구현되어 있습니다.


## 시스템을 만들면서 고민했던 것들

### 주식이 아닌 가상화폐를 선택한 이유
*	upbit의 API가 사용하기 쉽게 잘 되어 있다는 점이 좋았습니다.
*	가상화폐는 24시간 거래가 가능하다는 점이 좋았습니다.
*	시장의 변동성이 커 기술적 분석이 더 유의미하다고 판단했습니다.

### 분산투자를 진행하지 않은 이유
*	목표수익을 얻기까지 너무 많은 거래가 필요합니다.
	*	10%의 분산투자로 51%의 성공률을 달성하면 500번의 거래를 해야 전체 자산의 1% 수익이 발생합니다. 하지만 실제 시스템의 평균 매수 횟수는 일 25.2회로 거래량이 많지 않습니다. 
*	거래에서 부담하는 리스크가 -1%로 고정되어 분산투자로 얻는 효과가 크지 않다고 판단했습니다.




### -1%의 손해를 설정한 이유
*	자산거래에서 손절이 존재하지 않는건 말이 안됩니다.
	*	손절이 없다면 수익을 극대화할 수 없으며, 자산의 유동성이 낮아져 좋은 거래를 할 수 없습니다.
*	하나의 거래에서 목표수익이 1%이기 때문에 손절기준도 작아야 한다고 생각했습니다.
	*	-1%와 -2% 둘 중 하나의 값을 고민했고, -2%의 경우 이를 매꾸기 위해 필요한 거래가 너무 많아 -1%로 설정했습니다.

### LIFE개념을 도입한 이유
*	가상화폐 시장은 모든 종목이 하락세를 보이는 날이 빈번하게 등장합니다.
	*	저는 이러한 상황을 `거래를 하면 안되는 날`로 정의했습니다.
	*	RSI는 지속적인 하락을 매수신호로 인식합니다. 그래서 단기간에 반등하지 않는 하락을 걸러낼 필요가 있다고 생각해 DAY단위로 거래를 멈출 수 있는 LIFE를 도입했습니다.
	

### 데이터를 수집하는 이유
*	거래의 성공확률을 높이기 위해서 입니다.
*	시장에 알려진 기술적 분석 방법 이외에 저만의 거래기법을 발견하기 위해서 데이터를 수집하고 있습니다.


### checklist와 donelist로 종목을 관리하는 이유
*	프로세스가 종료된 뒤 다시 시작할 때 이전 프로세스의 거래를 기억하지 못하는 문제를 해결하기 위해서 입니다.


### 손절시 지정가 판매가 아닌 시장가 판매를 하는 이유
*	위험을 줄이기 위해서 입니다.
*	가격이 급락해서 지정가 판매가 체결되지 못하는 위험을 없애기 위해 손절판매는 확실한 판매가 가능한 시장가 거래를 이용합니다.


## 거래결과

### 21년 거래결과
![1120-1231_25분단위](https://user-images.githubusercontent.com/25142537/151659656-bb496572-08c6-4186-a013-bf660435dc5e.png)

### 1월 거래결과
![0101-0129_25분단위](https://user-images.githubusercontent.com/25142537/151659658-c31c9607-04ed-43e8-b4a1-fac63c563500.png)

### 2월 거래결과
![2월 거래결과](https://user-images.githubusercontent.com/25142537/156164472-420a9f59-81ea-4055-a1ec-2ca13c386b88.png)

### 3월 거래결과
![3월](https://user-images.githubusercontent.com/25142537/161555858-00f82bf5-5a16-4ccf-91da-7888ddb15291.png)



## problems
### Major problem
*	네트워크 연결이 끊기면 시스템도 종료되는 문제가 발생합니다.
	*	시스템이 종료되었을 때 자동으로 실행하는 윈도우 스케줄러를 만들 계획입니다.

### Minor problem
*	5000원 이하의 찌꺼기가 남는 경우 거래되지 않는 문제가 발생합니다.
*	네트워크가 불안정할 때 null값이 들어가는 문제가 발생합니다.
	*	try-catch로 해당 구간을 에러처리하고 다시 진행하고 있습니다.
*	지정가 구매가 일부만 이뤄질 수 있습니다.
	*	나머지 금액으로 다른 종목을 계속 거래하고 있습니다.



## 추가구현(예정)
*	판매로직(가제 - rollingSell)테스트 및 도입.
~~*	DB연동을 통한 데이터 관리.~~

## DB
*	기본 연결에 성공했습니다
*	json형태 그대로 데이터를 저장하도록 변경할 예정입니다
