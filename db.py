from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    seed_krw = db.Column(db.Float, default=1000000.0)  # KRW 초기 금액
    seed_usd = db.Column(db.Float, default=0.0)        # USD 초기 금액

    # 관계 설정
    stocks = db.relationship('StockPortfolio', backref='owner', lazy=True)

class StockPortfolio(db.Model):
    __tablename__ = 'stock_portfolio'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)  # 주식 이름
    quantity = db.Column(db.Integer, nullable=False)        # 보유 수량
    average_price = db.Column(db.Float, nullable=False)     # 평균 매수 단가
    current_price = db.Column(db.Float, nullable=True)      # 현재 가격 (API로 업데이트)
    profit_rate = db.Column(db.Float, nullable=True)        # 수익률
