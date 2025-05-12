from fastapi import APIRouter, Depends, HTTPException, Path
from uuid import UUID

from mancala.app.models.api import GameCreate, GameState, MoveRequest, MoveResponse
from mancala.app.services.game import GameService
from mancala.app.api.dependencies import get_game_service

router = APIRouter()


@router.post("/", response_model=GameState)
async def create(
    request: GameCreate, service: GameService = Depends(get_game_service)
) -> GameState:
    id_ = service.create_game(request.player1, request.player2)

    # If player 2 is an agent and goes first, make its move
    game_state = service.get_game_state(id_)
    if game_state.current_player == 1:
        service.execute_agent_moves(id_)

    return service.get_game_state(id_)


@router.get("/{game_id}", response_model=GameState)
async def get_game(
    game_id: UUID = Path(...), service: GameService = Depends(get_game_service)
) -> GameState:
    try:
        return service.get_game_state(game_id)

    except ValueError:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found")


@router.post("/{game_id}/moves", response_model=MoveResponse)
async def make_move(
    move: MoveRequest,
    game_id: UUID = Path(...),
    service: GameService = Depends(get_game_service),
) -> MoveResponse:
    """Make a move in a game"""
    try:
        # Make the human player's move
        result = service.make_move(game_id, move.pit_index)

        # If move was successful and it's the agent's turn, make its move
        if result.success and not result.extra_turn and not result.is_game_over:
            agent_results = service.execute_agent_moves(game_id)

            # If the agent made any moves, use the last result for response
            if agent_results:
                result = agent_results[-1]

        game_state = service.get_game_state(game_id)

        return MoveResponse(
            success=result.success,
            message=result.message,
            extra_turn=result.extra_turn,
            is_game_over=result.is_game_over,
            game_state=game_state,
        )

    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
