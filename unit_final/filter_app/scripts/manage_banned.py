#!/usr/bin/env python3
"""Управление списком запрещенных товаров через CLI"""
import sys
import json
from confluent_kafka import Producer

def manage_banned_product(action, product_id, kafka_config):
    producer = Producer(kafka_config)
    message = {
        "product_id": product_id,
        "action": action
    }
    try:
        producer.produce(
            topic="banned-products",
            key=product_id.encode('utf-8'),
            value=json.dumps(message).encode('utf-8')
        )
        producer.flush()
        print(f"Команда '{action}' для товара {product_id} отправлена")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    kafka_config = {
        "bootstrap.servers": "localhost:1090",
        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "kafka_creds/ca.crt",
        "sasl.mechanism": "PLAIN",
        "sasl.username": "faust",
        "sasl.password": "faust-secret"
    }
    if len(sys.argv) < 3:
        print("Использование: python manage_banned.py [add|remove] <product_id>")
        sys.exit(1)
    action = sys.argv[1]
    product_id = sys.argv[2]
    if action not in ['add', 'remove']:
        print("Действие должно быть 'add' или 'remove'")
        sys.exit(1)
    manage_banned_product(action, product_id, kafka_config)
