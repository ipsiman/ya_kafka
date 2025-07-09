import time

from confluent_kafka import Consumer


# Настройка консьюмера – адрес сервера
conf = {
    "bootstrap.servers": "localhost:9094",
    "group.id": "my-group",
    "auto.offset.reset": "earliest",
}
# Создание консьюмера
consumer = Consumer(conf)

# Подписка на топик
consumer.subscribe(["my_topic"])

# Чтение сообщений в бесконечном цикле
try:
    while True:
        # Получение сообщений
        msg = consumer.poll(0.1)

        if msg is None:
            continue
        if msg.error():
            print(f"Ошибка: {msg.error()}")
            continue

        key = msg.key().decode("utf-8")
        value = msg.value().decode("utf-8")
        print(f"Получено сообщение: {key=}, {value=}, offset={msg.offset()}")
        time.sleep(1)
finally:
    # Закрытие консьюмера
    consumer.close()
