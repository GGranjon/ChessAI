from random import choice

class Bot():
    def __init__(self, color):
        self.color = color
    
    def getMove(self, board):
        moves = board.getAllMoves(board.turn, board.pieces, board.board)
        move = choice(moves)
        return move