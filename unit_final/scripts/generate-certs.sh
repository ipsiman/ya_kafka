#!/bin/bash

# Создаем директории
mkdir -p ./certs ./kafka-1-creds ./kafka-2-creds ./kafka-3-creds ./kafka-secondary-1-creds ./kafka-secondary-2-creds ./kafka-secondary-3-creds ./kafka_creds

# Файл конфигурации для корневого сертификата (Root CA)
cat > ./certs/ca.cnf << EOF2
[ policy_match ]
countryName = match
stateOrProvinceName = match
organizationName = match
organizationalUnitName = optional
commonName = supplied
emailAddress = optional

[ req ]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
x509_extensions = v3_ca

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = yandex-practice-kafka-ca

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign
EOF2

# Создадим корневой сертификат (Root CA)
openssl req -new -nodes -x509 \
  -days 3650 \
  -newkey rsa:2048 \
  -keyout ./certs/ca.key \
  -out ./certs/ca.crt \
  -config ./certs/ca.cnf

#  Создадим файл для хранения сертификата безопасности
cat ./certs/ca.crt ./certs/ca.key > ./certs/ca.pem

# Файлы конфигурации для каждого брокера основного кластера
cat > ./kafka-1-creds/kafka-1.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-1

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
DNS.11 = faust-app
IP.1 = 127.0.0.1
EOF2

cat > ./kafka-2-creds/kafka-2.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-2

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
IP.1 = 127.0.0.1
EOF2

cat > ./kafka-3-creds/kafka-3.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-3

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
IP.1 = 127.0.0.1
EOF2

# Файлы конфигурации для каждого брокера вторичного кластера
cat > ./kafka-secondary-1-creds/kafka-secondary-1.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-secondary-1

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
IP.1 = 127.0.0.1
EOF2

cat > ./kafka-secondary-2-creds/kafka-secondary-2.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-secondary-2

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
IP.1 = 127.0.0.1
EOF2

cat > ./kafka-secondary-3-creds/kafka-secondary-3.cnf << EOF2
[req]
prompt = no
distinguished_name = dn
default_md = sha256
default_bits = 4096
req_extensions = v3_req

[ dn ]
countryName = RU
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = kafka-secondary-3

[ v3_ca ]
subjectKeyIdentifier = hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign

[ v3_req ]
subjectKeyIdentifier = hash
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kafka-1
DNS.2 = kafka-2
DNS.3 = kafka-3
DNS.4 = localhost
DNS.5 = kafka-controller-0
DNS.6 = kafka-controller-1
DNS.7 = kafka-ui
DNS.8 = kafka-secondary-1
DNS.9 = kafka-secondary-2
DNS.10 = kafka-secondary-3
IP.1 = 127.0.0.1
EOF2

# Генерируем сертификаты для каждого брокера основного кластера
for i in 1 2 3; do
  echo "Генерация сертификатов для kafka-$i"

  # Создаем приватный ключ и запрос на сертификат (CSR)
  openssl req -new \
      -newkey rsa:2048 \
      -keyout ./kafka-$i-creds/kafka-$i.key \
      -out ./kafka-$i-creds/kafka-$i.csr \
      -config ./kafka-$i-creds/kafka-$i.cnf \
      -nodes


  # Создаем сертификат брокера, подписанный CA
  openssl x509 -req \
    -days 3650 \
    -in ./kafka-$i-creds/kafka-$i.csr \
    -CA ./certs/ca.crt \
    -CAkey ./certs/ca.key \
    -CAcreateserial \
    -out ./kafka-$i-creds/kafka-$i.crt \
    -extfile ./kafka-$i-creds/kafka-$i.cnf \
    -extensions v3_req

  # Создаем PEM файл с цепочкой сертификатов
  cat ./kafka-$i-creds/kafka-$i.crt ./certs/ca.pem > ./kafka-$i-creds/kafka-$i-chain.pem

  # Создаем PKCS12 хранилище с цепочкой сертификатов
  openssl pkcs12 -export \
    -in ./kafka-$i-creds/kafka-$i-chain.pem \
    -inkey ./kafka-$i-creds/kafka-$i.key \
    -name kafka-$i \
    -out ./kafka-$i-creds/kafka-$i.p12 \
    -password pass:your-password

  # Создаем keystore для Kafka
  keytool -importkeystore \
    -deststorepass your-password \
    -destkeystore ./kafka-$i-creds/kafka.kafka-$i.keystore.pkcs12 \
    -srckeystore ./kafka-$i-creds/kafka-$i.p12 \
    -deststoretype PKCS12  \
    -srcstoretype PKCS12 \
    -noprompt \
    -srcstorepass your-password

  # Создаем truststore для Kafka с полной цепочкой сертификатов
  keytool -import \
    -file ./certs/ca.crt \
    -alias ca \
    -keystore ./kafka-$i-creds/kafka.kafka-$i.truststore.jks \
    -storepass your-password \
    -noprompt

done

# Генерируем сертификаты для каждого брокера вторичного кластера
for i in 1 2 3; do
  echo "Генерация сертификатов для kafka-secondary-$i"

  # Создаем приватный ключ и запрос на сертификат (CSR)
  openssl req -new \
      -newkey rsa:2048 \
      -keyout ./kafka-secondary-$i-creds/kafka-secondary-$i.key \
      -out ./kafka-secondary-$i-creds/kafka-secondary-$i.csr \
      -config ./kafka-secondary-$i-creds/kafka-secondary-$i.cnf \
      -nodes


  # Создаем сертификат брокера, подписанный CA
  openssl x509 -req \
    -days 3650 \
    -in ./kafka-secondary-$i-creds/kafka-secondary-$i.csr \
    -CA ./certs/ca.crt \
    -CAkey ./certs/ca.key \
    -CAcreateserial \
    -out ./kafka-secondary-$i-creds/kafka-secondary-$i.crt \
    -extfile ./kafka-secondary-$i-creds/kafka-secondary-$i.cnf \
    -extensions v3_req

  # Создаем PEM файл с цепочкой сертификатов
  cat ./kafka-secondary-$i-creds/kafka-secondary-$i.crt ./certs/ca.pem > ./kafka-secondary-$i-creds/kafka-secondary-$i-chain.pem

  # Создаем PKCS12 хранилище с цепочкой сертификатов
  openssl pkcs12 -export \
    -in ./kafka-secondary-$i-creds/kafka-secondary-$i-chain.pem \
    -inkey ./kafka-secondary-$i-creds/kafka-secondary-$i.key \
    -name kafka-secondary-$i \
    -out ./kafka-secondary-$i-creds/kafka-secondary-$i.p12 \
    -password pass:your-password

  # Создаем keystore для Kafka
  keytool -importkeystore \
    -deststorepass your-password \
    -destkeystore ./kafka-secondary-$i-creds/kafka.kafka-secondary-$i.keystore.pkcs12 \
    -srckeystore ./kafka-secondary-$i-creds/kafka-secondary-$i.p12 \
    -deststoretype PKCS12  \
    -srcstoretype PKCS12 \
    -noprompt \
    -srcstorepass your-password

  # Создаем truststore для Kafka с полной цепочкой сертификатов
  keytool -import \
    -file ./certs/ca.crt \
    -alias ca \
    -keystore ./kafka-secondary-$i-creds/kafka.kafka-secondary-$i.truststore.jks \
    -storepass your-password \
    -noprompt

done

# Копируем все необходимые файлы в папку kafka_creds
echo "Копирование файлов в kafka_creds..."
cp ./kafka-1-creds/kafka.kafka-1.keystore.pkcs12 ./kafka_creds/
cp ./kafka-2-creds/kafka.kafka-2.keystore.pkcs12 ./kafka_creds/
cp ./kafka-3-creds/kafka.kafka-3.keystore.pkcs12 ./kafka_creds/
cp ./kafka-secondary-1-creds/kafka.kafka-secondary-1.keystore.pkcs12 ./kafka_creds/
cp ./kafka-secondary-2-creds/kafka.kafka-secondary-2.keystore.pkcs12 ./kafka_creds/
cp ./kafka-secondary-3-creds/kafka.kafka-secondary-3.keystore.pkcs12 ./kafka_creds/
cp ./certs/ca.crt ./kafka_creds/
cp ./certs/ca.pem ./kafka_creds/


echo "Сертификаты успешно созданы для обоих кластеров"
