#!/bin/bash

# Создаем топики
docker exec unit_5_final-kafka-1-1 kafka-topics --create --topic topic-1 --partitions 3 --replication-factor 3 \
--bootstrap-server kafka-1:1092 --command-config /etc/kafka/secrets/client.properties

docker exec unit_5_final-kafka-1-1 kafka-topics --create --topic topic-2 --partitions 3 --replication-factor 3 \
  --bootstrap-server kafka-1:1092 --command-config /etc/kafka/secrets/client.properties

# Настраиваем ACL для topic-1 (доступ для всех)
docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:producer --operation Write --topic topic-1 \
  --command-config /etc/kafka/secrets/client.properties

docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:producer --operation Describe --topic topic-1 \
  --command-config /etc/kafka/secrets/client.properties

docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:consumer --operation Read --topic topic-1 \
  --group consumer-sasl-group \
  --command-config /etc/kafka/secrets/client.properties

docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:consumer --operation Describe --topic topic-1 \
  --group consumer-sasl-group \
  --command-config /etc/kafka/secrets/client.properties

# Настраиваем ACL для topic-2 (только запись)
docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:producer --operation Write --topic topic-2 \
  --command-config /etc/kafka/secrets/client.properties

docker exec unit_5_final-kafka-1-1 kafka-acls --bootstrap-server kafka-1:1092 \
  --add --allow-principal User:producer --operation Describe --topic topic-2 \
  --command-config /etc/kafka/secrets/client.properties
# Не добавляем права на чтение для консьюмеров, чтобы они не могли читать сообщения из topic-2

echo "ACL настроены"
