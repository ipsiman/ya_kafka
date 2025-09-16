import json
import time
import uuid

from confluent_kafka import Producer, Consumer, KafkaException


# === Конфигурация продюсера ===
producer_conf = {
    'bootstrap.servers': 'localhost:9094',
    'acks': 'all',
    'retries': 5,
    'client.id': 'test-producer'
}

producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err:
        print(f'[ERROR] Message delivery failed: {err}')
    else:
        print(
            f'Сообщение доставлено в {msg.topic()} '
            f'[{msg.partition()}] @ offset {msg.offset()}'
        )

# === Конфигурация консьюмера ===
consumer_conf = {
    'bootstrap.servers': 'localhost:9094',
    'group.id': f'test-group-{uuid.uuid4()}',  # уникальная группа для каждого запуска
    'auto.offset.reset': 'earliest',           # читаем с самого начала
    'enable.auto.commit': False,               # контролируем коммит вручную
    'client.id': 'test-consumer'
}

consumer = Consumer(consumer_conf)
consumer.subscribe(['filtered_messages'])

# === Шаг 1: Отправка команды блокировки ===
print("Отправка команды блокировки...")
block_command = {
    "user": "alice",
    "blocked_user": "bob",
    "action": "add"
}

producer.produce(
    topic='blocked_users',
    value=json.dumps(block_command, ensure_ascii=False).encode('utf-8'),
    callback=delivery_report
)
producer.poll(0)
producer.flush(timeout=5.0)
print("Команда блокировки отправлена.")

time.sleep(3)  # Даём Faust время обработать команду

# === Шаг 2: Отправка сообщений ===
print("Отправка тестовых сообщений...")
messages = [
    {
        "sender": "bob",
        "recipient": "alice",
        "text": "Привет, ты глупый дурак!",
        "timestamp": "2025-04-05T10:00:00Z"
    },
    {
        "sender": "charlie",
        "recipient": "alice",
        "text": "Ты идиот, но я тебя люблю!",
        "timestamp": "2025-04-05T10:01:00Z"
    },
    {
        "sender": "tedd",
        "recipient": "mark",
        "text": "Hello my friend!",
        "timestamp": "2025-04-05T10:04:00Z"
    }
]

for i, msg in enumerate(messages):
    producer.produce(
        topic='messages',
        value=json.dumps(msg, ensure_ascii=False).encode('utf-8'),
        callback=delivery_report
    )
    producer.poll(0)
    time.sleep(0.5)

producer.flush(timeout=10.0)
print("Все сообщения отправлены.")

# === Шаг 3: Чтение обработанных сообщений ===
print("Ожидание обработанных сообщений из 'filtered_messages' (таймаут 5 сек)...")

received_messages = []
start_time = time.time()
timeout = 5

try:
    while time.time() - start_time < timeout:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            message_data = json.loads(msg.value().decode('utf-8'))
            received_messages.append(message_data)
            print(f"Получено: {message_data}")
            consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()

# === Шаг 4: Проверка результатов ===
print("\n" + "="*60)
print("РЕЗУЛЬТАТЫ ТЕСТА:")
print("="*60)

expected_censored_text = "Ты [CENSORED], но я тебя люблю!"

found_expected = False
for msg in received_messages:
    if msg["sender"] == "charlie" and msg["recipient"] == "alice":
        if msg["text"] == expected_censored_text:
            print("Цензура сработала: запрещённые слова заменены на [CENSORED]")
            found_expected = True
        else:
            print(f"Цензура НЕ сработала: текст = '{msg['text']}'")

if not found_expected and received_messages:
    print(
        f"Не найдено ожидаемое сообщение от charlie "
        f"с текстом: '{expected_censored_text}'"
    )

# Проверка: сообщение от bob НЕ должно появиться
bob_messages = [m for m in received_messages if m["sender"] == "bob"]
if not bob_messages:
    print("Блокировка сработала: сообщения от bob не дошли до alice")
else:
    print(f"Блокировка НЕ сработала: получено {len(bob_messages)} сообщений от bob")

if not received_messages:
    print("Нет сообщений в топике filtered_messages, ошибка в Faust или Kafka")

print("="*60)
