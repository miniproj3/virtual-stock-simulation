from flask import Flask, render_template, session
from flask_session import Session
from flask_login import *
from db import *
from blueprints.stock_kr import stock_kr
from blueprints.auth import auth
from blueprints.stock_kr_detail import stock_kr_detail  # 추가된 부분
from blueprints.exchange import exchange
from blueprints.mypage import mypage
import threading
from kafka.kafka_consume import consume_stock_data
from confluent_kafka.admin import AdminClient, NewTopic
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC
import kafka.data_preloader as data_preloader
import logging
from logging.handlers import RotatingFileHandler
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

# Flask 애플리케이션 초기화
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 설정을 적용합니다.

    # db.py에서 정의된 db와 연결
    init_app(app)
    Session(app)

    # 블루프린트 등록
    app.register_blueprint(stock_kr, url_prefix='/stock_kr')
    app.register_blueprint(stock_kr_detail, url_prefix='/stock_kr_detail')  # 추가된 부분
    app.register_blueprint(exchange, url_prefix='/exchange')
    app.register_blueprint(mypage, url_prefix='/mypage')
    app.register_blueprint(auth, url_prefix='/auth')

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

    app = create_app('development')  # 개발 환경 설정을 사용합니다.

    # 앱 컨텍스트 내에서 DB 초기화 및 테스트 유저 추가
    with app.app_context():
        db.create_all()

        # 테스트 유저 추가
        if not User.query.filter_by(username='testuser').first():
            test_user = User(username='testuser', seed_krw=1000000)
            db.session.add(test_user)
            db.session.commit()

        # Kafka 토픽 생성
        create_topic(KAFKA_TOPIC)

    # Kafka Consumer를 백그라운드에서 실행
    start_kafka_consumer()

    # Flask 애플리케이션 실행
    app.run(host="0.0.0.0", port=5000, debug=True)