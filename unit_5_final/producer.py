import uuid
import time
from confluent_kafka import Producer


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(
            f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


def create_producer():
    config = {
        "bootstrap.servers": "localhost:1090",

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-1.crt",
        "ssl.key.location": "kafka-1.key",

        "sasl.mechanism": "PLAIN",
        "sasl.username": "producer",
        "sasl.password": "producer-secret",
    }
    return Producer(config)


if __name__ == '__main__':
    producer = create_producer()

    # Отправляем сообщения в оба топика
    for i in range(10):
        key = f"key-{uuid.uuid4()}"
        value1 = f"Message {i} for topic-1"
        value2 = f"Message {i} for topic-2"

        producer.produce('topic-1', key=key, value=value1, callback=delivery_report)
        producer.produce('topic-2', key=key, value=value2, callback=delivery_report)

        # Ждем немного между сообщениями
        time.sleep(0.2)

    # Ждем завершения отправки всех сообщений
    producer.flush()
    print("Все сообщения отправлены")
