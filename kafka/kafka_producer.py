from confluent_kafka import Producer
from kafka.kafka_config import KAFKA_BROKER

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'security.protocol': 'PLAINTEXT',
    'api.version.request': False,
})

def get_producer():
    return producer
