from enum import Enum
from enum import auto


# Enum that lists channels for readability and beta testing.
class Channels(Enum):
    CHIT_CHAT = 858167284069302292
    GENERAL_CHAT = 1155085683631857724


class C4PlaceResults(Enum):
    SUCCESSFUL = auto()
    NO_SPACE = auto()
