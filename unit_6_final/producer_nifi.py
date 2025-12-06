import time
import random
import logging
import json
from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# Настройки Producer
config = {
    "bootstrap.servers": "localhost:9094",
    "batch.num.messages": 10,
    "queue.buffering.max.messages": 50,
    "queue.buffering.max.ms": 1000,
}


class PurchaseProducer:
    def __init__(self):
        self.producer = Producer(config)

        # Данные для генерации фейковых данных
        self.customers = [
            "Иван Петров", "Мария Сидорова", "Алексей Козлов",
            "Елена Новикова", "Дмитрий Волков", "Ольга Морозова",
            "Сергей Павлов", "Анна Лебедева", "Михаил Соловьев"
        ]

        self.products = [
            {"name": "Ноутбук", "price_range": (30000, 150000)},
            {"name": "Смартфон", "price_range": (15000, 80000)},
            {"name": "Наушники", "price_range": (2000, 25000)},
            {"name": "Планшет", "price_range": (10000, 50000)},
            {"name": "Монитор", "price_range": (8000, 40000)},
            {"name": "Клавиатура", "price_range": (500, 5000)},
            {"name": "Мышь", "price_range": (300, 3000)}
        ]

    def generate_fake_purchase(self):
        """Генерация фейковой покупки"""
        customer = random.choice(self.customers)
        product = random.choice(self.products)
        quantity = random.randint(1, 3)
        price = random.randint(*product["price_range"])
        amount = price * quantity

        purchase_data = {
            "order_id": f"ORD-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
            "customer_name": customer,
            "product_name": product["name"],
            "quantity": quantity,
            "amount": float(amount),
            "timestamp": int(time.time() * 1000)
        }

        return purchase_data

    def delivery_report(self, err, msg):
        """Callback для отчетов о доставке"""
        if err is not None:
            log.error(f"Ошибка доставки сообщения: {err}")
        else:
            log.info(f"Сообщение доставлено в топик {msg.topic()} "
                     f"[партиция {msg.partition()}] @ offset {msg.offset()}")

    def produce_purchases(self, num_messages=100, delay=1):
        """Генерация и отправка сообщений"""
        log.info(f"Запуск продюсера. Будет отправлено {num_messages} сообщений...")

        for i in range(num_messages):
            try:
                # Генерация данных
                purchase_data = self.generate_fake_purchase()
                key = purchase_data["order_id"]

                # Отправка в Kafka
                self.producer.produce(
                    topic="purchases",
                    key=key,
                    value=json.dumps(purchase_data, ensure_ascii=False),
                    callback=self.delivery_report
                )

                log.info(f"Отправлено сообщение {i + 1}/{num_messages}: "
                         f"{purchase_data['customer_name']} купил(а) "
                         f"{purchase_data['product_name']} за {purchase_data['amount']} руб.")

                # Небольшая задержка между сообщениями
                time.sleep(delay)

                # Периодическая flush для надежности
                if i % 10 == 0:
                    self.producer.poll(0)

            except Exception as e:
                log.error(f"Ошибка при отправке сообщения: {e}")

        # Завершение работы
        self.producer.flush()
        log.info("Все сообщения отправлены!")


if __name__ == "__main__":
    producer = PurchaseProducer()
    producer.produce_purchases(num_messages=10, delay=1)
