from flask import Flask, Blueprint, request, jsonify, render_template

app = Flask(__name__)

# Trade API Blueprint
trade_api = Blueprint('trade_api', __name__)

# 하드코딩된 데이터
mock_stocks = [
    {"id": 1, "stock_symbol": "NAVER", "stock_name": "네이버", "current_price": 150000.0},
    {"id": 2, "stock_symbol": "삼성전자", "stock_name": "삼성전자", "current_price": 80000.0},
]

mock_portfolio = [
    {"user_id": 1, "stock_id": 1, "stock_amount": 5, "total_value": 750000.0},  # Naver 5주
]

mock_transactions = []  # 거래 기록을 저장


@trade_api.route('/buy', methods=['POST'])
def buy_stock():
    data = request.json
    stock_symbol = data.get('stock_symbol')
    amount = data.get('amount')

    try:
        stock = next((s for s in mock_stocks if s["stock_symbol"] == stock_symbol), None)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        total_cost = stock["current_price"] * amount
        mock_transactions.append({
            "user_id": 1,
            "stock_id": stock["id"],
            "transaction_type": "BUY",
            "amount": amount,
            "price_per_unit": stock["current_price"],
            "total_value": total_cost,
        })

        portfolio = next((p for p in mock_portfolio if p["user_id"] == 1 and p["stock_id"] == stock["id"]), None)
        if portfolio:
            portfolio["stock_amount"] += amount
            portfolio["total_value"] += total_cost
        else:
            mock_portfolio.append({
                "user_id": 1,
                "stock_id": stock["id"],
                "stock_amount": amount,
                "total_value": total_cost,
            })

        return jsonify({"message": "Stock purchase successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trade_api.route('/sell', methods=['POST'])
def sell_stock():
    data = request.json
    stock_symbol = data.get('stock_symbol')
    amount = data.get('amount')

    try:
        stock = next((s for s in mock_stocks if s["stock_symbol"] == stock_symbol), None)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        portfolio = next((p for p in mock_portfolio if p["user_id"] == 1 and p["stock_id"] == stock["id"]), None)
        if not portfolio or portfolio["stock_amount"] < amount:
            return jsonify({"error": "Insufficient stocks to sell"}), 400

        total_revenue = stock["current_price"] * amount
        mock_transactions.append({
            "user_id": 1,
            "stock_id": stock["id"],
            "transaction_type": "SELL",
            "amount": amount,
            "price_per_unit": stock["current_price"],
            "total_value": total_revenue,
        })

        portfolio["stock_amount"] -= amount
        portfolio["total_value"] -= total_revenue
        if portfolio["stock_amount"] == 0:
            mock_portfolio.remove(portfolio)

        return jsonify({"message": "Stock sale successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trade_api.route('/portfolio', methods=['GET'])
def get_portfolio():
    try:
        user_id = request.args.get('user_id', default=1, type=int)
        user_portfolio = [
            {
                "stock_name": next((s["stock_name"] for s in mock_stocks if s["id"] == p["stock_id"]), "Unknown"),
                "stock_symbol": next((s["stock_symbol"] for s in mock_stocks if s["id"] == p["stock_id"]), "Unknown"),
                "stock_amount": p["stock_amount"],
                "total_value": p["total_value"]
            }
            for p in mock_portfolio if p["user_id"] == user_id
        ]

        return jsonify({"portfolio": user_portfolio}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trade_api.route('/stocks', methods=['GET'])
def get_stocks():
    return jsonify(mock_stocks), 200


app.register_blueprint(trade_api, url_prefix='/api')