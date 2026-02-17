#!/usr/bin/env python3
"""SHOP API - Продюсер для отправки товаров в Kafka"""
import json
import time
import logging
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class ShopAPIProducer:
    def __init__(self, config):
        self.producer = Producer(config)
        self.admin_client = AdminClient(config)
    
    def create_topic_if_not_exists(self, topic_name, num_partitions=3, replication_factor=3):
        topic_list = [NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        futures = self.admin_client.create_topics(topic_list)
        for topic, future in futures.items():
            try:
                future.result()
                log.info(f"Топик {topic} создан")
            except Exception as e:
                log.error(f"Ошибка при создании топика {topic}: {e}")
    
    def delivery_report(self, err, msg):
        if err is not None:
            log.error(f"Ошибка доставки: {err}")
        else:
            log.info(f"Товар отправлен в {msg.topic()} [партиция {msg.partition()}] @ offset {msg.offset()}")
    
    def load_products(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Ошибка загрузки файла: {e}")
            return []
    
    def send_products(self, products, topic_name="shop-products", delay=0.5):
        log.info(f"Отправка {len(products)} товаров в топик {topic_name}")
        for i, product in enumerate(products, 1):
            try:
                key = product.get("product_id", "").encode('utf-8')
                value = json.dumps(product, ensure_ascii=False).encode('utf-8')
                self.producer.produce(topic=topic_name, key=key, value=value, callback=self.delivery_report)
                log.info(f"Отправлен товар {i}/{len(products)}: {product.get('name', 'Unknown')}")
                time.sleep(delay)
                if i % 10 == 0:
                    self.producer.poll(0)
            except Exception as e:
                log.error(f"Ошибка при отправке товара {i}: {e}")
        self.producer.flush()
        log.info("Все товары отправлены!")

if __name__ == "__main__":
    config = {
        "bootstrap.servers": "localhost:1090",
        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "kafka_creds/ca.crt",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "shop_api",
        "sasl.password": "shop-api-secret",
        "client.id": "shop-api-producer"
    }
    producer = ShopAPIProducer(config)
    producer.create_topic_if_not_exists("shop-products", num_partitions=3, replication_factor=3)
    products = producer.load_products("shop_api/products.json")
    if products:
        producer.send_products(products, topic_name="shop-products", delay=0.5)
