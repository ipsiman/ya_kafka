from confluent_kafka import Consumer

if __name__ == "__main__":
    consumer_conf = {
        "bootstrap.servers": "localhost:1090",
        "group.id": "consumer-sasl-group",
        "auto.offset.reset": "earliest",

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",
        "ssl.key.location": "kafka-1-creds/kafka-1.key",

        "sasl.mechanism": "PLAIN",
        "sasl.username": "consumer",
        "sasl.password": "consumer-secret",
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe(["sasl-plain-topic"])
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
