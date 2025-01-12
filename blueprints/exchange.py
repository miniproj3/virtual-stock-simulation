import yfinance as yf
from flask import *
from db import *
from datetime import *

exchange = Blueprint('exchange', __name__)

# 캐시 변수
cached_exchange_rate = None
last_fetch_time = None

def get_exchange_rate():
    global cached_exchange_rate, last_fetch_time
    now = datetime.now()
    next_full_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    if cached_exchange_rate and last_fetch_time and last_fetch_time >= next_full_hour - timedelta(hours=1):
        return cached_exchange_rate
    
    try:
        ticker = yf.Ticker("USDKRW=X")
        exchange_rate = ticker.history(period="1d")['Close'].iloc[-1]
        cached_exchange_rate = round(exchange_rate, 2)
        last_fetch_time = now
        return cached_exchange_rate
    except Exception as e:
        print(f"환율 데이터를 가져오는 중 오류 발생: {e}")
        return None

@exchange.route('/', methods=['GET', 'POST'])
def handle_exchange():
    user_info = session.get('user')
    if not user_info:
        return redirect(url_for('auth.kakaologin'))  # 로그인 페이지로 리디렉트

    user_id = user_info['id']
    user = User.query.get(user_id)
    if not user:
        return "사용자를 찾을 수 없습니다.", 404

    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        exchange_rate = 1450.00  # API 실패 시 기본 환율

    message = ""
    if request.method == 'POST':
        currency_pair = request.form.get('currency_pair')
        amount = float(request.form.get('amount', 0))

        if currency_pair == 'KRW_to_USD':
            if user.seed_krw >= amount:
                exchanged_amount = round(amount / exchange_rate, 2)
                user.seed_krw -= amount
                user.seed_usd += exchanged_amount

                exchange_record = Exchange(
                    user_id=user.id,
                    from_currency='KRW',
                    to_currency='USD',
                    amount=amount,
                    exchange_rate=exchange_rate,
                    total_value=exchanged_amount
                )
                db.session.add(exchange_record)

                message = f"{amount} KRW를 {exchanged_amount} USD로 환전했습니다!"
            else:
                message = "잔액이 부족합니다!"
        elif currency_pair == 'USD_to_KRW':
            if user.seed_usd >= amount:
                exchanged_amount = round(amount * exchange_rate, 2)
                user.seed_usd -= amount
                user.seed_krw += exchanged_amount

                exchange_record = Exchange(
                    user_id=user.id,
                    from_currency='USD',
                    to_currency='KRW',
                    amount=amount,
                    exchange_rate=exchange_rate,
                    total_value=exchanged_amount
                )
                db.session.add(exchange_record)

                message = f"{amount} USD를 {exchanged_amount} KRW로 환전했습니다!"
            else:
                message = "잔액이 부족합니다!"
        else:
            message = "올바른 환전 통화를 선택해주세요."

        db.session.commit()  # 변경사항 저장 및 환전 기록 커밋
        return render_template('exchange.html', user=user, exchange_rate=exchange_rate, message=message)

    return render_template('exchange.html', user=user, exchange_rate=exchange_rate)

@exchange.route('/get_balance', methods=['POST'])
def get_balance():
    user_info = session.get('user')
    if not user_info:
        return jsonify({'error': '사용자가 존재하지 않습니다!'}), 404

    user_id = user_info['id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '사용자가 존재하지 않습니다!'}), 404

    try:
        currency_pair = request.json.get('currency_pair')
        if currency_pair == 'KRW_to_USD':
            balance = user.seed_krw
        elif currency_pair == 'USD_to_KRW':
            balance = user.seed_usd
        else:
            balance = 0
        return jsonify({'balance': balance})
    except Exception as e:
        return jsonify({'error': f"잔액 정보를 가져오는 중 오류 발생: {e}"}), 500
