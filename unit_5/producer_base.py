import uuid
from confluent_kafka import Producer

if __name__ == "__main__":
    producer_conf = {
        "bootstrap.servers": "localhost:9093",
        "security.protocol": "SSL",
        "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
        "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",  # Сертификат клиента Kafka
        "ssl.key.location": "kafka-1-creds/kafka-1.key",  # Приватный ключ для клиента Kafka
    }
    producer = Producer(producer_conf)
    key = f"key-{uuid.uuid4()}"
    value = "SSL message"
    producer.produce(
        "ssl-topic",
        key=key,
        value=value,
    )
    producer.flush()
    print(f"Отправлено сообщение: {key=}, {value=}")
