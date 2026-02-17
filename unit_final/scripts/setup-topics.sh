#!/bin/bash
# Создание топиков и настройка ACL

CONTAINER="unit_final-kafka-1-1"
BOOTSTRAP="kafka-1:1092"
CONFIG="/etc/kafka/secrets/client.properties"

# Создание топиков
echo "Создание топиков..."
docker exec $CONTAINER kafka-topics --create --topic shop-products --partitions 3 --replication-factor 3 \
  --bootstrap-server $BOOTSTRAP --command-config $CONFIG --if-not-exists

docker exec $CONTAINER kafka-topics --create --topic filtered-products --partitions 3 --replication-factor 3 \
  --bootstrap-server $BOOTSTRAP --command-config $CONFIG --if-not-exists

docker exec $CONTAINER kafka-topics --create --topic client-queries --partitions 3 --replication-factor 3 \
  --bootstrap-server $BOOTSTRAP --command-config $CONFIG --if-not-exists

docker exec $CONTAINER kafka-topics --create --topic banned-products --partitions 3 --replication-factor 3 \
  --bootstrap-server $BOOTSTRAP --command-config $CONFIG --if-not-exists

docker exec $CONTAINER kafka-topics --create --topic recommendations --partitions 3 --replication-factor 3 \
  --bootstrap-server $BOOTSTRAP --command-config $CONFIG --if-not-exists

# Настройка ACL для shop-products (только shop_api может писать)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:shop_api --operation Write --topic shop-products \
  --command-config $CONFIG

# Настройка ACL для filtered-products (faust может писать, connect может читать)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Write --topic filtered-products \
  --command-config $CONFIG

docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Read --topic filtered-products \
  --group connect-group --command-config $CONFIG

# Настройка ACL для client-queries (client_api может писать)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:client_api --operation Write --topic client-queries \
  --command-config $CONFIG

# Настройка ACL для banned-products (faust может читать и писать)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Read --topic banned-products \
  --group faust-group --command-config $CONFIG

docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Write --topic banned-products \
  --command-config $CONFIG


# Настройка ACL для пользователя faust - РАСШИРЕННАЯ ВЕРСИЯ

# 1. РАЗРЕШЕНИЕ НА ЧТЕНИЕ И ЗАПИСЬ СИСТЕМНЫХ ТОПИКОВ FAUST
# Faust автоматически создает топики для внутренней координации
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation All --topic product-filter-__ \
  --command-config $CONFIG

# 2. РАЗРЕШЕНИЕ НА УПРАВЛЕНИЕ СМЕЩЕНИЯМИ ПОТРЕБИТЕЛЕЙ (Consumer Group)
# Это критически важно для работы Faust
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation All --group faust-group \
  --command-config $CONFIG

docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation All --group "product-filter*" \
  --command-config $CONFIG

# 3. РАЗРЕШЕНИЕ НА УПРАВЛЕНИЕ ТОПИКАМИ (CREATE/DESCRIBE)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Create --cluster \
  --command-config $CONFIG

docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation DescribeConfigs --topic product-filter-__ \
  --command-config $CONFIG

# 4. РАЗРЕШЕНИЕ НА ЧТЕНИЕ shop-products (ваш Faust читает этот топик)
# Это было упущено в вашей конфигурации!
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Read --topic shop-products \
  --group faust-group --command-config $CONFIG

# 5. РАЗРЕШЕНИЕ НА УПРАВЛЕНИЕ ТОПИКОМ filtered-products (опционально, если Faust будет его создавать)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Create --topic filtered-products \
  --command-config $CONFIG

# 6. РАЗРЕШЕНИЕ НА DESCRIBE ТОПИКОВ (необходимо для получения метаданных)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:faust --operation Describe --topic "*" \
  --command-config $CONFIG

echo "Расширенные ACL для пользователя faust настроены"

echo "Топики и ACL настроены"
