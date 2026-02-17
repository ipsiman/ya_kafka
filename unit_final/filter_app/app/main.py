import faust
import ssl
from typing import Optional, Dict, Any
from faust import SASLCredentials


CAFILE = "/etc/faust/ca.crt"
SASL_USERNAME = "faust"
SASL_PASSWORD = "faust-secret"

# Создаем SSL контекст
ssl_context = ssl.create_default_context(cafile=CAFILE)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Создаем credentials
credentials = SASLCredentials(
    ssl_context=ssl_context,
    mechanism='PLAIN',
    username=SASL_USERNAME,
    password=SASL_PASSWORD,
)

# Важно: используйте правильные настройки для топиков
app = faust.App(
    'product-filter',
    broker='kafka://kafka-1:1092',
    broker_credentials=credentials,
    autodiscover=False,
    # Эти настройки должны соответствовать кластеру
    topic_partitions=3,
    topic_replication_factor=3,
    consumer_group="faust-group",
)

# Определяем модели
class Product(faust.Record, serializer='json'):
    product_id: str
    name: str
    price: Dict[str, Any]
    category: str
    brand: str
    store_id: str
    description: Optional[str] = None

class BannedProductUpdate(faust.Record, serializer='json'):
    product_id: str
    action: str  # 'add' or 'remove'

shop_products_topic = app.topic('shop-products', value_type=Product)
banned_products_topic = app.topic('banned-products', value_type=BannedProductUpdate)
filtered_products_topic = app.topic('filtered-products', value_type=Product)

banned_products_table = app.Table(
    'banned_products',
    default=set,
    help='Список запрещенных товаров'
)

@app.agent(banned_products_topic)
async def process_banned_products(updates):
    async for update in updates:
        if update.action == 'add':
            banned_products_table[update.product_id] = True
            print(f"Товар {update.product_id} добавлен в список запрещенных")
        elif update.action == 'remove':
            banned_products_table.pop(update.product_id, None)
            print(f"Товар {update.product_id} удален из списка запрещенных")

@app.agent(shop_products_topic)
async def filter_products(products):
    async for product in products:
        if product.product_id not in banned_products_table:
            await filtered_products_topic.send(value=product)
            print(f"Товар {product.name} (ID: {product.product_id}) прошел фильтрацию")
        else:
            print(f"Товар {product.name} (ID: {product.product_id}) заблокирован")
