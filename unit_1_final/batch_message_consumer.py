from confluent_kafka import Consumer, KafkaException
from message_model import MessageModel
import logging

logging.basicConfig(level=logging.INFO)

conf = {
    'bootstrap.servers': 'localhost:9094',
    'group.id': 'batch-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'fetch.min.bytes': 1024 * 10,  # Minimum bytes per fetch
    'max.poll.records': 10         # Max records per poll
}

consumer = Consumer(conf)
consumer.subscribe(['final-1-topic'])

try:
    while True:
        messages = consumer.poll(1.0, num_messages=10)
        if not messages:
            continue

        for msg in messages:
            if msg.error():
                raise KafkaException(msg.error())

            message = MessageModel.deserialize(msg.value())
            if message:
                logging.info(f"BatchConsumer received: {message.content}")

        consumer.commit(asynchronous=False)  # Commit after batch
except KeyboardInterrupt:
    logging.info("Stopping BatchMessageConsumer...")
finally:
    consumer.close()
