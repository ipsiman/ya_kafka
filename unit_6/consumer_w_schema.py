from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer




def user_from_dict(user, ctx):
   """
   Десериализация объекта пользователя из dict.
   """
   return user




if __name__ == "__main__":
   schema_registry_url = "http://localhost:8081"
   topic = "user"


   consumer_conf = {
       "bootstrap.servers": "localhost:9094,localhost:9095,localhost:9096",
       "group.id": "group",
       "auto.offset.reset": "earliest",
   }
   consumer = Consumer(consumer_conf)
   consumer.subscribe([topic])


   schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
   latest = schema_registry_client.get_latest_version(topic + "-value")
   json_schema_str = latest.schema.schema_str
   json_deserializer = JSONDeserializer(json_schema_str, from_dict=user_from_dict)


   try:
       while True:
           msg = consumer.poll(timeout=10)

           if msg is None:
               continue
           if msg.error():
               print(f"Error: {msg.error()}")
               break


           context = SerializationContext(msg.topic(), MessageField.VALUE)
           user = json_deserializer(msg.value(), context)
           print(f"Message on {msg.topic()}:\n{user}")
           if msg.headers():
               print(f"Headers: {msg.headers()}")
               print(f"Offset: {msg.offset()}")
   except KeyboardInterrupt as err:
       print(f"Consumer error: {err}")
   finally:
       consumer.close()
       print("Closing consumer")
