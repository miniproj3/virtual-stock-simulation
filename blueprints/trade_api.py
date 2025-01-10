from flask import Blueprint, request, jsonify, render_template, current_app
from db import db, User, Stock, Portfolio, Order
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import threading
import time

trade_api = Blueprint('trade_api', __name__)

@trade_api.route('/trade', methods=['GET'])
def trade_page():
    """렌더링 trade.html"""
    return render_template('trade.html')

# 주문 처리 함수
def process_orders(app):
    """주문을 처리하는 백그라운드 작업 (app_context 사용하지 않음)"""
    while True:
        try:
            print("[DEBUG] Starting order processing...")
            # db.session은 Flask-SQLAlchemy에서 제공되는 세션이므로, 직접 app과 연결된 db를 사용
            with app.app_context():
                pending_orders = Order.query.filter_by(status='PENDING').all()
                print(f"[DEBUG] Found {len(pending_orders)} pending orders.")

                for order in pending_orders:
                    stock = Stock.query.get(order.stock_id)
                    
                    if stock is None:
                        print(f"[WARNING] Stock ID {order.stock_id} not found for Order ID {order.id}.")
                        continue

                    # 디버깅: 주문 및 주식 정보 출력
                    print(f"[DEBUG] Processing Order ID: {order.id}, Type: {order.order_type}, "
                          f"Target Price: {order.target_price}, Stock Symbol: {stock.stock_symbol}, "
                          f"Current Price: {stock.current_price}")

                    # 매수 조건 확인
                    if order.order_type == 'BUY' and stock.current_price <= order.target_price:
                        portfolio = Portfolio.query.filter_by(user_id=order.user_id, stock_id=order.stock_id).first()
                        print(f"[INFO] Order ID {order.id} matches BUY condition.")

                        # 포트폴리오 업데이트
                        total_cost = stock.current_price * order.quantity
                        if not portfolio:
                            portfolio = Portfolio(user_id=order.user_id, stock_id=order.stock_id,
                                                  stock_amount=order.quantity, total_value=total_cost)
                            db.session.add(portfolio)
                        else:
                            portfolio.stock_amount += order.quantity
                            portfolio.total_value += total_cost

                        # 주문 상태 업데이트
                        order.status = 'COMPLETED'
                        order.completed_at = datetime.utcnow()
                        print(f"[INFO] Order ID {order.id} marked as COMPLETED (BUY).")

                    # 매도 조건 확인
                    elif order.order_type == 'SELL' and stock.current_price >= order.target_price:
                        portfolio = Portfolio.query.filter_by(user_id=order.user_id, stock_id=order.stock_id).first()
                        if portfolio:
                            print(f"[INFO] Order ID {order.id} matches SELL condition.")
                        else:
                            print(f"[WARNING] No portfolio found for Order ID {order.id}.")

                        # 포트폴리오 업데이트 (매도 가능한 경우)
                        if portfolio and portfolio.stock_amount >= order.quantity:
                            total_revenue = stock.current_price * order.quantity
                            portfolio.stock_amount -= order.quantity
                            portfolio.total_value -= total_revenue
                            if portfolio.stock_amount == 0:
                                db.session.delete(portfolio)

                            # 주문 상태 업데이트
                            order.status = 'COMPLETED'
                            order.completed_at = datetime.utcnow()
                            print(f"[INFO] Order ID {order.id} marked as COMPLETED (SELL).")

                db.session.commit()
                print("[DEBUG] Order processing completed successfully.")

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"[ERROR] Error processing orders: {e}")

        time.sleep(5)  # 5초마다 주문 상태를 확인

def start_order_processing_thread(app):
    """주문 처리 백그라운드 스레드 시작"""
    thread = threading.Thread(target=process_orders, args=(app,), daemon=True)
    thread.start()

def register_process_order_thread(app):
    """Flask 애플리케이션 시작 시 주문 처리 스레드 등록"""
    with app.app_context():
        start_order_processing_thread()

# 주문 생성 API
@trade_api.route('/order', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get('user_id')
    stock_symbol = data.get('stock_symbol')
    order_type = data.get('order_type')  # 'BUY' 또는 'SELL'
    target_price = data.get('target_price')
    quantity = data.get('quantity')

    try:
        # 유효성 검사
        user = User.query.get(user_id)
        stock = Stock.query.filter_by(stock_symbol=stock_symbol).first()
        if not user or not stock:
            return jsonify({"error": "Invalid user or stock"}), 400

        # 주문 생성
        new_order = Order(
            user_id=user_id,
            stock_id=stock.id,
            order_type=order_type,
            target_price=target_price,
            quantity=quantity,
        )
        db.session.add(new_order)
        db.session.commit()
        print(f"[INFO] New order created: ID {new_order.id}, Type {order_type}, Target Price {target_price}, Quantity {quantity}")

        return jsonify({"message": "Order placed successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"[ERROR] Error placing order: {e}")
        return jsonify({"error": str(e)}), 500

# 주문 목록 조회 API
@trade_api.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id', type=int)
    orders = Order.query.filter_by(user_id=user_id).all()

    order_list = [
        {
            "id": order.id,
            "stock_symbol": order.stock.stock_symbol,
            "order_type": order.order_type,
            "target_price": order.target_price,
            "quantity": order.quantity,
            "status": order.status,
            "created_at": order.created_at,
            "completed_at": order.completed_at,
        }
        for order in orders
    ]
    print(f"[INFO] Retrieved orders for User ID {user_id}: {len(order_list)} orders found.")
    return jsonify(order_list), 200