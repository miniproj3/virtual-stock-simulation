from flask import Blueprint, render_template, session, jsonify, request
from confluent_kafka import Producer
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import yfinance as yf
import logging
import json
import redis
import threading
import time

# Blueprint 설정
stock_kr = Blueprint('stock_kr', __name__)

# Kafka Producer 설정
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

# 기존 로깅 핸들러 제거
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.handlers.clear()

# 로깅 설정
logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

# Redis 설정
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 글로벌 변수 초기화
stock_data_cache = []

@stock_kr.route('/send_stock_data', methods=['POST'])
def send_stock_data():
    """Kafka로 주식 데이터를 전송하는 엔드포인트"""
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
    """사용자 세션 기반으로 주식 데이터를 표시"""
    if 'username' in session:
        user = {
            'username': session['username'],
            'seed_krw': session.get('seed_krw', 0),
            'seed_usd': session.get('seed_usd', 0)
        }
        logger.info(f"Rendering stock_kr.html for user: {user['username']}")
        return render_template('stock_kr.html', user=user)
    else:
        logger.error("User not found in session")
        return "User not found", 404

@stock_kr.route('/get_stock_data', methods=['GET'])
def fetch_stock_data():
    """캐싱된 주식 데이터를 반환"""
    try:
        stock_data_cache = json.loads(redis_client.get('kr_stock_data'))
        logger.debug(f"Returning stock data cache: {len(stock_data_cache)} entries")
        
        # 데이터 중 첫 번째 주식 정보만 로그로 기록
        if stock_data_cache:
            logger.debug(f"First stock data: {stock_data_cache[0]}")
            
        return jsonify(stock_data_cache)
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


def fetch_kr_stock_data():
    """yfinance를 통해 한국 주식 데이터를 가져오는 함수"""
    stock_data = []

    # 한국 주식 대표 상위 20개 종목 리스트
    stock_symbols = [
        "005930.KS", "000660.KS", "035420.KS", "207940.KS", "051910.KS",
        "005380.KS", "068270.KS", "028260.KS", "096770.KS", "035720.KS",
        "105560.KS", "000270.KS", "006400.KS", "017670.KS", "012330.KS",
        "003490.KS", "090430.KS", "066570.KS", "018260.KS", "034730.KS"
    ]

    for symbol in stock_symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            stock_name = info.get("shortName", "N/A")
            current_price = info.get("currentPrice", None)
            previous_close = info.get("previousClose", None)

            if current_price and previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                stock_data.append({
                    'shortName': stock_name,
                    'regularMarketPrice': round(current_price),
                    'regularMarketChange': round(change),
                    'regularMarketChangePercent': f"{change_percent:.2f} %"
                })
            else:
                logger.warning(f"No valid data for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")

    logger.debug(f"Final stock data: {stock_data[0]}...")  # 첫 번째 항목만 로깅
    return stock_data

def initialize_stock_data():
    global stock_data_cache
    try:
        stock_data_cache = fetch_kr_stock_data()
        if stock_data_cache:
            redis_client.set('kr_stock_data', json.dumps(stock_data_cache))
            logger.info("Stock data cached in Redis")
    except Exception as e:
        logger.error(f"Error initializing stock data: {str(e)}")

def update_stock_data():
    """5초마다 주식 데이터를 업데이트하는 함수"""
    global stock_data_cache
    while True:
        new_data = fetch_kr_stock_data()
        if new_data != stock_data_cache:  # 데이터가 변경된 경우에만 업데이트
            stock_data_cache = new_data
            redis_client.set('kr_stock_data', json.dumps(stock_data_cache))
            logger.info("Stock data updated and cached in Redis")
        else:
            logger.info("No changes in stock data")
        time.sleep(5)

# 별도의 스레드에서 주기적으로 데이터 업데이트
update_thread = threading.Thread(target=update_stock_data, daemon=True)
update_thread.start()
