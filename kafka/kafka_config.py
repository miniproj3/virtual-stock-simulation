import os

KAFKA_BROKER = f"{os.getenv('PUBLIC_IP', 'localhost')}:9092"
KAFKA_TOPIC = 'kr_stock_data'
KAFKA_STOCK_KR_DETAIL_TOPIC = 'kr_stock_detail_data'
