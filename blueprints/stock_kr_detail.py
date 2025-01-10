from flask import Blueprint, render_template, request, jsonify, Response, session
import json
from confluent_kafka import Consumer, KafkaException, KafkaError  # confluent_kafka 사용
from kafka.kafka_producer import get_producer  # 수정된 부분
from kafka.kafka_config import KAFKA_BROKER, KAFKA_STOCK_KR_DETAIL_TOPIC  # 수정된 부분
from db import db, User, Stock, StockTransaction
from datetime import datetime

# Kafka Producer 가져오기
producer = get_producer()

stock_kr_detail = Blueprint('stock_kr_detail', __name__)

@stock_kr_detail.route('/stock_detail')
def stock_detail():
    symbol = request.args.get('symbol')
    print(f'Received symbol: {symbol}')
    if not symbol:
        return "Invalid stock symbol", 400
    stock = Stock.query.filter_by(stock_symbol=symbol).first()
    if stock:
        return render_template('stock_kr_detail.html', stock=stock)
    else:
        return "Stock not found", 404

@stock_kr_detail.route('/stream')
def stream():
    def generate():
        consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'stock_detail_consumer_group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe([KAFKA_STOCK_KR_DETAIL_TOPIC])
        
        try:
            while True:
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise KafkaException(msg.error())

                yield f'data:{json.dumps(msg.value().decode("utf-8"))}\n\n'

        except Exception as e:
            print(f"Error in Kafka Consumer: {str(e)}")
        finally:
            consumer.close()

    return Response(generate(), mimetype='text/event-stream')

@stock_kr_detail.route('/buy', methods=['POST'])
def buy_stock():
    data = request.json
    user = User.query.filter_by(username=session['username']).first()
    stock = Stock.query.filter_by(stock_symbol=data['symbol']).first()
    
    if user and stock:
        amount = data['amount']
        total_cost = stock.current_price * amount
        if user.seed_krw >= total_cost:
            user.seed_krw -= total_cost
            transaction = StockTransaction(
                user_id=user.id,
                stock_id=stock.id,
                transaction_type='BUY',
                amount=amount,
                price_per_unit=stock.current_price,
                total_value=total_cost,
                transaction_date=datetime.now()
            )
            db.session.add(transaction)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Stock bought successfully'})
        else:
            return jsonify({'success': False, 'message': 'Insufficient funds'})
    return jsonify({'success': False, 'message': 'Invalid user or stock'})

@stock_kr_detail.route('/sell', methods=['POST'])
def sell_stock():
    data = request.json
    user = User.query.filter_by(username=session['username']).first()
    stock = Stock.query.filter_by(stock_symbol=data['symbol']).first()

    if user and stock:
        amount = data['amount']
        transaction = StockTransaction(
            user_id=user.id,
            stock_id=stock.id,
            transaction_type='SELL',
            amount=amount,
            price_per_unit=stock.current_price,
            total_value=stock.current_price * amount,
            transaction_date=datetime.now()
        )
        db.session.add(transaction)
        user.seed_krw += stock.current_price * amount
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock sold successfully'})
    return jsonify({'success': False, 'message': 'Invalid user or stock'})
