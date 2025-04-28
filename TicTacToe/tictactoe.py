
class GameBoard():
    def __init__(self):
        self.matrix = [[0 for _ in range(3)] for _ in range(3)]
        self.char_mapping = {-1: 'O', 0: ' ', 1: 'X'}

    def display(self):
        print('   1   2   3')
        for idx, row in enumerate(self.matrix):
            print(f'{idx + 1}  {" | ".join(self.char_mapping[i] for i in row)}')
            if idx < len(self.matrix) - 1:
                print('  ---+---+---')
        print()

    def place_mark(self, row, col, mark):
        if self.matrix[row][col] == 0: 
            self.matrix[row][col] = mark
            return True # success
        else:
            return False # fail

    def check_lines(self):
        lines = [                      # all winning lines
            [(0, 0), (0, 1), (0, 2)],  # Row 1
            [(1, 0), (1, 1), (1, 2)],  # Row 2
            [(2, 0), (2, 1), (2, 2)],  # Row 3
            [(0, 0), (1, 0), (2, 0)],  # Column 1
            [(0, 1), (1, 1), (2, 1)],  # Column 2
            [(0, 2), (1, 2), (2, 2)],  # Column 3
            [(0, 0), (1, 1), (2, 2)],  # Diagonal 1
            [(0, 2), (1, 1), (2, 0)]   # Diagonal 2
        ]
        
        # Check if any line has all the same, non-zero values
        for line in lines:
            values = [self.matrix[r][c] for r, c in line]
            if values[0] != 0 and values[0] == values[1] == values[2]:
                return True  # Somebody won
        return False  # Nobody won yet

class Game():
    def __init__(self):
        self.game_board = GameBoard()
        self.is_running = True
        self.mark_turn = True
        
        player_mark = None
        while player_mark not in ['X', 'O']:
            player_mark = input('Play as X or O?: ').upper()

        if player_mark == 'X':
            self.is_player_turn = True
            self.bot = Bot(False)
        
        elif player_mark == 'O':
            self.is_player_turn = False
            self.bot = Bot(True)
        

    def get_valid_int(self, prompt):
        while True:
            i = input(prompt)
            if i.isdigit():
                i = int(i)
                if 1 <= i <= 3:
                    return i-1
            print('Invalid input')

    def loop(self):
        moves = 0
        while self.is_running:
            
            self.game_board.display()
            
            if self.is_player_turn:
                print(f'Player\'s Turn ({"X" if self.mark_turn else "O"})')                
                col = self.get_valid_int('col: ')
                row = self.get_valid_int('row: ')
                
                if self.game_board.place_mark(row, col, (1 if self.mark_turn else -1)):
                    moves += 1
                    self.mark_turn = not self.mark_turn
                    self.is_player_turn = not self.is_player_turn
                    
                else:
                    print('Spot Taken')
            
            else:
                print(f'Bot\'s Turn ({"X" if self.mark_turn else "O"})')
                row, col = self.bot.choose_move(self.game_board.matrix)
                self.game_board.place_mark(row, col, (1 if self.mark_turn else -1))
                moves += 1
                self.mark_turn = not self.mark_turn
                self.is_player_turn = not self.is_player_turn

            if self.game_board.check_lines():
                self.game_board.display()
                if self.is_player_turn:
                    print(f'Bot Wins ({"X" if not self.mark_turn else "O"})')
                else:
                    print(f'Player Wins ({"X" if not self.mark_turn else "O"})')
                    
                self.is_running = False
                
                
            elif moves >= 9:
                self.game_board.display()
                print('Tied')
                self.is_running = False

class Bot:
    def __init__(self, is_x):
        self.symbol = 1 if is_x else -1

    def choose_move(self, board):
        best_move = None
        best_value = float('-inf')

        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = self.symbol
                    move_value = self.minimax(board, 0, False)
                    board[i][j] = 0

                    if move_value > best_value:
                        best_value = move_value
                        best_move = (i, j)

        return best_move

    def minimax(self, board, depth, is_maximizing):
        
        if self.is_winner(board, self.symbol):
            return 10 - depth
        elif self.is_winner(board, self.symbol * -1):
            return depth - 10
        elif not any(0 in row for row in board):
            return 0

        if is_maximizing:
            best_value = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == 0:
                        board[i][j] = self.symbol
                        value = self.minimax(board, depth + 1, False)
                        board[i][j] = 0
                        best_value = max(best_value, value)
            return best_value
        else:
            best_value = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == 0:
                        board[i][j] = self.symbol * -1
                        value = self.minimax(board, depth + 1, True)
                        board[i][j] = 0
                        best_value = min(best_value, value)
            return best_value

    def is_winner(self, board, symbol):
        lines = [                      # all winning lines
            [(0, 0), (0, 1), (0, 2)],  # Row 1
            [(1, 0), (1, 1), (1, 2)],  # Row 2
            [(2, 0), (2, 1), (2, 2)],  # Row 3
            [(0, 0), (1, 0), (2, 0)],  # Column 1
            [(0, 1), (1, 1), (2, 1)],  # Column 2
            [(0, 2), (1, 2), (2, 2)],  # Column 3
            [(0, 0), (1, 1), (2, 2)],  # Diagonal 1
            [(0, 2), (1, 1), (2, 0)]   # Diagonal 2
        ]
        
        for line in lines:
            if all(board[i][j] == symbol for i, j in line):
                return True
        return False
        
        

if __name__ == '__main__':
    game = Game()
    game.loop()
