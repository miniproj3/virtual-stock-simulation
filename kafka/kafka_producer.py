from confluent_kafka import Producer
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC, KAFKA_STOCK_KR_DETAIL_TOPIC
import json

producer = Producer({
    'bootstrap.servers': KAFKA_BROKER,
    'security.protocol': 'PLAINTEXT',
    'api.version.request': False,
})

def get_producer():
    return producer

def send_stock_data(stock_data):
    producer.produce(KAFKA_TOPIC, key=str(stock_data['symbol']), value=json.dumps(stock_data))
    producer.flush()
    print("Stock data sent to KAFKA_TOPIC.")

def send_chart_data(chart_data):
    producer.produce(KAFKA_STOCK_KR_DETAIL_TOPIC, key=str(chart_data['symbol']), value=json.dumps(chart_data))
    producer.flush()
    print("Chart data sent to KAFKA_STOCK_KR_DETAIL_TOPIC.")
