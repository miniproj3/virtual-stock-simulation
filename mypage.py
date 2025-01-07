from flask import *
from db import *

mypage = Blueprint('mypage', __name__)

@mypage.route('/')
def mypage_home():
    # TestUser로 가정
    user = User.query.filter_by(username="testuser").first()

    if not user:
        return "사용자를 찾을 수 없습니다.", 404

    # 사용자의 주식 포트폴리오 정보
    stock_portfolio = StockPortfolio.query.filter_by(user_id=user.id).all()
    total_profit_rate = 0
    if stock_portfolio:
        total_profit_rate = sum([stock.profit_rate for stock in stock_portfolio]) / len(stock_portfolio)

    return render_template(
        'mypage.html',
        user=user,
        stock_portfolio=stock_portfolio,
        avg_profit_rate=round(total_profit_rate, 2)
    )
