class Board:
    def __init__(self, pits: int = 6, stones: int = 6) -> None:
        self.pits = pits
        self.stones = stones
        self.board = [stones] * pits + [0] + [stones] * pits + [0]
        
    def get_player_pits(self, player_id: int) -> list[int]:
        """Get the indices of pits belonging to a player (excluding store)"""
        # First player
        if player_id == 0:
            return list(range(0, self.pits))
        
        # Second player
        else: 
            return list(range(self.pits + 1, 2 * self.pits + 1))
            
    def get_store_index(self, player_id: int) -> int:
        """Get the index of a player's store"""
        if player_id == 0:
            return self.pits
        
        else:
            return 2 * self.pits + 1
            
    def get_opposite_pit_index(self, pit_index: int) -> int | None:
        """Get the index of the pit opposite to the given pit"""
        if pit_index in self.get_player_pits(0):
            return 2 * self.pits - pit_index
        
        elif pit_index in self.get_player_pits(1):
            return 2 * self.pits - pit_index
        
        else:
            return None  # Stores don't have opposite pits
            
    def get_stones(self, pit_index: int) -> int:
        """Get the number of stones in a pit"""
        return self.board[pit_index]
    
    def set_stones(self, pit_index: int, count: int) -> None:
        """Set the number of stones in a pit"""
        self.board[pit_index] = count
    
    def is_game_over(self) -> bool:
        """Check if the game is over (one side has no stones)"""
        player1_pits = self.get_player_pits(0)
        player2_pits = self.get_player_pits(1)
        
        player1_empty = all(self.board[i] == 0 for i in player1_pits)
        player2_empty = all(self.board[i] == 0 for i in player2_pits)
        
        return player1_empty or player2_empty
    
    def _collect_remaining_stones(self) -> None:
        """Collect remaining stones into stores at game end"""
        if not self.is_game_over():
            return
            
        for player_id in [0, 1]:
            store_index = self.get_store_index(player_id)
            player_pits = self.get_player_pits(player_id)
            
            for pit in player_pits:
                self.board[store_index] += self.board[pit]
                self.board[pit] = 0
    
    def get_winner(self) -> int | None:
        """Get the winner of the game (returns None if game not over)"""
        if not self.is_game_over():
            return None
        
        # Move remaining stones to respective stores
        self._collect_remaining_stones()
        
        player1_store = self.get_store_index(0)
        player2_store = self.get_store_index(1)
        
        if self.board[player1_store] > self.board[player2_store]:
            return 0
        
        elif self.board[player2_store] > self.board[player1_store]:
            return 1
        
        else:
            return -1  # Draw