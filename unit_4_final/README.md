# Kafka + Debezium + PostgreSQL: CDC Solution

## Описание

Этот проект демонстрирует реализацию Change Data Capture (CDC) с использованием:
- **PostgreSQL** – как источника данных,
- **Debezium** – для отслеживания изменений в БД,
- **Apache Kafka** – для потоковой передачи данных,
- **Schema Registry** – для управления схемами Avro,
- **Kafka Connect** – для интеграции компонентов.

## Инструкции по запуску через Docker Compose

1. **Клонируйте репозиторий или перейдите в директорию проекта**:
   ```bash
   cd unit_4_final
   ```

2. **Запустите все сервисы**:
   ```bash
   docker-compose up -d
   ```

3. **Дождитесь запуска всех контейнеров** (это может занять 1–2 минуты):
   ```bash
   docker-compose ps
   ```

4. **Проверьте логи Kafka Connect для подтверждения загрузки плагина Debezium**:
   ```bash
   docker logs kafka-connect
   ```

## Назначение компонентов и их взаимосвязи

| Компонент            | Назначение |
|----------------------|------------|
| **PostgreSQL**       | Хранит данные таблиц. |
| **Debezium Connector** | Отслеживает изменения в PostgreSQL и отправляет их в Kafka. |
| **Kafka**            | Распределённая шина сообщений. Принимает данные от Debezium и передаёт их консьюмерам. |
| **Schema Registry**  | Хранит и управляет схемами Avro для топиков Kafka. |
| **Kafka Connect**    | Запускает Debezium коннектор и взаимодействует с Kafka и PostgreSQL. |
| **Kafka UI**         | Веб-интерфейс для мониторинга Kafka. |
| **Debezium UI**      | Веб-интерфейс для управления Debezium коннекторами. |

### Связи:
- **Debezium** читает WAL PostgreSQL и публикует события в Kafka.
- **Kafka** принимает события и хранит их в топиках (например, `users.public.users`).
- **Schema Registry** предоставляет схемы для Avro-сообщений.
- **Kafka UI** позволяет просматривать топики и сообщения.
- **Debezium UI** позволяет управлять коннекторами без использования CLI.

## Настройки Debezium Connector

Коннектор настроен для отслеживания таблиц `public.users` и `public.orders`.

### Основные параметры:

```json
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "database.hostname": "postgres",
  "database.port": "5432",
  "database.user": "postgres-user",
  "database.password": "postgres-pw",
  "database.dbname": "customers",
  "database.server.name": "customers",
  "slot.name": "debezium_slot",
  "table.include.list": "public.users,public.orders",
  "snapshot.mode": "initial",
  "decimal.handling.mode": "precise",
  "include.schema.changes": "true",
  "heartbeat.interval.ms": "10000",
  "transforms": "unwrap",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "rewrite",
  "topic.prefix": "users",
  "topic.creation.enable": "true",
  "topic.creation.default.replication.factor": "-1",
  "topic.creation.default.partitions": "-1",
  "skipped.operations": "none"
}
```

### Пример применения настроек:

```bash
curl -X PUT \
-H "Content-Type: application/json" \
--data '{
   "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
   "database.hostname": "postgres",
   "database.port": "5432",
   "database.user": "postgres-user",
   "database.password": "postgres-pw",
   "database.dbname": "customers",
   "database.server.name": "customers",
   "slot.name": "debezium_slot",
   "table.include.list": "public.users,public.orders",
   "snapshot.mode": "initial",
   "decimal.handling.mode": "precise",
   "include.schema.changes": "true",
   "heartbeat.interval.ms": "10000",
   "transforms": "unwrap",
   "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
   "transforms.unwrap.drop.tombstones": "false",
   "transforms.unwrap.delete.handling.mode": "rewrite",
   "topic.prefix": "users",
   "topic.creation.enable": "true",
   "topic.creation.default.replication.factor": "-1",
   "topic.creation.default.partitions": "-1",
   "skipped.operations": "none"
 }' \
http://localhost:8083/connectors/pg-deb-connector/config
```

## Пошаговая проверка работоспособности

### 1. Проверьте статус Kafka Connect:

```bash
curl -s localhost:8083/ | jq
```

### 2. Проверьте список плагинов коннекторов:

```bash
curl localhost:8083/connector-plugins | jq
```

### 3. Создайте коннектор Debezium для PostgreSQL (если еще не создан):

```bash
curl -X PUT \
-H "Content-Type: application/json" \
--data '{
   "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
   "database.hostname": "postgres",
   "database.port": "5432",
   "database.user": "postgres-user",
   "database.password": "postgres-pw",
   "database.dbname": "customers",
   "database.server.name": "customers",
   "slot.name": "debezium_slot",
   "table.include.list": "public.users,public.orders",
   "snapshot.mode": "initial",
   "decimal.handling.mode": "precise",
   "include.schema.changes": "true",
   "heartbeat.interval.ms": "10000",
   "transforms": "unwrap",
   "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
   "transforms.unwrap.drop.tombstones": "false",
   "transforms.unwrap.delete.handling.mode": "rewrite",
   "topic.prefix": "users",
   "topic.creation.enable": "true",
   "topic.creation.default.replication.factor": "-1",
   "topic.creation.default.partitions": "-1",
   "skipped.operations": "none"
 }' \
http://localhost:8083/connectors/pg-deb-connector/config
```

### 4. Проверьте статус коннектора и убедитесь, что он работает корректно:

```bash
curl -s localhost:8083/connectors/pg-deb-connector/status | jq
```

Должно быть `"state": "RUNNING"`.

### 5. Подключитесь к PostgreSQL и создайте таблицы (если еще не созданы):

```bash
docker exec -it postgres psql -U postgres-user -d customers
```

Затем выполните SQL команды:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_name VARCHAR(100),
    quantity INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Добавьте тестовые данные в таблицы:

```sql
-- Добавление пользователей
INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');
INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com');
INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob Brown', 'bob@example.com');

-- Добавление заказов
INSERT INTO orders (user_id, product_name, quantity) VALUES (1, 'Product A', 2);
INSERT INTO orders (user_id, product_name, quantity) VALUES (1, 'Product B', 1);
INSERT INTO orders (user_id, product_name, quantity) VALUES (2, 'Product C', 5);
INSERT INTO orders (user_id, product_name, quantity) VALUES (3, 'Product D', 3);
INSERT INTO orders (user_id, product_name, quantity) VALUES (4, 'Product E', 4);
```

### 7. Проверьте сообщения в топиках Kafka:

Для таблицы users:
```bash
docker exec -it unit_4_final-schema-registry-1 kafka-avro-console-consumer \
  --bootstrap-server kafka-0:9092 \
  --topic users.public.users \
  --from-beginning \
  --property schema.registry.url=http://schema-registry:8081
```

Для таблицы orders:
```bash
docker exec -it unit_4_final-schema-registry-1 kafka-avro-console-consumer \
  --bootstrap-server kafka-0:9092 \
  --topic users.public.orders \
  --from-beginning \
  --property schema.registry.url=http://schema-registry:8081
```

### 8. Проверьте работу CDC - добавьте новые данные и убедитесь, что они попадают в Kafka:

```sql
INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com');
```

### 9. (Опционально) Удалите коннектор при необходимости:

```bash
curl -X DELETE http://localhost:8083/connectors/pg-deb-connector
```

---

## 🧹 Остановка и очистка

Остановка всех сервисов:

```bash
docker-compose down
```

Удаление данных (томов):

```bash
docker-compose down -v
```

---

## Веб-интерфейсы

- **Kafka UI**: http://localhost:8080
- **Debezium UI**: http://localhost:8085
