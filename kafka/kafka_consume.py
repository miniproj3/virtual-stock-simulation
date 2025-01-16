from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import logging
import threading
from kafka.kafka_config import KAFKA_BROKER, KAFKA_TOPIC, KAFKA_STOCK_KR_DETAIL_TOPIC

# 전역 변수로 데이터를 초기화
stock_data = []
chart_data = []

def consume_stock_data():
    global stock_data
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'stock_consumer_group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([KAFKA_TOPIC])
    logging.basicConfig(level=logging.INFO)
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.info(f"Reached end of {msg.topic()} partition {msg.partition()} at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            stock = json.loads(msg.value().decode('utf-8'))
            logging.info(f"Received stock data: {stock}")
            stock_data.append(stock)
            logging.info(f"Updated stock_data: {stock_data}")
    except KafkaException as ke:
        logging.error(f"Kafka error: {ke}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        consumer.close()

def consume_chart_data():
    global chart_data
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'chart_consumer_group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([KAFKA_STOCK_KR_DETAIL_TOPIC])
    logging.basicConfig(level=logging.INFO)
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.info(f"Reached end of {msg.topic()} partition {msg.partition()} at offset {msg.offset()}")
                else:
                    raise KafkaException(msg.error())
            chart = json.loads(msg.value().decode('utf-8'))
            logging.info(f"Received chart data: {chart}")
            chart_data.append(chart)
            logging.info(f"Updated chart_data: {chart_data}")
    except KafkaException as ke:
        logging.error(f"Kafka error: {ke}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        consumer.close()

def start_kafka_consumer():
    consumer_thread_stock = threading.Thread(target=consume_stock_data, daemon=True)
    consumer_thread_chart = threading.Thread(target=consume_chart_data, daemon=True)
    consumer_thread_stock.start()
    consumer_thread_chart.start()
