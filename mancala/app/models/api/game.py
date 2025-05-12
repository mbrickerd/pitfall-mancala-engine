from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from mancala.app.models.domain.enum import GameStatusEnum, PlayerEnum, PlayerTypeEnum
from mancala.app.models.domain.move import Move


class GameCreate(BaseModel):
    player1_name: str = "Player 1"
    player2_name: str | None = None
    player2_type: PlayerTypeEnum = PlayerTypeEnum.AGENT
    
    class Config:
        json_schema_extra = {
            "example": {
                "player1_name": "Human",
                "player2_name": "Agent",
                "player2_type": "agent" 
            }
        }


class GameState(BaseModel):
    id: UUID
    board: list[int]
    current_player: int
    status: GameStatusEnum
    winner: int | None = None


class GameStatusResponse(BaseModel):
    game_id: UUID
    status: GameStatusEnum
    current_player: PlayerEnum
    winner: PlayerEnum | None = None
    player1_score: int
    player2_score: int


class GameResponse(BaseModel):
    game_id: UUID
    board: list[int]
    current_player: PlayerEnum
    status: GameStatusEnum
    moves: list[Move] = []
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "game_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "board": [6, 6, 6, 6, 6, 6, 0, 6, 6, 6, 6, 6, 6, 0],
                "current_player": "player1",
                "status": "active",
                "moves": [],
                "created_at": "2023-10-27T12:34:56.789Z"
            }
        }