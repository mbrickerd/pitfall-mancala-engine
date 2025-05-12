from pydantic import BaseModel

from mancala.app.models.domain.enum import PlayerTypeEnum


class PlayerCreate(BaseModel):
    name: str
    type: PlayerTypeEnum = PlayerTypeEnum.HUMAN


class PlayerInfo(BaseModel):
    id: str
    name: str
    type: PlayerTypeEnum
