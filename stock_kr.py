import yfinance as yf
from flask import *
from socketio_instance import socketio
from flask_socketio import emit

stock_kr = Blueprint('stock_kr', __name__)

@stock_kr.route('/')
def get_kr_stock_data():
    stock_data = fetch_kr_stock_data()
    print(stock_data)
    return render_template('main.html', stock_data=stock_data)

def fetch_kr_stock_data():
    symbols = ['005930.KS', '000660.KS', '035420.KS']
    stock_data = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        try:
            stock_info = stock.info
            current_price = stock_info.get('currentPrice', 0)
            previous_close = stock_info.get('regularMarketPreviousClose', 0)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            stock_data.append({
                'shortName': stock_info.get('shortName', 'N/A'),
                'regularMarketPrice': round(current_price),
                'regularMarketChange': round(change),
                'regularMarketChangePercent': f"{change_percent:.2f}"
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    return stock_data

@socketio.on('request_stock_data')
def handle_request_stock_data():
    stock_data = fetch_kr_stock_data()
    emit('stock_data_update', stock_data)