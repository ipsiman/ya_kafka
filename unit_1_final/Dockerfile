# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запуск — будет переопределён в docker-compose
CMD ["python", "producer.py"]