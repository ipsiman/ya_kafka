#!/usr/bin/env python3
"""CLIENT API - Команды для поиска товаров и получения рекомендаций"""
import json
import time
import sys
import logging
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class ClientAPI:
    def __init__(self, kafka_config):
        self.producer = Producer(kafka_config)
        self.consumer = None
        self.kafka_config = kafka_config
    
    def search_product(self, product_name):
        """Поиск товара по имени"""
        log.info(f"Поиск товара: {product_name}")
        query = {
            "type": "search",
            "query": product_name,
            "timestamp": str(int(time.time() * 1000))
        }
        try:
            self.producer.produce(
                topic="client-queries",
                key="search".encode('utf-8'),
                value=json.dumps(query).encode('utf-8')
            )
            self.producer.flush()
            log.info(f"Запрос на поиск '{product_name}' отправлен в Kafka")
        except Exception as e:
            log.error(f"Ошибка при отправке запроса: {e}")
    
    def get_recommendations(self, user_id="default_user"):
        """Получение персонализированных рекомендаций"""
        log.info(f"Запрос рекомендаций для пользователя: {user_id}")
        query = {
            "type": "recommendations",
            "user_id": user_id,
            "timestamp": str(int(time.time() * 1000))
        }
        try:
            self.producer.produce(
                topic="client-queries",
                key="recommendations".encode('utf-8'),
                value=json.dumps(query).encode('utf-8')
            )
            self.producer.flush()
            log.info(f"Запрос рекомендаций отправлен в Kafka")
        except Exception as e:
            log.error(f"Ошибка при отправке запроса: {e}")

kafka_config = {
    "bootstrap.servers": "localhost:1090",
    "security.protocol": "SASL_SSL",
    "ssl.ca.location": "kafka_creds/ca.crt",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "client_api",
    "sasl.password": "client-api-secret",
    "client.id": "client-api"
}

api = ClientAPI(kafka_config)
if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == "search" and len(sys.argv) > 2:
        api.search_product(sys.argv[2])
    elif command == "recommendations":
        user_id = sys.argv[2] if len(sys.argv) > 2 else "default_user"
        api.get_recommendations(user_id)
    else:
        print("Использование: python client_api.py [search <name>|recommendations [user_id]]")
else:
    print("Использование: python client_api.py [search <name>|recommendations [user_id]]")
