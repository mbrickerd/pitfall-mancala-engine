from uuid import UUID, uuid4

from mancala.app.models.domain.agent import Agent
from mancala.app.models.domain.game import Game
from mancala.app.models.domain.enum import PlayerTypeEnum, GameStatusEnum
from mancala.app.models.api import GameState, MoveResult, PlayerCreate

class GameService:
    def __init__(self):
        self.games: dict[UUID, Game] = {}
        self.game_types: dict[UUID, tuple[PlayerTypeEnum, PlayerTypeEnum]] = {}
        self.agent = Agent()
    
    def create(self, player1: PlayerCreate, player2: PlayerCreate | None = None) -> UUID:
        game = Game()
        game_id = uuid4()
        self.games[game_id] = game
        
        # Store player types
        player2_type = player2.type if player2 else PlayerTypeEnum.AGENT
        self.game_types[game_id] = (player1.type, player2_type)
        
        return game_id
    
    def get(self, game_id: UUID) -> Game:
        if game_id not in self.games:
            raise ValueError(f"Game with ID {game_id} not found")
        
        return self.games[game_id]
    
    def get_state(self, game_id: UUID) -> GameState:
        game = self.get(game_id)
        winner = game.board.get_winner() if game.game_over else None
        
        return GameState(
            id=game_id,
            board=game.board.board,
            current_player=game.current_player,
            status=GameStatusEnum.OVER if game.game_over else GameStatusEnum.ACTIVE,
            winner=winner
        )
    
    def make_move(self, game_id: UUID, pit_index: int) -> MoveResult:
        game = self.get(game_id)
        
        # Convert from 1-based to 0-based index for player 1
        if game.current_player == 0:
            pit_index -= 1
        
        # For player 2, adjust the index
        else:
            pit_index = game.board.pits + pit_index
        
        success, message = game.make_move(pit_index)
        
        return MoveResult(
            success=success,
            message=message,
            extra_turn=message == "You get another turn!",
            is_game_over=game.game_over
        )
    
    def get_agent_move(self, game_id: UUID) -> int | None:
        game = self.get(game_id)
        player_types = self.game_types.get(game_id)
        
        if not player_types or player_types[game.current_player] != PlayerTypeEnum.AGENT:
            return None
            
        return self.agent.choose_move(game)
    
    def execute_agent_moves(self, game_id: UUID) -> list[MoveResult]:
        results = []
        game = self.get(game_id)
        player_types = self.game_types.get(game_id)
        
        if not player_types:
            return results
            
        # Keep making agent moves as long as it's the agent's turn
        while (
            not game.game_over 
            and player_types[game.current_player] == PlayerTypeEnum.AGENT
        ):
            agent_move = self.agent.choose_move(game)
            if agent_move is None:
                break
                
            success, message = game.make_move(agent_move)
            result = MoveResult(
                success=success,
                message=message,
                extra_turn=message == "You get another turn!",
                is_game_over=game.game_over
            )
            results.append(result)
            
            # If game ended or agent doesn't get another turn, stop
            if game.game_over or not result.extra_turn:
                break
                
        return results