from flask import Blueprint, request, render_template, jsonify
import yfinance as yf

stock_kr_detail = Blueprint('stock_kr_detail', __name__)

@stock_kr_detail.route('/stock_detail/')
def stock_detail():
    return render_template('stock_kr_detail.html')

@stock_kr_detail.route("/api/get_stock_detail", methods=["GET"])
def get_stock_detail():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"success": False, "message": "Symbol value is missing."})

    try:
        stock_data = yf.Ticker(symbol)
        history = stock_data.history(period="1d", interval="1m")
        
        if history.empty:
            return jsonify({"success": False, "message": "Stock data not found."})

        timestamps = [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in history.index]
        prices = history["Close"].tolist()
        volumes = history["Volume"].tolist()  # 거래량 추가

        return jsonify({
            "success": True,
            "stock": {
                "symbol": symbol,
                "name": stock_data.info.get("shortName", "Unknown"),
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