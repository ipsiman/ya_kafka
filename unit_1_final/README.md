# Kafka Producer & Consumer на Python

Это приложение демонстрирует работу с Apache Kafka в режиме KRaft (без ZooKeeper) с использованием Python. Реализованы продюсер и батч-потребитель, запускаемые в Docker с масштабированием (по 2 экземпляра каждого).

---

## 📁 Структура проекта

```
.
├── docker-compose.yml          # Оркестрация сервисов
├── Dockerfile                  # Сборка Python-образа
├── requirements.txt            # Зависимости
├── message_model.py            # Модель сообщения
├── producer.py                 # Продюсер: отправляет сообщения
├── batch_message_consumer.py   # Потребитель: читает батчами
├── single_message_consumer.py  # Потребитель: читает по одному сообщению
├── topic.txt                   # Команды консоли создания топика и информация топике
└── README.md                   # Этот файл
```

---

## Классы и компоненты

### 1. `MessageModel` (`message_model.py`)

Модель сообщения, передаваемого через Kafka.

```python
class MessageModel:
    def __init__(self, message_id, content):
        self.message_id = message_id
        self.content = content
```

- **`serialize()`** — преобразует объект в JSON и кодирует в `bytes` для отправки в Kafka.
- **`deserialize(data)`** — восстанавливает объект из байтового JSON-представления.

> Используется для унифицированной передачи данных между producer и consumer.

---

### 2. `producer.py`

Продюсер, который:
- Генерирует случайные сообщения каждые 1.5 секунды.
- Сериализует их через `MessageModel`.
- Отправляет в топик `final-1-topic`.
- Использует `confluent_kafka` с подтверждением доставки.

**Особенности**:
- Поддержка retry и idempotence.
- Подключение к Kafka через внешние порты (`9094`, `9095`, `9096`).

---

### 3. `batch_message_consumer.py`

Батч-потребитель, который:
- Читает сообщения **пачками** (до 10 за раз).
- Десериализует их в `MessageModel`.
- Обрабатывает и логирует.
- Подтверждает offset **после обработки всего батча** (`at-least-once` семантика).

**Настройки**:
- `enable.auto.commit: False` — ручное подтверждение.
- `max.poll.records: 10` — ограничение размера батча.
- Группа потребителей: `batch-group`.

---

### 4. `single_message_consumer.py`

Потребитель, который:
- Читает сообщения **по одному**.
- Десериализует их в `MessageModel`.
- Обрабатывает и логирует.

**Настройки**:
- `enable.auto.commit: False` — ручное подтверждение.
- Группа потребителей: `single-group`.

### 5. `docker-compose.yml`

Запускает:
- **3-нодовый Kafka-кластер** в режиме KRaft.
- **Kafka UI** для мониторинга.
- **Producer ×2** через `replicas`.

---

## Инструкция по запуску

### 1. Убедитесь, что установлено:
- Docker
- Docker Compose

### 2. Запустите кластер и приложение (продюсер)

```bash
docker compose up
```

### 3. Создайте топик `final-1-topic` 

```bash
docker exec -it unit_1_final-kafka-0-1 kafka-topics.sh --create \
  --topic final-1-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 2
```

### 4. Запустите потребителей

```bash
python batch_message_consumer.py
```
или / и
```bash
python single_message_consumer.py
```

---

## Проверка работы

### 1. Логи в терминале
- Убедитесь, что **продюсеры** пишут:
  ```
  producer-1  | Message delivered to project-topic [0]
  producer-2  | Message delivered to project-topic [0]
  ```

- Убедитесь, что **потребители** читают:
  ```
  INFO:root:SingleConsumer received: Test message 2886
  ```

### 2. Kafka UI
Открой браузер: [http://localhost:8080](http://localhost:8080)

#### Проверьте:
- **Кластер `kraft`** — активен.
- **Топик `final-1-topic`**:
  - Растёт количество сообщений (в секции `Messages`).
  - Offset увеличивается.
