from confluent_kafka import Producer


# Конфигурация продюсера – адрес сервера
conf = {
    "bootstrap.servers": "localhost:9094",
}
# Создание продюсера
producer = Producer(conf)

# Отправка сообщения
producer.produce(
    topic="my_topic",
    key="key-1",
    value="message-155",
)
# Ожидание завершения отправки всех сообщений
producer.flush()
