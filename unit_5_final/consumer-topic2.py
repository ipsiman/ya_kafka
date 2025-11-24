from confluent_kafka import Consumer


def create_consumer():
    config = {
        "bootstrap.servers": "localhost:1090",
        "group.id": "consumer-sasl-group",
        "auto.offset.reset": "earliest",

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-1.crt",
        "ssl.key.location": "kafka-1.key",

        "sasl.mechanism": "PLAIN",
        "sasl.username": "consumer",
        "sasl.password": "consumer-secret",
    }
    return Consumer(config)


if __name__ == '__main__':
    consumer = create_consumer()
    consumer.subscribe(['topic-2'])

    print("Попытка потребления сообщений из topic-2 (должна быть ошибка доступа)...")
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f'Ошибка: {message.error()}')
                continue

            key = message.key().decode('utf-8') if message.key() else None
            value = message.value().decode('utf-8')
            print(f'Получено сообщение: key={key}, value={value}')

    except KeyboardInterrupt:
        print("Потребление остановлено")
    finally:
        consumer.close()
