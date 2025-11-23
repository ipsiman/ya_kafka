import uuid
from confluent_kafka import Producer

if __name__ == "__main__":
    config = {
        "bootstrap.servers": "localhost:1090",

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",
        "ssl.key.location": "kafka-1-creds/kafka-1.key",

        "sasl.mechanism": "PLAIN",
        "sasl.username": "producer",
        "sasl.password": "producer-secret",
    }

    producer = Producer(config)

    key = f"key-{uuid.uuid4()}"
    value = "SASL/PLAIN"

    producer.produce(
        "sasl-plain-topic",
        key=key,
        value=value,
    )

    producer.flush()
    print(f"Отправлено сообщение: {key=}, {value=}")
