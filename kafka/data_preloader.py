import yfinance as yf
import logging
import json
import redis

# Redis 설정
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 주식 심볼 리스트
STOCK_SYMBOLS = [
    "005930.KS", "000660.KS", "035420.KS", "207940.KS", "051910.KS",
    "005380.KS", "068270.KS", "028260.KS", "096770.KS", "035720.KS",
    "105560.KS", "000270.KS", "006400.KS", "017670.KS", "012330.KS",
    "003490.KS", "090430.KS", "066570.KS", "018260.KS", "034730.KS"
]

def fetch_kr_stock_data():
    stock_data = []

    for symbol in STOCK_SYMBOLS:
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

    try:
        redis_client.set('kr_stock_data', json.dumps(stock_data))
        logging.info("Stock data loaded into Redis successfully")
    except redis.ConnectionError as e:
        logging.error(f"Error connecting to Redis: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_kr_stock_data()
