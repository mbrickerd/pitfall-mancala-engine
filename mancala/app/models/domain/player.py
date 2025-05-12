from pydantic.dataclasses import dataclass

from mancala.app.models.domain.enum import PlayerTypeEnum


@dataclass
class Player:
    name: str
    type: PlayerTypeEnum