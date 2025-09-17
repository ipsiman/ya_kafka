import os
import faust
from typing import Optional
from .censor import censor_text
from .constants import BlockAction


# Читаем настройки из переменных окружения
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka://localhost:9092')
APP_STORE = os.getenv('APP_STORE', 'memory://')
APP_NAME = os.getenv('APP_NAME', 'app_name')

# Создаём приложение
app = faust.App(
    id=APP_NAME,
    broker=KAFKA_BROKER,
    store=APP_STORE
)

# Модели
class Message(faust.Record, serializer='json'):
    sender: str
    recipient: str
    text: str
    timestamp: Optional[str] = None

class BlockedUsersUpdate(faust.Record, serializer='json'):
    user: str
    blocked_user: str
    action: BlockAction

# Топики (Kafka создаст их автоматически при первой записи)
messages_topic = app.topic('messages', value_type=Message)
blocked_users_topic = app.topic('blocked_users', value_type=BlockedUsersUpdate)
filtered_messages_topic = app.topic('filtered_messages', value_type=Message)

# Таблица блокировок
blocked_users_table = app.Table(
    'blocked_users',
    default=list,
    partitions=4,
    help='Список заблокированных пользователей'
)

# Агент: обработка блокировок
@app.agent(blocked_users_topic)
async def process_blocked_users(updates):
    async for update in updates:
        user = update.user
        blocked_user = update.blocked_user
        action = update.action

        current_list = set(blocked_users_table[user])

        if action == BlockAction.ADD:
            current_list.add(blocked_user)
            print(f"{user} заблокировал {blocked_user}")
        elif action == BlockAction.REMOVE:
            current_list.discard(blocked_user)
            print(f"{user} разблокировал {blocked_user}")
        else:
            print(f"Неизвестная операция {action} для {user}")
            continue

        blocked_users_table[user] = list(current_list)

# Агент: обработка сообщений
@app.agent(messages_topic)
async def process_messages(messages):
    async for message in messages:
        sender = message.sender
        recipient = message.recipient

        # Проверка блокировки
        blocked_list = set(blocked_users_table[recipient])
        if sender in blocked_list:
            print(f"Сообщение от {sender} к {recipient} отклонено (заблокирован)")
            continue

        # Применяем цензуру
        message.text = censor_text(message.text)

        # Отправляем в выходной топик
        await filtered_messages_topic.send(value=message)
        print(f"Сообщение от {sender} к {recipient} обработано: {message.text}")
