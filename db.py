import pymysql, os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from config import config

pymysql.install_as_MySQLdb()

db = SQLAlchemy()

def get_stock_by_symbol(stock_symbol):
    return Stock.query.filter_by(symbol=stock_symbol).first()

def init_app(app):
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
    db_name = config[app.config['ENV']].DB_NAME
    db_uri = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[0]

    engine = create_engine(db_uri)
    with engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

    complete_db_uri = f"{db_uri}/{db_name}"
    engine = create_engine(complete_db_uri)
    app.config['SQLALCHEMY_DATABASE_URI'] = complete_db_uri
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kakao_id = db.Column(db.String(20), unique=True, nullable=True)  # kakao_id 추가
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=True, unique=True)
    seed_krw = db.Column(db.Float, default=0.0)
    seed_usd = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime)
    last_seed_update = db.Column(db.DateTime, default=None)

    portfolios = db.relationship('Portfolio', backref='owner', lazy=True)
    orders = db.relationship('Order', backref='user_orders', lazy=True)
    exchanges = db.relationship('Exchange', backref='owner', lazy=True)


class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(50), nullable=False, unique=True)
    stock_name = db.Column(db.String(255), nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    market = db.Column(db.Enum('DOMESTIC', 'INTERNATIONAL', name='market_enum'), nullable=False)

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    stock_amount = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    initial_investment = db.Column(db.Float, default=0.0)  # 초기 투자 금액 추가

    stock = db.relationship('Stock', backref='portfolios')
    user = db.relationship('User', backref='user_portfolios')  # backref 이름을 'user_portfolios'로 변경

    def calculate_profit_rate(self):
        """수익률을 계산하는 메서드"""
        if self.initial_investment > 0:
            current_value = self.stock_amount * self.stock.current_price
            profit_rate = (current_value - self.initial_investment) / self.initial_investment * 100
            return profit_rate
        return 0


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    order_type = db.Column(db.Enum('BUY', 'SELL', name='order_type_enum'), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('PENDING', 'COMPLETED', name='order_status_enum'), default='PENDING')
    created_at = db.Column(db.DateTime, default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('user-orders', lazy=True))
    stock = db.relationship('Stock', backref=db.backref('orders', lazy=True))

class Exchange(db.Model):
    __tablename__ = 'exchanges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_currency = db.Column(db.String(10), nullable=False)
    to_currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    exchange_date = db.Column(db.DateTime, default=db.func.now())