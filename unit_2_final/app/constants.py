from enum import Enum

class BlockAction(str, Enum):
    ADD = "add"
    REMOVE = "remove"

    def __str__(self) -> str:
        return self.value
