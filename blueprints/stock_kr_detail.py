from flask import Blueprint, request, render_template, jsonify, session
import yfinance as yf
from db import *

stock_kr_detail = Blueprint('stock_kr_detail', __name__)

def get_stock_by_symbol(stock_symbol):
    stock = Stock.query.filter_by(stock_symbol=stock_symbol).first()
    if not stock:
        # 주식 데이터가 없다면 Yahoo Finance에서 데이터를 가져오고 DB에 저장
        stock_data = yf.Ticker(stock_symbol)
        stock_info = stock_data.info
        print(f"[DEBUG] Stock Info: {stock_info}")  # stock_info 확인
        stock = Stock(
            stock_symbol=stock_symbol,
            stock_name=stock_info.get('shortName', 'Unknown'),
            current_price=stock_info.get('regularMarketPrice', 0),  # regular_market_price 값 가져오기
            market='DOMESTIC'  # market 값을 지정 (예시로 DOMESTIC으로 설정)
        )
        db.session.add(stock)
        db.session.commit()
    return stock



@stock_kr_detail.route('/buy_sell_stock', methods=['POST'])
def buy_sell_stock():
    user_info = session.get('user')
    if not user_info:
        print("[DEBUG] User is not authenticated.")
        return jsonify({"error": "User is not authenticated. Please log in."}), 401

    user = User.query.get(user_info['id'])
    if not user:
        print("[DEBUG] User not found.")
        return jsonify({"error": "User not found."}), 404

    # JSON 데이터로부터 값을 추출
    stock_symbol = request.json.get('stock_symbol')
    order_type = request.json.get('order_type')
    try:
        quantity = int(request.json.get('quantity'))
        price = float(request.json.get('target_price'))  # target_price로 수정
    except (TypeError, ValueError) as e:
        print(f"[DEBUG] Received invalid order data: {e}")
        return jsonify({"error": "Invalid order data. Please check the input values."}), 400

    print(f"[DEBUG] stock_symbol: {stock_symbol}")
    print(f"[DEBUG] order_type: {order_type}")
    print(f"[DEBUG] quantity: {quantity}")
    print(f"[DEBUG] price: {price}")

    # Check for None or invalid values
    if stock_symbol is None or order_type is None or quantity <= 0 or price <= 0:
        print("[DEBUG] Missing or invalid order data")
        return jsonify({"error": "Missing or invalid order data."}), 400

    stock = get_stock_by_symbol(stock_symbol)
    if not stock:
        print("[DEBUG] Stock not found.")
        return jsonify({"error": "Stock not found."}), 404

    # 주문 데이터베이스에 추가
    order = Order(
        user_id=user.id,
        stock_id=stock.id,
        order_type=order_type,
        target_price=price,
        quantity=quantity,
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    print("[DEBUG] Order successfully placed.")
    return jsonify({"message": "Order successfully placed."}), 200


@stock_kr_detail.route('/stock_detail/')
def stock_detail():
    user_info = session.get('user')

    if not user_info:
        print("[DEBUG] 세션에 사용자 정보가 없습니다.")
        return render_template('auth.html')  # 로그인 페이지로 리다이렉트

    return render_template('stock_kr_detail.html', user=user_info)


@stock_kr_detail.route("/api/get_stock_detail", methods=["GET"])
def get_stock_detail():
    symbol = request.args.get("symbol")
    user_info = session.get('user')
    
    if not user_info:
        return jsonify({"success": False, "message": "User is not authenticated. Please log in."}), 401

    if not symbol:
        return jsonify({"success": False, "message": "Symbol value is missing."})

    try:
        stock_data = yf.Ticker(symbol)
        history = stock_data.history(period="1d", interval="1m")

        if history.empty:
            return jsonify({"success": False, "message": "Stock data not found."})

        timestamps = [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in history.index]
        prices = history["Close"].tolist()
        volumes = history["Volume"].tolist()

        return jsonify({
            "success": True,
            "user_id": user_info['id'],
            "stock": {
                "symbol": symbol,
                "name": stock_data.info.get("shortName", "Unknown"),  # 여기도 stock_name으로 수정 가능
                "current_price": stock_data.info.get("regularMarketPrice", 0),
            },
            "chartData": {
                "timestamps": timestamps,
                "prices": prices,
                "volumes": volumes
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
