from mancala.app.models.domain.board import Board

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = 0  # Player 1 starts
        self.game_over = False
        
    def make_move(self, pit_index: int) -> tuple[bool, str]:
        """Make a move from the selected pit"""
        # Validate move
        if self.game_over:
            return False, "Game is already over."
            
        player_pits = self.board.get_player_pits(self.current_player)
        
        if pit_index not in player_pits:
            return False, "Invalid pit selected."
            
        if self.board.get_stones(pit_index) == 0:
            return False, "Selected pit is empty."
        
        # Execute move
        stones = self.board.get_stones(pit_index)
        self.board.set_stones(pit_index, 0)
        
        current_index = pit_index
        opponent_store = self.board.get_store_index(1 - self.current_player)
        
        # Distribute stones
        while stones > 0:
            current_index = (current_index + 1) % len(self.board.board)
            # Skip opponent's store
            if current_index == opponent_store:
                continue
                
            self.board.board[current_index] += 1
            stones -= 1
        
        # Handle last stone special cases
        last_pit = current_index
        
        # Check if game is over
        if self.board.is_game_over():
            self.game_over = True
            return True, "Game over!"
        
        # Check if last stone was in player's store (get another turn)
        if last_pit == self.board.get_store_index(self.current_player):
            return True, "You get another turn!"
        
        # Check if last stone was in an empty pit on player's side
        player_pits = self.board.get_player_pits(self.current_player)
        if last_pit in player_pits and self.board.get_stones(last_pit) == 1:
            opposite_pit = self.board.get_opposite_pit_index(last_pit)
            if opposite_pit is not None and self.board.get_stones(opposite_pit) > 0:
                # Capture stones
                player_store = self.board.get_store_index(self.current_player)
                self.board.board[player_store] += self.board.get_stones(opposite_pit) + 1
                self.board.set_stones(opposite_pit, 0)
                self.board.set_stones(last_pit, 0)
                
        # Switch player
        self.current_player = 1 - self.current_player
        return True, "Move completed."