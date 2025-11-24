# Практическая работа 6: Настройка защищенного соединения и управление доступом в Apache Kafka

## Описание
Этот проект демонстрирует настройку безопасного кластера Apache Kafka с использованием SSL и ACL.

## Структура проекта
- `docker-compose.yml` - конфигурация кластера
- `kafka_creds/` - сертификаты и файлы конфигурации
- `producer.py` - продюсер для отправки сообщений
- `consumer-topic1.py` - консьюмер для topic-1
- `consumer-topic2.py` - консьюмер для topic-2

## Запуск

1. Запустите кластер:
    ```bash
    docker-compose down
    docker-compose up -d
2. Настройте ACL:
    ```bash
    chmod +x setup-acls.sh
    ./setup-acls.sh
3. Запустите продюсера:
    ```bash
    python producer.py
4. Запустите консьюмер для topic-1:
    ```bash
    python consumer-topic1.py
5. Запустите консьюмер для topic-2:
    ```bash
    python consumer-topic2.py # должен получить ошибку доступа
6. Остановите кластер:
    ```bash
    docker-compose down
