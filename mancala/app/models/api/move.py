from pydantic import BaseModel, Field

from mancala.app.models.domain.enum import PlayerEnum
from mancala.app.models.api.game import GameState


class MoveRequest(BaseModel):
    pit_index: int = Field(..., gt=0, le=6, description="Pit index (1-6)")
    player: PlayerEnum | None = None


class MoveResult(BaseModel):
    success: bool
    message: str
    extra_turn: bool = False
    is_game_over: bool = False


class MoveResponse(BaseModel):
    success: bool
    message: str
    extra_turn: bool
    is_game_over: bool
    game_state: GameState
