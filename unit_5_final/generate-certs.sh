#!/bin/bash

# Создаем директории
mkdir -p ./certs ./kafka-1-creds ./kafka-2-creds ./kafka-3-creds

# Файл конфигурации для корневого сертификата (Root CA)
cat > ./certs/ca.cnf << EOF
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
EOF

# Создадим корневой сертификат (Root CA)
openssl req -new -nodes -x509 \
  -days 3650 \
  -newkey rsa:2048 \
  -keyout ./certs/ca.key \
  -out ./certs/ca.crt \
  -config ./certs/ca.cnf

#  Создадим файл для хранения сертификата безопасности
cat ./certs/ca.crt ./certs/ca.key > ./certs/ca.pem

# Файлы конфигурации для каждого брокера
cat > ./kafka-1-creds/kafka-1.cnf << EOF
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
IP.1 = 127.0.0.1
EOF

cat > ./kafka-2-creds/kafka-2.cnf << EOF
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
IP.1 = 127.0.0.1
EOF

cat > ./kafka-3-creds/kafka-3.cnf << EOF
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
IP.1 = 127.0.0.1
EOF

# Генерируем сертификаты для каждого брокера
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

  # Создаем PKCS12 хранилище
  openssl pkcs12 -export \
    -in ./kafka-$i-creds/kafka-$i.crt \
    -inkey ./kafka-$i-creds/kafka-$i.key \
    -chain \
    -CAfile ./certs/ca.pem \
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

  # Создаем truststore для Kafka
  keytool -import \
    -file ./certs/ca.crt \
    -alias ca \
    -keystore ./kafka-$i-creds/kafka.kafka-$i.truststore.jks \
    -storepass your-password \
    -noprompt

done

echo "Сертификаты успешно созданы"
