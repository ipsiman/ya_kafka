# Импортируем необходимые классы из библиотеки confluent_kafka
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.json_schema import JSONSerializer


def user_to_dict(user, ctx):
    """
    Функция для преобразования объекта пользователя в словарь.
    В данном случае просто возвращает сам объект, так как он уже является dict.
    Используется при сериализации данных перед отправкой в Kafka.
    """
    return user


def delivery_report(err, msg):
    """
    Callback-функция, вызываемая после попытки доставки сообщения.
    Выводит результат доставки: успех или ошибка.
    """
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Delivered message to topic {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


# Определяем JSON-схему для валидации данных пользователя
USER_SCHEMA_STR = """
{
 "$schema": "http://json-schema.org/draft-07/schema#",
 "title": "User",
 "type": "object",
 "properties": {
    "name": {"type": "string"},
    "favoriteNumber": {"type": "integer"},
    "favoriteColor": {"type": "string"}
 },
 "required": ["name", "favoriteNumber", "favoriteColor"]
}
"""

if __name__ == "__main__":
    # Конфигурационные параметры подключения
    bootstrap_servers = "localhost:9094,localhost:9095,localhost:9096"  # Адреса брокеров Kafka
    schema_registry_url = "http://localhost:8081"  # URL Schema Registry
    topic = "user"  # Название топика Kafka
    subject = topic + "-value"  # Название субъекта в Schema Registry (по умолчанию topic-name-value)

    # Конфигурация продюсера Kafka
    producer_conf = {
        "bootstrap.servers": bootstrap_servers,
    }
    producer = Producer(producer_conf)  # Создаем экземпляр продюсера

    # Создаем клиент для взаимодействия с Schema Registry
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

    # Проверяем, существует ли уже схема в Schema Registry
    try:
        latest = schema_registry_client.get_latest_version(subject)
        print(f"Schema is already registered for {subject}:\n{latest.schema.schema_str}")
    except Exception:
        # Если схема не найдена, регистрируем новую
        schema_object = Schema(USER_SCHEMA_STR, "JSON")  # Создаем объект схемы
        schema_id = schema_registry_client.register_schema(subject,
                                                           schema_object)  # Регистрируем схему
        print(f"Registered schema for {subject} with id: {schema_id}")

    # Создаем сериализатор JSON с использованием схемы
    json_serializer = JSONSerializer(USER_SCHEMA_STR, schema_registry_client,
                                     user_to_dict)

    # Данные пользователя для отправки
    user = {
        "name": "First user",
        "favoriteNumber": 42,
        "favoriteColor": "blue",
    }

    # Создаем контекст сериализации (указываем топик и тип поля - значение сообщения)
    context = SerializationContext(topic, MessageField.VALUE)

    # Сериализуем данные пользователя в байты
    serialized_value = json_serializer(user, context)

    # Отправляем сообщение в Kafka
    producer.produce(
        topic,
        key="first-user",  # Ключ сообщения
        value=serialized_value,  # Сериализованное значение
        headers=[("myTestHeader", b"header values are binary")],  # Заголовки сообщения
        callback=delivery_report,
        # Callback-функция для отслеживания результата доставки
    )

    # Ждем завершения всех асинхронных операций отправки
    producer.flush()
