from enum import Enum, auto

class PlayerTypeEnum(str, Enum):
    HUMAN = auto()
    AGENT = auto()


class PlayerEnum(str, Enum):
    PLAYER1 = "player1"
    PLAYER2 = "player2"


class GameStatusEnum(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    OVER = "over"