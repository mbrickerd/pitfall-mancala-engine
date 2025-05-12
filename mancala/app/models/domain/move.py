from pydantic.dataclasses import dataclass

from datetime import datetime


@dataclass
class Move:
    pit_index: int
    player_id: int
    stones_moved: int = 0
    captured: bool = False
    captured_stones: int = 0
    extra_turn: bool = False
    timestamp: datetime = datetime.now()