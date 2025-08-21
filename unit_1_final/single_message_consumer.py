from confluent_kafka import Consumer, KafkaException
from message_model import MessageModel
import logging

logging.basicConfig(level=logging.INFO)

conf = {
    'bootstrap.servers': 'localhost:9094',
    'group.id': 'single-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(conf)
consumer.subscribe(['final-1-topic'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        message = MessageModel.deserialize(msg.value())
        if message:
            logging.info(f"SingleConsumer received: {message.content}")
except KeyboardInterrupt:
    logging.info("Stopping SingleMessageConsumer...")
finally:
    consumer.close()
