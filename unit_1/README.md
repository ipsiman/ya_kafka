# Kafka Кластер с KRaft и Kafka UI

Этот проект предоставляет конфигурацию Docker Compose для запуска локального **Kafka-кластера из 3 узлов**, работающего в режиме **KRaft (Kafka Raft Metadata)** без использования Zookeeper. Также подключён **Kafka UI** для удобного управления и мониторинга кластера.

---

## Архитектура

- **3 узла Kafka**: `kafka-0`, `kafka-1`, `kafka-2`
  - Все узлы работают как **брокеры и контроллеры**
  - Работают в режиме KRaft (`KAFKA_ENABLE_KRAFT=yes`)
- **Kafka UI**: Веб-интерфейс для просмотра состояния кластера, топиков, потребителей и метрик
- **Сеть**: Общий Docker network `kafka-net` для связи между контейнерами
- **Данные**: Сохраняются в отдельных томах (`kafka_0_data`, `kafka_1_data`, `kafka_2_data`)

---

## Как развернуть проект

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-репо/kafka-cluster.git
   cd kafka-cluster
   ```

2. Запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

3. Подождите несколько секунд, пока сервисы инициализируются.

---

## Проверка работы

### Посмотрите статус контейнеров:
```bash
docker ps
```

Вы должны увидеть следующие контейнеры:
- `kafka-0`, `kafka-1`, `kafka-2` — узлы Kafka
- `ui` — интерфейс Kafka UI

### Проверьте логи на наличие ошибок:
```bash
docker logs kafka-0
docker logs kafka-1
docker logs kafka-2
```

Если всё хорошо — ошибок быть не должно.

### Откройте Kafka UI:
Перейдите по адресу:  
🔗 [http://localhost:8080](http://localhost:8080)

Убедитесь, что кластер `kraft` отображается и доступен.

---

## Конфигурация Kafka

| Параметр | Описание |
|----------|----------|
| `KAFKA_CFG_NODE_ID` | Уникальный ID узла (0, 1, 2) |
| `KAFKA_CFG_PROCESS_ROLES` | Роли узла: `broker,controller` |
| `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS` | Список голосующих контроллеров |
| `KAFKA_CFG_LISTENERS` | Слушатели: `PLAINTEXT://:9092`, `CONTROLLER://:9093` |
| `KAFKA_CFG_ADVERTISED_LISTENERS` | Адреса для внешних клиентов |
| `KAFKA_CFG_CONTROLLER_LISTENER_NAMES` | Имя слушателя для контроллера |
| `KAFKA_KRAFT_CLUSTER_ID` | Уникальный ID кластера (UUID) |
| `ALLOW_PLAINTEXT_LISTENER` | Разрешает использование незащищённого протокола |
| `KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP` | Маппинг протоколов и слушателей |

---

## Как использовать Kafka UI

1. Перейдите по адресу:  
   [http://localhost:8080](http://localhost:8080)

2. Нажмите на кластер `kraft`.

3. Вы можете:
   - Создавать и управлять топиками
   - Просматривать список производителей и потребителей
   - Следить за метриками брокеров и топиков

---

## Остановка и удаление кластера

Остановите контейнеры:
```bash
docker-compose down
```

Чтобы удалить данные (тома):
```bash
docker-compose down -v
```
