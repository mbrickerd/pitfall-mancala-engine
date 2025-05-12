from mancala.app.models.domain.game import Game


class Agent:
    def choose_move(self, game: Game) -> int | None:
        """Choose a move based on strategic evaluation"""
        player_pits = game.board.get_player_pits(game.current_player)
        valid_moves = [pit for pit in player_pits if game.board.get_stones(pit) > 0]

        if not valid_moves:
            return None

        # Strategy 1: Try to get another turn by ending in store
        for pit in valid_moves:
            stones = game.board.get_stones(pit)
            if (pit + stones) % len(game.board.board) == game.board.get_store_index(
                game.current_player
            ):
                return pit

        # Strategy 2: Try to capture opponent's stones
        for pit in valid_moves:
            stones = game.board.get_stones(pit)
            last_pit = (pit + stones) % len(game.board.board)
            player_pits = game.board.get_player_pits(game.current_player)
            if last_pit in player_pits and game.board.get_stones(last_pit) == 0:
                opposite_pit = game.board.get_opposite_pit_index(last_pit)
                if opposite_pit is not None and game.board.get_stones(opposite_pit) > 0:
                    return pit

        # Strategy 3: Prefer pits with more stones
        return max(valid_moves, key=lambda pit: game.board.get_stones(pit))
