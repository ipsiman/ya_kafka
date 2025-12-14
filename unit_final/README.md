# Финальный проект: Аналитическая платформа для маркетплейса

## Описание проекта

Проект представляет собой аналитическую платформу для маркетплейса "Покупай выгодно", которая собирает и обрабатывает данные о взаимодействии клиентов с сайтом: просмотры товаров, добавление в корзину, покупки и отзывы.

## Архитектура системы

- **SHOP API**: Эмуляция API магазинов для отправки данных о товарах в Kafka
- **CLIENT API**: Эмуляция API клиентов для поиска товаров и получения рекомендаций
- **Apache Kafka (Кластер 1)**: Основной кластер с TLS и ACL для безопасной передачи данных
- **Apache Kafka (Кластер 2)**: Второй кластер для дублирования данных
- **Faust**: Потоковая обработка данных для фильтрации запрещенных товаров
- **Kafka Connect**: Запись отфильтрованных данных в файл
- **Prometheus + Grafana**: Мониторинг кластера Kafka
- **Alertmanager**: Оповещения при сбоях

## Инструкция по запуску

### Предварительные требования

- Docker и Docker Compose
- Python 3.9+
- OpenSSL и keytool (для генерации сертификатов)

### 1. Подготовка сертификатов и конфигурации

Если сертификаты еще не сгенерированы:

```bash
./scripts/generate-certs.sh

./scripts/update-certs.sh
```


```bash
# Создаем конфигурацию JAAS
cat > kafka_creds/kafka_server_jaas.conf << 'EOF'
Client {
 org.apache.kafka.common.security.plain.PlainLoginModule required
 username="admin"
 password="admin-secret";
};

KafkaServer {
 org.apache.kafka.common.security.plain.PlainLoginModule required
 username="admin"
 password="admin-secret"
 user_admin="admin-secret"
 user_shop_api="shop-api-secret"
 user_client_api="client-api-secret"
 user_faust="faust-secret"
 user_connect="connect-secret";
};
EOF

# Создаем client.properties для административных операций
cat > kafka_creds/client.properties << 'EOF'
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
ssl.truststore.location=/etc/kafka/secrets/kafka.kafka-1.truststore.jks
ssl.truststore.password=your-password
EOF
```

### 2. Запуск инфраструктуры

```bash
# Очистка предыдущих данных (если были проблемы)
docker-compose down -v

# Запуск всех сервисов
docker-compose up -d
```

**Важно:** Дождитесь полного запуска всех сервисов (около 1-2 минут). Проверьте статус:

```bash
docker-compose ps
```

Все контейнеры должны быть в статусе "Up" или "Up (healthy)".

### 3. Проверка запуска Kafka брокеров

Убедитесь, что все брокеры успешно запустились:

```bash
# Проверка логов брокеров
docker-compose logs kafka-1 | grep "Kafka Server started"
docker-compose logs kafka-2 | grep "Kafka Server started"
docker-compose logs kafka-3 | grep "Kafka Server started"

# Проверка отсутствия ошибок
docker-compose logs kafka-1 | grep -i "error\|exception\|fatal" | tail -5
```

Если брокеры не запускаются с ошибками о метаданных, выполните:

```bash
docker-compose down -v
docker-compose up -d
```

### 4. Настройка ACL для Kafka Connect

Kafka Connect требует специальных прав доступа:

```bash
chmod +x scripts/setup-connect-acls.sh
./scripts/setup-connect-acls.sh
```

### 5.1 Проверка работоспособности Kafka Connect

```bash
# Проверка статуса контейнера
docker-compose ps kafka-connect

# Проверка логов на ошибки
docker-compose logs kafka-connect | grep -i "error\|exception\|fatal" | tail -5

# Проверка доступности REST API
curl -s http://localhost:8083/connector-plugins | head -20
```

Kafka Connect должен быть в статусе "healthy" и REST API должен отвечать.

### 6.1 Настройка топиков и ACL

```bash
# Создание топиков
./scripts/setup-topics.sh
```

### 6.2 Запуск коннекторов

```bash
# Запуск коннекторов
./scripts/setup-connect.sh
```

### 6.3 Проверка работоспособности коннектора для записи в файл

```bash
# Проверка статуса коннектора
curl http://localhost:8083/connectors/file-sink-connector/status | jq

# Тестовое сообщение -> /data/filtered-products.txt
docker-compose exec kafka-1 bash \
  -c 'printf "{\"product_id\": \"12345\", \"name\": \"Умные часы XYZ\"}\n" \
  | kafka-console-producer --bootstrap-server kafka-1:1092 \
  --producer.config /etc/kafka/secrets/client.properties \
  --topic filtered-products'
```

### 7. Проверка работоспособности всех сервисов

#### Kafka UI
```bash
# Откройте в браузере
open http://localhost:8080
# или
curl -s http://localhost:8080 | head -10
```

#### Prometheus
```bash
# Проверка доступности
curl -s http://localhost:9090/-/healthy
```

#### Grafana
```bash
# Откройте в браузере
open http://localhost:3000
# Логин: admin, Пароль: kafka
```

#### Alertmanager
```bash
# Проверка доступности
curl -s http://localhost:9093/-/healthy
```

### 8. Запуск SHOP API

```bash
python3 ./shop_api/shop_producer.py
```


### 9. Управление запрещенными товарами

```bash
# Добавить товар в список запрещенных
python3 filter_app/scripts/manage_banned.py add 12345

# Удалить товар из списка запрещенных
python3 filter_app/scripts/manage_banned.py remove 12345

```

### 10. Использование CLIENT API

```bash
# Поиск товара
python3 client_api/client_api.py search "Умные часы"

# Получение рекомендаций
python3 client_api/client_api.py recommendations user123
```

### Проверка безопасности


Проверка TLS соединений. Все соединения должны использовать SASL_SSL
```bash
docker-compose logs kafka-1 | grep "SASL_SSL"
```
Проверка ACL. <br>
Попробуйте подключиться без правильных учетных данных. Должна быть ошибка авторизации


### Устранение проблем

Если какой-то сервис не запускается:

```bash
# Просмотр детальных логов
docker-compose logs <service-name>

# Перезапуск сервиса
docker-compose restart <service-name>

# Полная перезагрузка с очисткой данных
docker-compose down -v
docker-compose up -d

# Проверка сетевых подключений
docker network inspect marketplace_network
```


## Используемые технологии

- **Apache Kafka**: Брокер сообщений с поддержкой KRaft
- **TLS/SSL**: Шифрование соединений
- **SASL/PLAIN**: Аутентификация
- **ACL**: Управление доступом к топикам
- **Faust**: Потоковая обработка данных
- **Kafka Connect**: Интеграция с внешними системами
- **Prometheus**: Сбор метрик
- **Grafana**: Визуализация метрик
- **Alertmanager**: Управление алертами

## Реализация

### Безопасность

- Все соединения с Kafka защищены TLS
- Используется SASL/PLAIN для аутентификации
- Настроены ACL для ограничения доступа к топикам

### Отказоустойчивость

- Кластер Kafka состоит из 3 брокеров
- Репликация данных: replication-factor=3, min.insync.replicas=2
- Второй кластер для дублирования данных

### Фильтрация товаров

- Faust приложение читает товары из топика `shop-products`
- Проверяет товары на наличие в списке запрещенных
- Отфильтрованные товары отправляются в топик `filtered-products`

### Мониторинг

- Prometheus собирает метрики через JMX Exporter
- Grafana визуализирует метрики Kafka
- Alertmanager отправляет оповещения при падении брокера

## Доступ к сервисам

- **Kafka UI**: http://localhost:8080
- **Grafana**: http://localhost:3001 (admin/kafka)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
