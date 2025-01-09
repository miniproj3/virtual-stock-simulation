from flask import Blueprint, render_template, session, jsonify, request
from confluent_kafka import Producer
from kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import yfinance as yf
import logging
import json

# Blueprint 설정
stock_kr = Blueprint('stock_kr', __name__)

# Kafka Producer 설정
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 글로벌 변수
stock_data_cache = []  # 캐싱된 주식 데이터

# 초기화 함수
def initialize_stock_data():
    global stock_data_cache
    try:
        stock_data_cache = fetch_kr_stock_data()
        logging.info(f"Stock data initialized: {len(stock_data_cache)} entries loaded.")
        if not stock_data_cache:
            logging.warning("Stock data cache is empty after initialization")
    except Exception as e:
        logging.error(f"Error initializing stock data: {str(e)}")

@stock_kr.route('/send_stock_data', methods=['POST'])
def send_stock_data():
    """Kafka로 주식 데이터를 전송하는 엔드포인트"""
    try:
        for stock in stock_data_cache:
            producer.produce(KAFKA_TOPIC, value=json.dumps(stock))
            logging.info(f"Sent stock data to Kafka: {stock}")
        producer.flush()
        logging.info("Kafka flush successful")
        return {"status": "success", "message": "Stock data sent to Kafka"}
    except Exception as e:
        logging.error(f"Error sending stock data to Kafka: {str(e)}")
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
        logging.info(f"Rendering stock_kr.html for user: {user}")
        return render_template('stock_kr.html', user=user)
    else:
        logging.error("User not found in session")
        return "User not found", 404

@stock_kr.route('/get_stock_data', methods=['GET'])
def fetch_stock_data():
    """캐싱된 주식 데이터를 반환"""
    try:
        logging.info(f"Returning stock data cache: {len(stock_data_cache)} entries")
        return jsonify(stock_data_cache)
    except Exception as e:
        logging.error(f"Error fetching stock data: {str(e)}")
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
                logging.warning(f"No valid data for {symbol}")
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")

    logging.info(f"Final stock data: {stock_data[:5]}...")  # 첫 5개만 로깅
    return stock_data

def setup():
    logging.info("Initializing stock data on app startup")
    initialize_stock_data()

# Flask 앱 시작 시 초기화
stock_kr.before_request(setup)
