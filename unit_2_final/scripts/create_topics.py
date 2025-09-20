import logging
from confluent_kafka.admin import AdminClient, NewTopic

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Подключаемся ко всем брокерам
conf = {'bootstrap.servers': 'kafka-0:9092,kafka-1:9092,kafka-2:9092'}
admin = AdminClient(conf)

# Определяем топики с 4 партициями и replication_factor=3 (для 3 брокеров)
topics = [
    NewTopic("messages", num_partitions=4, replication_factor=3),
    NewTopic("blocked_users", num_partitions=4, replication_factor=3),
    NewTopic("filtered_messages", num_partitions=4, replication_factor=3),
]

log.info("Создание топиков...")
fs = admin.create_topics(topics)

for topic, f in fs.items():
    try:
        f.result()  # Ждём завершения
        log.info(f"Топик '{topic}' создан")
    except Exception as e:
        log.error(f"Ошибка создания топика '{topic}': {e}")

log.info("Все топики созданы")
