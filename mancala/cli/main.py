import argparse
import sys
import time
import os
import platform
import random
from typing import List, Dict, Optional, Tuple

from mancala.app.models.domain.player import Player
from mancala.app.models.domain.enum import PlayerTypeEnum, GameStatusEnum
from mancala.app.services.game import GameService


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    
    @staticmethod
    def disable():
        """Disable colors for terminals that don't support ANSI"""
        Colors.RESET = ""
        Colors.BOLD = ""
        Colors.RED = ""
        Colors.GREEN = ""
        Colors.YELLOW = ""
        Colors.BLUE = ""
        Colors.MAGENTA = ""
        Colors.CYAN = ""


def print_game_title():
    """Print an ASCII art title for the game"""
    title = r"""
    __  __                            _       
   |  \/  | __ _ _ __   ___ __ _  ___| | __ _ 
   | |\/| |/ _` | '_ \ / __/ _` |/ __| |/ _` |
   | |  | | (_| | | | | (_| (_| | (__| | (_| |
   |_|  |_|\__,_|_| |_|\___\__,_|\___|_|\__,_|
                                              
    """
    print(f"{Colors.GREEN}{title}{Colors.RESET}")


def display_rules():
    """Display the rules of Mancala"""
    rules = f"""
{Colors.BOLD}HOW TO PLAY MANCALA:{Colors.RESET}

1. {Colors.CYAN}Player 1{Colors.RESET} owns the bottom row of pits and the store on the right.
   {Colors.YELLOW}Player 2{Colors.RESET} owns the top row of pits and the store on the left.

2. On your turn, select a pit number from your side of the board.

3. The stones from that pit are distributed counterclockwise, one in each pit.
   - Your own store is included in the distribution.
   - Your opponent's store is skipped.

4. Special rules:
   - If your last stone lands in your store, you get another turn.
   - If your last stone lands in an empty pit on your side, you capture that stone
     and all stones in the opponent's pit directly across.

5. The game ends when all pits on one side are empty.
   - The remaining stones go to the owner of that side.
   - The player with the most stones in their store wins.

Press Enter to start the game...
"""
    print(rules)
    input()


def clear_screen():
    """Clear the terminal screen with a better cross-platform approach"""
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        os.system('cls')
    else:  # For Linux and MacOS
        os.system('clear')
    
    # As a fallback, also use ANSI escape sequence
    print("\033[H\033[J", end="")


def print_header(title):
    """Print a formatted header"""
    print(f"{Colors.BOLD}{Colors.GREEN}== {title} =={Colors.RESET}\n")


def print_player_info(player_num, name, color):
    """Print player information"""
    print(f"Player {player_num}: {color}{name}{Colors.RESET}")


def print_turn_info(player_name, color=None):
    """Print whose turn it is with optional color"""
    if color:
        print(f"\n{Colors.BOLD}Current turn: {color}{player_name}{Colors.RESET}")
    else:
        print(f"\n{Colors.BOLD}Current turn: {player_name}{Colors.RESET}")


def print_message(message, color=Colors.GREEN):
    """Print a colored message"""
    print(f"{color}{message}{Colors.RESET}")


def calculate_pit_indices(board_arr: List[int]) -> Tuple[int, int, Dict[int, int]]:
    """Calculate pit indices based on board structure."""
    # Assuming standard mancala structure
    board_size = len(board_arr)
    pits = (board_size - 2) // 2
    p1_store = pits
    p2_store = 2 * pits + 1
    
    # Create a mapping for easier access
    # Key: display position, Value: index in board_arr
    pit_map = {}
    
    # Player 1 pits (bottom row)
    for i in range(pits):
        pit_map[i + 1] = i  # Player 1's pits are 1-6 in display
    
    # Player 2 pits (top row)
    for i in range(pits):
        pit_map[pits + i + 1] = pits + 1 + i  # Player 2's pits are 7-12 in display
    
    return pits, p1_store, p2_store


def print_board(board_arr, pits, current_player: int, last_move: Optional[int] = None):
    """Print a simplified but reliable Mancala board"""
    p1_color = Colors.CYAN
    p2_color = Colors.YELLOW
    
    # Highlight current player
    p1_highlight = Colors.BOLD if current_player == 0 else ""
    p2_highlight = Colors.BOLD if current_player == 1 else ""
    
    # Calculate indices
    p1_store = pits
    p2_store = 2 * pits + 1
    
    # Get store stone counts
    p1_store_stones = board_arr[p1_store]
    p2_store_stones = board_arr[p2_store]
    
    # Stone representation
    stones_symbol = "●"
    max_stones_display = 6  # Max stones to display (2 rows of 3)
    
    # Print the board
    print("\n")
    
    # Format for pit numbers
    print("    ", end="")
    for i in range(pits, 0, -1):
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == i and current_player == 1 else p2_highlight
        print(f"{highlight}{p2_color}[{i}]{Colors.RESET}", end="  ")
    print()
    
    # Top border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Player 2 pits - first row of stones
    print("   |", end="")
    for i in range(2*pits, pits, -1):
        stones = board_arr[i]
        pit_num = 2*pits + 1 - i
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 1 else p2_color
        
        # First row of stones (up to 3)
        first_row = min(3, stones)
        print(f"{highlight}{stones_symbol * first_row}{Colors.RESET}", end="")
        print(" " * (3 - first_row), end="|")
    print()
    
    # Player 2 pits - second row of stones
    print("   |", end="")
    for i in range(2*pits, pits, -1):
        stones = board_arr[i]
        pit_num = 2*pits + 1 - i
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 1 else p2_color
        
        # Second row of stones (if more than 3)
        second_row = min(3, max(0, stones - 3))
        print(f"{highlight}{stones_symbol * second_row}{Colors.RESET}", end="")
        print(" " * (3 - second_row), end="|")
    print()
    
    # Middle border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Stores in the middle
    print(f"[S]{p2_color}{p2_store_stones:2d}{Colors.RESET}", end="")
    print(" " * (pits * 4 - 4), end="")  # Simple calculation based on pits
    print(f"{p1_color}{p1_store_stones:2d}{Colors.RESET}[S]")
    
    # Middle border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Player 1 pits - first row of stones
    print("   |", end="")
    for i in range(pits):
        stones = board_arr[i]
        pit_num = i + 1
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 0 else p1_color
        
        # First row of stones (up to 3)
        first_row = min(3, stones)
        print(f"{highlight}{stones_symbol * first_row}{Colors.RESET}", end="")
        print(" " * (3 - first_row), end="|")
    print()
    
    # Player 1 pits - second row of stones
    print("   |", end="")
    for i in range(pits):
        stones = board_arr[i]
        pit_num = i + 1
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 0 else p1_color
        
        # Second row of stones (if more than 3)
        second_row = min(3, max(0, stones - 3))
        print(f"{highlight}{stones_symbol * second_row}{Colors.RESET}", end="")
        print(" " * (3 - second_row), end="|")
    print()
    
    # Bottom border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Format for pit numbers
    print("    ", end="")
    for i in range(1, pits+1):
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == i and current_player == 0 else p1_highlight
        print(f"{highlight}{p1_color}[{i}]{Colors.RESET}", end="  ")
    print("\n")
def print_board(board_arr, pits, current_player: int, last_move: Optional[int] = None):
    """Print a Mancala board with dynamic rows for extra stones"""
    p1_color = Colors.CYAN
    p2_color = Colors.YELLOW
    
    # Highlight current player
    p1_highlight = Colors.BOLD if current_player == 0 else ""
    p2_highlight = Colors.BOLD if current_player == 1 else ""
    
    # Calculate indices
    p1_store = pits
    p2_store = 2 * pits + 1
    
    # Get store stone counts
    p1_store_stones = board_arr[p1_store]
    p2_store_stones = board_arr[p2_store]
    
    # Stone representation
    stones_symbol = "●"
    stones_per_row = 3  # Maximum stones per row
    
    # Calculate how many rows we need for each player's pits
    p1_stones = [board_arr[i] for i in range(pits)]
    p2_stones = [board_arr[i] for i in range(pits+1, 2*pits+1)]
    
    p1_max_stones = max(p1_stones) if p1_stones else 0
    p2_max_stones = max(p2_stones) if p2_stones else 0
    
    p1_rows_needed = max(2, (p1_max_stones + stones_per_row - 1) // stones_per_row)
    p2_rows_needed = max(2, (p2_max_stones + stones_per_row - 1) // stones_per_row)
    
    print("\n")
    
    # Format for pit numbers
    print("    ", end="")
    for i in range(pits, 0, -1):
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == i and current_player == 1 else p2_highlight
        print(f"{highlight}{p2_color}[{i}]{Colors.RESET}", end="  ")
    print()
    
    # Top border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Player 2 pits - display stones in rows
    for row in range(p2_rows_needed):
        print("   |", end="")
        for i in range(2*pits, pits, -1):
            stones = board_arr[i]
            pit_num = 2*pits + 1 - i
            highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 1 else p2_color
            
            # Calculate stones for this row
            start_idx = row * stones_per_row
            end_idx = min(start_idx + stones_per_row, stones)
            stones_in_row = max(0, end_idx - start_idx)
            
            print(f"{highlight}{stones_symbol * stones_in_row}{Colors.RESET}", end="")
            print(" " * (3 - stones_in_row), end="|")
        print()
    
    # Middle border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Stores in the middle
    print(f"[S]{p2_color}{p2_store_stones:2d}{Colors.RESET}", end="")
    print(" " * (pits * 4 - 4), end="")  # Simple calculation based on pits
    print(f"{p1_color}{p1_store_stones:2d}{Colors.RESET}[S]")
    
    # Middle border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Player 1 pits - display stones in rows
    for row in range(p1_rows_needed):
        print("   |", end="")
        for i in range(pits):
            stones = board_arr[i]
            pit_num = i + 1
            highlight = Colors.MAGENTA + Colors.BOLD if last_move == pit_num and current_player == 0 else p1_color
            
            # Calculate stones for this row
            start_idx = row * stones_per_row
            end_idx = min(start_idx + stones_per_row, stones)
            stones_in_row = max(0, end_idx - start_idx)
            
            print(f"{highlight}{stones_symbol * stones_in_row}{Colors.RESET}", end="")
            print(" " * (3 - stones_in_row), end="|")
        print()
    
    # Bottom border
    print("   +", end="")
    for _ in range(pits):
        print("---+", end="")
    print()
    
    # Format for pit numbers
    print("    ", end="")
    for i in range(1, pits+1):
        highlight = Colors.MAGENTA + Colors.BOLD if last_move == i and current_player == 0 else p1_highlight
        print(f"{highlight}{p1_color}[{i}]{Colors.RESET}", end="  ")
    print("\n")
    

def display_move_animation(game_service, game_id, pit_selected, current_player, pits):
    """
    Display a simple animation of stones moving during a move
    """
    # Get board state before animation
    initial_state = game_service.get_state(game_id)
    initial_board = initial_state.board.copy()
    
    # Prepare for animation
    p1_color = Colors.CYAN
    p2_color = Colors.YELLOW
    current_color = p1_color if current_player == 0 else p2_color
    
    # Calculate the path of stones
    # For Mancala, stones move counterclockwise from the selected pit
    
    # For player 1 (bottom row), pits are 0-5 in the array, store is at index 'pits'
    # For player 2 (top row), pits are (pits+1) to (2*pits) in the array, store is at index '2*pits+1'
    
    # Convert selected pit (1-based) to board array index (0-based)
    if current_player == 0:  # Player 1
        start_idx = pit_selected - 1
    else:  # Player 2
        start_idx = pits + pit_selected
    
    # Get number of stones in the selected pit
    num_stones = initial_board[start_idx]
    
    if num_stones == 0:
        print_message("No stones to move!", Colors.RED)
        time.sleep(0.5)
        return
    
    # Display initial message
    print_message(f"\nMoving {num_stones} stones from pit {pit_selected}...", current_color)
    time.sleep(0.5)
    
    # Create a simple animation of stones moving
    # We'll simulate this by updating the board after each stone placement
    animated_board = initial_board.copy()
    animated_board[start_idx] = 0  # Remove stones from starting pit
    
    opponent_store = 2*pits + 1 if current_player == 0 else pits
    
    # Distribute stones
    current_idx = (start_idx + 1) % len(animated_board)
    stones_remaining = num_stones
    
    while stones_remaining > 0:
        # Skip opponent's store
        if current_idx == opponent_store:
            current_idx = (current_idx + 1) % len(animated_board)
            continue
        
        # Add a stone to the current pit
        animated_board[current_idx] += 1
        stones_remaining -= 1
        
        # Clear screen and show intermediate board state
        clear_screen()
        print_game_title()
        
        # Show player info and turn
        player_names = ["Player 1", "Player 2"]  # Placeholder, actual names will be shown in main loop
        print_player_info(1, player_names[0], Colors.CYAN)
        print_player_info(2, player_names[1], Colors.YELLOW)
        print_turn_info(player_names[current_player], current_color)
        
        # Highlight the current pit where we're dropping a stone
        print_board(animated_board, pits, current_player, (current_idx % (pits+1)) + 1 if current_idx < pits else None)
        
        print_message(f"Placing stone in position {current_idx}...", current_color)
        time.sleep(0.2)  # Short delay for animation effect
        
        # Move to next pit
        current_idx = (current_idx + 1) % len(animated_board)
    
    # Final message after animation
    print_message("Move completed!", current_color)
    time.sleep(0.3)


def show_help_prompt(pits):
    """Show a help prompt at the bottom of the screen"""
    print(f"\n{Colors.MAGENTA}Commands: [1-{pits}] select pit, 'h' for help, 'q' to quit{Colors.RESET}")


def process_input(prompt, pits):
    """Process user input with additional commands"""
    while True:
        user_input = input(prompt).lower().strip()
        
        if user_input == 'h':
            # Show help/rules
            display_rules()
            return 'h'  # Signal to redraw the board
        elif user_input == 'q':
            # Quit game
            if input("Are you sure you want to quit? (y/n): ").lower().startswith('y'):
                print("\nThanks for playing Mancala! Goodbye.")
                sys.exit(0)
            return 'q'  # Signal to redraw the board
        elif user_input.isdigit():
            pit = int(user_input)
            if 1 <= pit <= pits:
                return pit
            else:
                print_message(f"Invalid pit number! Must be between 1-{pits}.", Colors.RED)
        else:
            print_message(f"Invalid input! Please enter a number or command.", Colors.RED)


def display_winner(winner_idx, players, board_arr, pits):
    """Display the winner with a trophy and score information"""
    p1_store = pits
    p2_store = 2 * pits + 1
    
    if winner_idx == -1:
        print_message("\nThe game ended in a draw!", Colors.BOLD)
    else:
        winner = players[winner_idx]
        winner_color = Colors.CYAN if winner_idx == 0 else Colors.YELLOW
        trophy = """
           ___________
          '._==_==_=_.'
          .-\\:      /-.
         | (|:.     |) |
          '-|:.     |-'
            \\::.    /
             '::. .'
               ) (
             _.' '._
        """
        print(f"{winner_color}{trophy}{Colors.RESET}")
        print_message(f"Winner: {winner.name}! 🎉", winner_color + Colors.BOLD)
    
    print(f"\n{Colors.BOLD}Final score:{Colors.RESET}")
    print(f"{Colors.CYAN}{players[0].name}{Colors.RESET}: {board_arr[p1_store]}")
    print(f"{Colors.YELLOW}{players[1].name}{Colors.RESET}: {board_arr[p2_store]}")
    
    # Calculate and display statistics
    p1_pits_sum = sum(board_arr[0:pits])
    p2_pits_sum = sum(board_arr[pits+1:2*pits+1])
    print(f"\n{Colors.BOLD}Game Statistics:{Colors.RESET}")
    print(f"Stones remaining in {Colors.CYAN}{players[0].name}'s{Colors.RESET} pits: {p1_pits_sum}")
    print(f"Stones remaining in {Colors.YELLOW}{players[1].name}'s{Colors.RESET} pits: {p2_pits_sum}")
    print(f"Total stones in play: {sum(board_arr)}")


def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Play Mancala from the command line")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--stones", type=int, default=6, help="Starting stones per pit")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay for Agent moves (seconds)")
    parser.add_argument("--no-animation", action="store_true", help="Disable move animations")
    parser.add_argument("--no-clear", action="store_true", help="Disable screen clearing")
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    # Initialize game service
    game_service = GameService()
    
    # Welcome screen
    if not args.no_clear:
        clear_screen()
    
    print_game_title()  # Use our new ASCII art title
    print("\nWelcome to Mancala! Let's set up the game.\n")
    
    # Offer to show rules
    if input("Would you like to see the rules? (y/n): ").lower().startswith('y'):
        display_rules()
    
    # Create a new game
    player1_name = input(f"{Colors.CYAN}Enter Player 1 name: {Colors.RESET}")
    if not player1_name.strip():
        player1_name = "Player 1"
    
    ai_opponent = input(f"{Colors.YELLOW}Play against Agent? (y/n): {Colors.RESET}").lower().startswith('y')
    if ai_opponent:
        player2_name = "Agent"
        player2_type = PlayerTypeEnum.AGENT
        
    else:
        player2_name = input(f"{Colors.YELLOW}Enter Player 2 name: {Colors.RESET}")
        if not player2_name.strip():
            player2_name = "Player 2"
            
        player2_type = PlayerTypeEnum.HUMAN
    
    # Create players and game
    player1 = Player(name=player1_name, type=PlayerTypeEnum.HUMAN)
    player2 = Player(name=player2_name, type=player2_type)
    
    print_message("\nCreating new game...", Colors.GREEN)
    game_id = game_service.create(player1, player2)
    game_state = game_service.get_state(game_id)
    
    # Store players locally since they may not be accessible from game_state
    players = [player1, player2]
    
    # Track last move for highlighting
    last_move = None
    
    # Calculate pit information
    pits, _, _ = calculate_pit_indices(game_state.board)
    
    # If AI goes first, execute its move
    if game_state.current_player == 1 and player2_type == PlayerTypeEnum.AGENT:
        print_message("Agent is making the first move...", Colors.YELLOW)
        time.sleep(args.delay)
        game_service.execute_agent_moves(game_id)
        game_state = game_service.get_state(game_id)
    
    # Main game loop
    while game_state.status != GameStatusEnum.OVER:
        # Clear screen
        if not args.no_clear:
            clear_screen()
        
        # Print game status
        current_player_idx = game_state.current_player
        current_player = players[current_player_idx]
        current_color = Colors.CYAN if current_player_idx == 0 else Colors.YELLOW
        
        print_game_title()  # Show the title on each screen
        print_player_info(1, players[0].name, Colors.CYAN)
        print_player_info(2, players[1].name, Colors.YELLOW)
        print_turn_info(current_player.name, current_color)
        
        # Print board - using our enhanced board visualization
        board_arr = game_state.board
        print_board(board_arr, pits, current_player_idx, last_move)
        
        # Show help prompt
        show_help_prompt(pits)
        
        # Handle player turn
        if current_player.type == PlayerTypeEnum.HUMAN:
            valid_move = False
            while not valid_move:
                try:
                    # Use our enhanced input processing
                    pit = process_input(f"Enter pit number (1-{pits}) or command: ", pits)
                    
                    # If the response is a command, redraw the board and continue
                    if pit in ['h', 'q']:
                        if not args.no_clear:
                            clear_screen()
                        
                        print_game_title()
                        print_player_info(1, players[0].name, Colors.CYAN)
                        print_player_info(2, players[1].name, Colors.YELLOW)
                        print_turn_info(current_player.name, current_color)
                        print_board(board_arr, pits, current_player_idx, last_move)
                        show_help_prompt(pits)
                        continue
                    
                    # Make the move
                    result = game_service.make_move(game_id, pit)
                    valid_move = result.success
                    
                    if valid_move:
                        last_move = pit
                        
                        # Get updated state for animation
                        if not args.no_animation:
                            display_move_animation(game_service, game_id, pit, current_player_idx, pits)
                    else:
                        print_message(result.message, Colors.RED)
                        time.sleep(1)  # Give user time to read error message
                    
                except ValueError:
                    print_message("Please enter a valid number!", Colors.RED)
        else:
            # AI's turn
            print_message("Agent is thinking...", Colors.YELLOW)
            time.sleep(args.delay)
            
            # Save the pre-move state for animation if we had access to the move info
            pre_move_state = game_state
            
            # Execute the agent's move
            game_service.execute_agent_moves(game_id)
            
            # A simple "animation" for the agent's move
            if not args.no_animation:
                # Get the new state
                new_state = game_service.get_state(game_id)
                
                # Find which pit changed (simplified approach)
                for i in range(pits):
                    idx = pits + 1 + i  # Player 2's pits
                    if pre_move_state.board[idx] != new_state.board[idx] and pre_move_state.board[idx] > 0:
                        # This pit likely was the move
                        display_move_animation(game_service, game_id, i + 1, current_player_idx, pits)
                        last_move = i + 1
                        break
        
        # Update game state
        game_state = game_service.get_state(game_id)
    
    # Game over
    if not args.no_clear:
        clear_screen()
    
    print_game_title()
    print_header("GAME OVER")
    print_player_info(1, players[0].name, Colors.CYAN)
    print_player_info(2, players[1].name, Colors.YELLOW)
    
    # Print final board
    board_arr = game_state.board
    print_board(board_arr, pits, -1)  # -1 for no current player
    
    # Display winner and statistics
    display_winner(game_state.winner, players, board_arr, pits)
    
    # Ask if the user wants to play again
    if input("\nWould you like to play again? (y/n): ").lower().startswith('y'):
        main()  # Restart the game
    else:
        print("\nThanks for playing Mancala! Goodbye.")


if __name__ == "__main__":
    try:
        main()
        
    except KeyboardInterrupt:
        print("\nGame aborted. Goodbye!")
        sys.exit(0)