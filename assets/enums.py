from enum import Enum
from enum import auto
import platform

# Used for distinguishing between the beta testing device which is on Windows
# and the actual server which is on Linux.
# the beta testing device should use the channels and roles from the beta server
os = platform.system()


# Enum that lists channels for readability and beta testing.
class Channels(Enum):
    CHIT_CHAT = 858167284069302292
    GENERAL_CHAT = 1155085683631857724


class C4PlaceResults(Enum):
    NO_SPACE = auto()


class C4GameResults(Enum):
    WIN = auto()
    DRAW = auto()
    FORFEIT = auto()
