from confluent_kafka import Consumer

if __name__ == "__main__":
    consumer_conf = {
        "bootstrap.servers": "localhost:9093",
        "group.id": "consumer-ssl-group",
        "auto.offset.reset": "earliest",
        "security.protocol": "SSL",
        "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
        "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",  # Сертификат клиента Kafka
        "ssl.key.location": "kafka-1-creds/kafka-1.key",  # Приватный ключ для клиента Kafka
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe(["ssl-topic"])
    try:
        while True:
            message = consumer.poll(0.1)
            if message is None:
                continue
            if message.error():
                print(f"Ошибка: {message.error()}")
                continue
            key = message.key().decode("utf-8")
            value = message.value().decode("utf-8")
            print(f"Получено сообщение: {key=}, {value=}, offset={message.offset()}")
    finally:
        consumer.close()
