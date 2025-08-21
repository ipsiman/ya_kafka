from confluent_kafka import Producer
from message_model import MessageModel
import random
import time

def delivery_report(err, msg):
    if err:
        print(f'[ERROR] Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

conf = {
    'bootstrap.servers': 'kafka-0:9092',
    'acks': 'all',           # At least once
    'retries': 5             # Enable retry logic
}

producer = Producer(conf)

try:
    while True:
        msg_id = random.randint(1000, 9999)
        content = f"Test message {msg_id}"
        message = MessageModel(msg_id, content)
        serialized = message.serialize()
        if serialized:
            producer.produce('final-1-topic', value=serialized, callback=delivery_report)
        producer.poll(0)
        time.sleep(1.5)
except KeyboardInterrupt:
    print("Stopping producer...")
finally:
    producer.flush()
