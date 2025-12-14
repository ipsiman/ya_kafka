#!/bin/bash

CONNECT_URL="http://localhost:8083"

# Создание коннектора для записи в файл
curl -s -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "file-sink-connector",
    "config": {
      "connector.class": "FileStreamSink",
      "tasks.max": "1",
      "topics": "filtered-products",
      "file": "/data/filtered-products.txt",
      "key.converter": "org.apache.kafka.connect.storage.StringConverter",
      "value.converter": "org.apache.kafka.connect.storage.StringConverter",
      "consumer.override.security.protocol": "SASL_SSL",
      "consumer.override.sasl.mechanism": "PLAIN",
      "consumer.override.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"admin\" password=\"admin-secret\";",
      "consumer.override.ssl.truststore.location": "/etc/kafka/secrets/kafka.kafka-1.truststore.jks",
      "consumer.override.ssl.truststore.password": "your-password"
    }
  }'

echo ""
echo "Коннектор file-sink-connector создан. Проверьте статус:"
echo "curl $CONNECT_URL/connectors/file-sink-connector/status"


# Создание коннектора products -> Postgres
curl -s -X POST http://localhost:8083/connectors \
-H 'Content-Type: application/json' \
-d '{
  "name": "sink-products-pg",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "topics": "filtered-products",
    "connection.url": "jdbc:postgresql://postgres:5432/marketplace",
    "connection.user": "postgres-user",
    "connection.password": "postgres-pw",
    "auto.create": "true",
    "auto.evolve": "true",
    "insert.mode": "insert",
    "table.name.format": "products",
    "pk.mode": "record_key",
    "tasks.max": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter"
  }
}'
echo ""
echo "Коннектор sink-products-pg-connector создан. Проверьте статус:"
echo "curl $CONNECT_URL/connectors/sink-products-pg/status"


# Создание коннектора client-queries -> Postgres
curl -s -X POST http://localhost:8083/connectors \
-H 'Content-Type: application/json' \
-d '{
  "name": "sink-client-queries-pg",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "topics": "client-queries",
    "connection.url": "jdbc:postgresql://postgres:5432/marketplace",
    "connection.user": "postgres-user",
    "connection.password": "postgres-pw",
    "auto.create": "true",
    "auto.evolve": "true",
    "insert.mode": "insert",
    "table.name.format": "client-queries",
    "pk.mode": "record_key",
    "tasks.max": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter"
  }
}'
echo ""
echo "Коннектор sink-client-queries-pg-connector создан. Проверьте статус:"
echo "curl $CONNECT_URL/connectors/sink-client-queries-pg/status"
