#!/bin/bash

# Настройка ACL для Kafka Connect
CONTAINER="unit_final-kafka-1-1"
BOOTSTRAP="kafka-1:1092"
CONFIG="/etc/kafka/secrets/client.properties"

echo "Настройка ACL для Kafka Connect..."

# Даем права на создание топиков (Cluster)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Create \
  --cluster \
  --command-config $CONFIG

# Даем права на управление топиками (Cluster)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Alter --operation Describe \
  --cluster \
  --command-config $CONFIG

# Даем права на топики connect-offset-storage
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Write --operation Read --operation Create --operation Describe \
  --topic connect-offset-storage \
  --command-config $CONFIG

# Даем права на топики connect-config-storage
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Write --operation Read --operation Create --operation Describe \
  --topic connect-config-storage \
  --command-config $CONFIG

# Даем права на топики connect-status-storage
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Write --operation Read --operation Create --operation Describe \
  --topic connect-status-storage \
  --command-config $CONFIG

# Даем права на все топики для чтения и записи (для коннекторов)
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Read --operation Write --operation Describe \
  --topic "*" \
  --command-config $CONFIG

# Даем права на consumer groups
docker exec $CONTAINER kafka-acls --bootstrap-server $BOOTSTRAP \
  --add --allow-principal User:connect --operation Read --operation Describe \
  --group "*" \
  --command-config $CONFIG

echo "ACL для Kafka Connect настроены"
