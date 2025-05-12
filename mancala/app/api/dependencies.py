from typing import Generator

from mancala.app.services.game import GameService


def get_game_service() -> Generator[GameService, None, None]:
    service = GameService()
    yield service
