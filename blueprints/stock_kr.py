from flask import Blueprint, render_template, session, jsonify, redirect, url_for  # redirect, url_for 추가
from kafka.kafka_producer import get_producer
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import yfinance as yf
import logging
import json
import redis
from db import *

# Blueprint 설정
stock_kr = Blueprint('stock_kr', __name__)

producer = get_producer()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

stock_data_cache = []

@stock_kr.route('/send_stock_data', methods=['POST'])
def send_stock_data():
    try:
        stock_data_cache = json.loads(redis_client.get('kr_stock_data'))
        for stock in stock_data_cache:
            producer.produce(KAFKA_TOPIC, value=json.dumps(stock))
            logger.info(f"Sent stock data to Kafka: {stock['shortName']}")
        producer.flush()
        logger.info("Kafka flush successful")
        return {"status": "success", "message": "Stock data sent to Kafka"}
    except Exception as e:
        logger.error(f"Error sending stock data to Kafka: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

@stock_kr.route('/')
def show_stock_kr():
    user_info = session.get('user')
    if not user_info:
        logger.error("User not found in session")
        return redirect(url_for('auth.kakaologin'))

    try:
        user_id = user_info['id']
        user = User.query.get(user_id)
        if not user:
            logger.error("User not found in database")
            return "User not found in database", 404

        logger.info(f"Rendering stock_kr.html for user: {user.username}")
        return render_template('stock_kr.html', user=user)
    except Exception as e:
        logger.error(f"Error fetching user from database: {str(e)}")
        return "Error fetching user from database", 500



@stock_kr.route('/get_stock_data', methods=['GET'])
def fetch_stock_data():
    try:
        stock_data_cache = json.loads(redis_client.get('kr_stock_data'))
        if stock_data_cache:
            logger.debug(f"Returning stock data cache: {len(stock_data_cache)} entries")
            return jsonify(stock_data_cache)
        else:
            logger.error("No stock data found in Redis cache")
            return {"status": "error", "message": "No stock data found"}, 500
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        return {"status": "error", "message": str(e)}, 500
