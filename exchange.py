import requests
from flask import *
from db import *
from datetime import *

exchange = Blueprint('exchange', __name__)

# API URL과 사용자 API 키
API_KEY = "2b2b881178db5167b9642f2b"  # 발급받은 API 키
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"  # USD를 기준으로

# 캐시 변수
cached_exchange_rate = None
last_fetch_time = None

def get_exchange_rate():
    global cached_exchange_rate, last_fetch_time
    now = datetime.now()
    next_full_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    # 캐시된 데이터가 있는지 확인, 마지막 가져온 시간이 다음 정각보다 이전인지 확인
    if cached_exchange_rate and last_fetch_time and last_fetch_time >= next_full_hour - timedelta(hours=1):
        return cached_exchange_rate

    try:
        response = requests.get(API_URL)
        data = response.json()
        print(data)  # API 응답 출력
        if data.get('result') == 'success':
            # USD to KRW 환율 반환, 정수로 변환
            cached_exchange_rate = int(data['conversion_rates']['KRW'])
            last_fetch_time = now
            return cached_exchange_rate
        else:
            print(f"환율 API 오류: {data.get('error-type', '알 수 없는 오류')}")
            return None
    except requests.RequestException as e:
        print(f"환율 데이터를 가져오는 중 오류 발생: {e}")
        return None

@exchange.route('/', methods=['GET', 'POST'])
def handle_exchange():
    # 임시로 testuser로 가정
    user = User.query.filter_by(username="testuser").first()

    # 실시간 환율 가져오기
    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        exchange_rate = 1450  # API 실패 시 기본 환율

    message = ""
    if request.method == 'POST':
        currency_pair = request.form.get('currency_pair')
        amount = float(request.form.get('amount', 0))

        if currency_pair == 'KRW_to_USD':  # 원화를 달러로 환전
            if user.seed_krw >= amount:
                exchanged_amount = round(amount / exchange_rate)
                user.seed_krw -= amount
                user.seed_usd += exchanged_amount
                message = f"{amount} KRW를 {exchanged_amount} USD로 환전했습니다!"
            else:
                message = "잔액이 부족합니다!"
        elif currency_pair == 'USD_to_KRW':  # 달러를 원화로 환전
            if user.seed_usd >= amount:
                exchanged_amount = round(amount * exchange_rate)
                user.seed_usd -= amount
                user.seed_krw += exchanged_amount
                message = f"{amount} USD를 {exchanged_amount} KRW로 환전했습니다!"
            else:
                message = "잔액이 부족합니다!"
        else:
            message = "올바른 환전 통화를 선택해주세요."

        db.session.commit()  # 변경사항 저장
        return render_template('exchange.html', user=user, exchange_rate=exchange_rate, message=message)

    return render_template('exchange.html', user=user, exchange_rate=exchange_rate)

@exchange.route('/get_balance', methods=['POST'])
def get_balance():
    user = User.query.filter_by(username="testuser").first()  # 테스트 사용자로 가정
    if not user:
        return jsonify({'error': '사용자가 존재하지 않습니다!'}), 404

    try:
        currency_pair = request.json.get('currency_pair')
        print(f"Received currency pair: {currency_pair}")  # 통화쌍 출력
        if currency_pair == 'KRW_to_USD':
            balance = user.seed_krw
        elif currency_pair == 'USD_to_KRW':
            balance = user.seed_usd
        else:
            balance = 0

        print(f"Returning balance: {balance}")  # 잔액 출력
        return jsonify({'balance': balance})
    except Exception as e:
        print(f"잔액 정보를 가져오는 중 오류 발생: {e}")  # 예외 로그 출력
        return jsonify({'error': f"잔액 정보를 가져오는 중 오류 발생: {e}"}), 500