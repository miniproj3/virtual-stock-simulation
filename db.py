import pymysql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.exc import OperationalError

pymysql.install_as_MySQLdb()

db = SQLAlchemy()

def init_app(app):
    # MySQL RDS 설정은 config.py에서 관리
    app.config['SQLALCHEMY_POOL_SIZE'] = 10  # 연결 풀 크기 설정
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30  # 풀 타임아웃 설정
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # 연결 재사용 시간 설정 (초)
    db.init_app(app)

    # 데이터베이스 존재 여부 확인 및 생성
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[-1]
    with engine.connect() as connection:
        try:
            connection.execute(text(f"USE {db_name}"))
        except OperationalError:
            connection.execute(text(f"CREATE DATABASE {db_name}"))
            connection.execute(text(f"USE {db_name}"))

# 사용자
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    seed_krw = db.Column(db.Float, default=1000000.0)
    seed_usd = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime)

    # 관계 설정
    portfolios = db.relationship('Portfolio', backref='owner', lazy=True)
    transactions = db.relationship('StockTransaction', backref='owner', lazy=True)
    exchanges = db.relationship('Exchange', backref='owner', lazy=True)

# # 시드머니 기록
# class SeedMoney(db.Model):
#     __tablename__ = 'seed_money'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     seed_krw = db.Column(db.Float, default=0.0)
#     seed_usd = db.Column(db.Float, default=0.0)
#     granted_date = db.Column(db.DateTime, default=db.func.now())
#     reset_date = db.Column(db.DateTime, nullable=True)
#     status = db.Column(db.Enum('GRANTED', 'RESET', name='status_enum'), nullable=False)

# 주식 정보
class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(50), nullable=False, unique=True)
    stock_name = db.Column(db.String(255), nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    market = db.Column(db.Enum('DOMESTIC', 'INTERNATIONAL', name='market_enum'), nullable=False)

# 포트폴리오
class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    stock_amount = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)

# 거래 기록
class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    transaction_type = db.Column(db.Enum('BUY', 'SELL', name='transaction_type_enum'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=db.func.now())

# 환전 기록
class Exchange(db.Model):
    __tablename__ = 'exchanges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_currency = db.Column(db.String(10), nullable=False)
    to_currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    exchange_date = db.Column(db.DateTime, default=db.func.now())
