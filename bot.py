from random import choice
import torch
import torch.nn as nn
import torch.nn.functional as F

import torch
import torch.nn as nn
import torch.nn.functional as F

class Bot():
    def __init__(self, color):
        self.color = color
    
    def getMove(self, board):
        moves = board.getAllMoves(board.turn, board.pieces, board.board)
        move = choice(moves)
        return move