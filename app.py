from flask import Flask, render_template, session, redirect
from flask_session import Session
from flask_login import *
from db import *
from blueprints.stock_kr import stock_kr
from blueprints.auth import auth
from blueprints.stock_kr_detail import stock_kr_detail
from blueprints.exchange import exchange
from blueprints.mypage import mypage
import threading
from kafka.kafka_consume import consume_stock_data
from confluent_kafka.admin import AdminClient, NewTopic
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import kafka.data_preloader as data_preloader
import logging
from logging.handlers import RotatingFileHandler
from blueprints.trade_api import * 
from config import config  

# 로깅 설정
handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Kafka 토픽 생성 함수
def create_topic(topic_name):
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER})
    topic_list = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    fs = admin_client.create_topics(topic_list)
    for topic, f in fs.items():
        try:
            f.result()
            logging.info(f"Topic '{topic}' created successfully")
        except Exception as e:
            if e.args[0].code() == 36:  # TOPIC_ALREADY_EXISTS
                logging.info(f"Topic '{topic}' already exists.")
            else:
                logging.error(f"Failed to create topic '{topic}': {e}")

import os

# create_app 함수
def create_app():
    app = Flask(__name__)

    # 환경 변수를 통해 동적으로 환경 값을 설정
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    app.config['ENV'] = config_name

    init_app(app)
    Session(app)

    # 블루프린트 등록
    app.register_blueprint(stock_kr, url_prefix='/stock_kr')
    app.register_blueprint(stock_kr_detail, url_prefix='/stock_kr_detail')
    app.register_blueprint(exchange, url_prefix='/exchange')
    app.register_blueprint(mypage, url_prefix='/mypage')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(trade_api, url_prefix='/api')  # trade_api 블루프린트 등록

    # 로그인 페이지로 리디렉션 설정
    @app.route('/')
    def main():
        return render_template('auth.html')

    return app

def start_background_tasks(app):
    """
    백그라운드 스레드 시작
    """
    # Kafka 소비자 스레드 시작
    consumer_thread = threading.Thread(target=consume_stock_data, daemon=True)
    consumer_thread.start()

    # 주문 처리 스레드 시작
    process_orders_thread = threading.Thread(target=process_orders, args=(app,), daemon=True)
    process_orders_thread.start()

if __name__ == "__main__":
    # 데이터 프리로딩
    try:
        data_preloader.fetch_kr_stock_data()
        logging.info("Stock data preloaded successfully")
    except Exception as e:
        logging.error(f"Error during data preloading: {e}")

    app = create_app()

    # 앱 컨텍스트 내에서 DB 초기화 및 테스트 유저 추가
    with app.app_context():
        db.create_all()
        register_process_order_thread(app)  # 주문 처리 스레드 시작
        create_topic(KAFKA_TOPIC)  # Kafka 토픽 생성

    # 백그라운드 스레드 실행
    start_background_tasks(app)

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=8080, debug=True)
