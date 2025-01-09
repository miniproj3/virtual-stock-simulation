from flask import Flask, render_template, session
from flask_session import Session
from flask_login import *
from db import *
from stock_kr import stock_kr
from exchange import exchange
from mypage import mypage
import threading
from kafka_consume import consume_stock_data  # Kafka Consumer 함수 추가
from confluent_kafka.admin import AdminClient, NewTopic
from kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import data_preloader  # data_preloader.py 추가
import logging
from logging.handlers import RotatingFileHandler

# 로깅 설정
handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Kafka 토픽 생성 함수
def create_topic(topic_name):
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER})
    topic_list = [NewTopic(topic=topic_name, num_partitions=1, replication_factor=1)]
    fs = admin_client.create_topics(topic_list)
    for topic, f in fs.items():
        try:
            f.result()
            logging.info(f"Topic '{topic}' created successfully")
        except Exception as e:
            logging.error(f"Failed to create topic '{topic}': {e}")

# Flask 애플리케이션 초기화
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # db.py에서 정의된 db와 연결
    init_app(app)  # db 초기화
    Session(app)

    # 블루프린트 등록
    app.register_blueprint(stock_kr, url_prefix='/stock_kr')
    app.register_blueprint(exchange, url_prefix='/exchange')
    app.register_blueprint(mypage, url_prefix='/mypage')

    @app.route('/')
    def main():
        user = User.query.filter_by(username='testuser').first()
        if user:
            session['username'] = user.username
            session['seed_krw'] = user.seed_krw
            session['seed_usd'] = user.seed_usd
            return render_template('stock_kr.html', user=user)
        else:
            return "User not found", 404

    return app

def start_kafka_consumer():
    # Kafka Consumer를 별도의 스레드에서 실행
    consumer_thread = threading.Thread(target=consume_stock_data, daemon=True)
    consumer_thread.start()

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
        db.create_all()  # 테이블 초기화

        # 테스트 유저 추가
        if not User.query.filter_by(username='testuser').first():
            test_user = User(username='testuser', seed_krw=1000000)  # 임시
            db.session.add(test_user)
            db.session.commit()

        # Kafka 토픽 생성
        create_topic(KAFKA_TOPIC)

    # Kafka Consumer를 백그라운드에서 실행
    start_kafka_consumer()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)