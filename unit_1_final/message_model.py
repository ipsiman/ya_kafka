import json

class MessageModel:
    """
    A model class for serializing and deserializing message data.

    This class represents a message with an ID and content. It provides methods to
    serialize the message into a JSON-encoded byte string and to deserialize
    a byte string back into a MessageModel instance.

    Attributes:
        message_id (str): The unique identifier for the message.
        content (str): The content of the message.

    Methods:
        serialize: Converts the message instance into a JSON-encoded byte string.
        deserialize: Creates a MessageModel instance from a JSON-encoded byte string.
    """

    def __init__(self, message_id, content):
        self.message_id = message_id
        self.content = content

    def serialize(self):
        try:
            return json.dumps({
                "id": self.message_id,
                "content": self.content
            }).encode('utf-8')
        except Exception as e:
            print(f"[ERROR] Serialization error: {e}")
            return None

    @staticmethod
    def deserialize(data):
        try:
            decoded = data.decode('utf-8')
            loaded = json.loads(decoded)
            return MessageModel(loaded["id"], loaded["content"])
        except Exception as e:
            print(f"[ERROR] Deserialization error: {e}")
            return None
