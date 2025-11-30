import logging

from confluent_kafka import avro
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class PurchaseConsumer:
    def __init__(self):
        # Настройки AvroConsumer
        avro_consumer_config = {
            "bootstrap.servers": "rc1a-eoekpp9ig4p786n4.mdb.yandexcloud.net:9091,rc1a-mbm9ss0t6v6rp11g.mdb.yandexcloud.net:9091,rc1a-uo7obcva7la6ss6t.mdb.yandexcloud.net:9091",
            "security.protocol": "SASL_SSL",
            "ssl.ca.location": "YandexInternalRootCA.crt",
            "sasl.mechanism": "SCRAM-SHA-512",
            "sasl.username": "consumer",
            "sasl.password": "lkddfgfglfh",
            "schema.registry.url": "https://rc1a-eoekpp9ig4p786n4.mdb.yandexcloud.net:443",
            "schema.registry.basic.auth.credentials.source": "SASL_INHERIT",
            "schema.registry.ssl.ca.location": "YandexInternalRootCA.crt",
            'group.id': 'purchase-consumer-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }

        self.consumer = AvroConsumer(avro_consumer_config)

    def format_timestamp(self, timestamp_ms):
        """Форматирование timestamp в читаемый вид"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')

    def calculate_statistics(self, purchases):
        """Расчет статистики по покупкам"""
        if not purchases:
            return

        total_amount = sum(p['amount'] for p in purchases)
        avg_amount = total_amount / len(purchases)

        print(f"\n=== СТАТИСТИКА ===")
        print(f"Всего покупок: {len(purchases)}")
        print(f"Общая сумма: {total_amount:.2f} руб.")
        print(f"Средний чек: {avg_amount:.2f} руб.")

        # Топ товаров
        from collections import Counter
        product_counts = Counter(p['product_name'] for p in purchases)
        print(f"Популярные товары: {dict(product_counts.most_common(3))}")

    def consume_purchases(self, max_messages=100):
        """Чтение сообщений из Kafka"""
        self.consumer.subscribe(['purchases'])

        print("Запуск консьюмера. Ожидание сообщений...")

        purchases = []
        message_count = 0

        try:
            while message_count < max_messages:
                try:
                    msg = self.consumer.poll(1.0)

                    if msg is None:
                        continue
                    if msg.error():
                        print(f"Ошибка потребителя: {msg.error()}")
                        continue

                    # Извлечение данных сообщения
                    value = msg.value()

                    message_count += 1
                    purchases.append(value)

                    # Вывод информации о покупке
                    print(f" ПОКУПКА #{message_count}")
                    print(f"   Заказ: {value['order_id']}")
                    print(f"   Клиент: {value['customer_name']}")
                    print(f"   Товар: {value['product_name']} (x{value['quantity']})")
                    print(f"   Сумма: {value['amount']:.2f} руб.")
                    print(f"   Время: {self.format_timestamp(value['timestamp'])}")
                    print(f"   Партиция: {msg.partition()}, Offset: {msg.offset()}")

                    # Коммит offset каждые 10 сообщений
                    if message_count % 10 == 0:
                        self.consumer.commit()
                        print(f"Завершено сообщений: {message_count}")

                        # Промежуточная статистика
                        self.calculate_statistics(purchases[-10:])

                except SerializerError as e:
                    print(f"Ошибка десериализации сообщения: {e}")
                except Exception as e:
                    print(f"Неожиданная ошибка: {e}")

        except KeyboardInterrupt:
            print("\nОстановка консьюмера...")

        finally:
            # Финальная статистика
            self.calculate_statistics(purchases)

            # Закрытие потребителя
            self.consumer.close()
            print(f"\nКонсьюмер остановлен. Обработано сообщений: {len(purchases)}")


if __name__ == "__main__":
    consumer = PurchaseConsumer()
    consumer.consume_purchases(max_messages=50)
