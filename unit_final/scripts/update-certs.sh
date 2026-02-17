#!/bin/bash


# Обновляем truststore для каждого брокера основного кластера
for i in 1 2 3; do
  echo "Обновление truststore для kafka-$i"

  # Добавляем сертификат брокера в truststore
  keytool -import \
    -file ./kafka-$i-creds/kafka-$i.crt \
    -alias kafka-$i \
    -keystore ./kafka-$i-creds/kafka.kafka-$i.truststore.jks \
    -storepass your-password \
    -noprompt
done

# Обновляем truststore для каждого брокера вторичного кластера
for i in 1 2 3; do
  echo "Обновление truststore для kafka-secondary-$i"

  # Добавляем сертификат брокера в truststore
  keytool -import \
    -file ./kafka-secondary-$i-creds/kafka-secondary-$i.crt \
    -alias kafka-secondary-$i \
    -keystore ./kafka-secondary-$i-creds/kafka.kafka-secondary-$i.truststore.jks \
    -storepass your-password \
    -noprompt
done

# Копируем обновленные truststore в папку kafka_creds
echo "Копирование обновленных truststore в kafka_creds..."
cp ./kafka-1-creds/kafka.kafka-1.truststore.jks ./kafka_creds/
cp ./kafka-2-creds/kafka.kafka-2.truststore.jks ./kafka_creds/
cp ./kafka-3-creds/kafka.kafka-3.truststore.jks ./kafka_creds/
cp ./kafka-secondary-1-creds/kafka.kafka-secondary-1.truststore.jks ./kafka_creds/
cp ./kafka-secondary-2-creds/kafka.kafka-secondary-2.truststore.jks ./kafka_creds/
cp ./kafka-secondary-3-creds/kafka.kafka-secondary-3.truststore.jks ./kafka_creds/

echo "Truststore успешно обновлены"