def tictactoe():
    ALL_SPACES = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
    X, O, BLANK = 'X', 'O', ' '

    class TicTacToeBoard:
        def __init__(self):
            """Create a new, blank tic-tac-toe board."""
            self._spaces = {}
            for space in ALL_SPACES:
                self._spaces[space] = BLANK

        def drawBoard(self):
            """Display a text-representation of the board."""
            print(f'''
    {self._spaces['1']}|{self._spaces['2']}|{self._spaces['3']} 1 2 3
    -+-+-
    {self._spaces['4']}|{self._spaces['5']}|{self._spaces['6']} 4 5 6
    -+-+-
    {self._spaces['7']}|{self._spaces['8']}|{self._spaces['9']} 7 8 9\n''')

        def isWinner(self, mark):
            """Return True if mark is a winner on this TicTacToeBoard."""
            bo, m = self._spaces, mark  
            return ((bo['1'] == m and bo['2'] == m and bo['3'] == m) or
                    (bo['4'] == m and bo['5'] == m and bo['6'] == m) or
                    (bo['7'] == m and bo['8'] == m and bo['9'] == m) or
                    (bo['1'] == m and bo['4'] == m and bo['7'] == m) or
                    (bo['2'] == m and bo['5'] == m and bo['8'] == m) or
                    (bo['3'] == m and bo['6'] == m and bo['9'] == m) or
                    (bo['3'] == m and bo['5'] == m and bo['7'] == m) or
                    (bo['1'] == m and bo['5'] == m and bo['9'] == m))

        def getPlayerMove(self, player):
            """Let the player type in their move."""
            space = None
            while space not in ALL_SPACES or not self._spaces[space] == BLANK:
                print(f'Как ходит {player}? (1-9)\n')
                space = input().upper()
            return space

        def isBoardFull(self):
            """Return True if every space on the board has been taken."""
            for space in ALL_SPACES:
                if self._spaces[space] == BLANK:
                    return False
            return True

        def setSpace(self, space, mark):
            """Sets the space on the board to mark."""
            self._spaces[space] = mark

    def main():
        """Runs a game of Tic-Tac-Toe."""
        print('Добро пожаловать в крестики-нолики!')
        gameBoard = TicTacToeBoard()
        turn, nextTurn = X, O

        while True:
            gameBoard.drawBoard()
            move = gameBoard.getPlayerMove(turn)
            gameBoard.setSpace(move, turn)
    
            if gameBoard.isWinner(turn):
                gameBoard.drawBoard()
                print(turn + ' выграл игру!\n')
                break
            elif gameBoard.isBoardFull():
                gameBoard.drawBoard()
                print('Игра заканчивается вничью!')
                break

            turn, nextTurn = nextTurn, turn
    main()
if __name__ == '__main__':
    tictactoe() 