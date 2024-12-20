from copy import deepcopy
from chessGame import Board
from time import time
from joblib import Parallel, delayed
import chess
from chess import Move

def generate_fen(board):
    # 1. Générer la partie de l'échiquier
    board_fen = ''
    for row in range(1,9):
        empty_squares = 0
        for col in range(1,9):
            if board[row][col] == None:
                empty_squares += 1
            else:
                if empty_squares > 0:
                    board_fen += str(empty_squares)
                    empty_squares = 0
                board_fen += board[row][col][0:2]
        if empty_squares > 0:
            board_fen += str(empty_squares)
        board_fen += '/'

    board_fen = board_fen[:-1]  # Retirer le dernier '/'
    
    # 5. Assembler la notation FEN
    fen = f"{board_fen}"

    return fen

nb_moves_per_position = {}


def toChessCoord(x,y):
    dico = {1:"a", 2:'b', 3:"c", 4:"d", 5:"e", 6:"f", 7:"g", 8:"h"}
    return dico[x] + str(y)

def moveToCoords(move, pieces):
    id = move[0]
    [px,py] = pieces[id[0]][id[1]][id[2]]
    return toChessCoord(px,py) + toChessCoord(move[1][0], move[1][1])

def checkMove(verif_board, move:Move):
    return verif_board.is_legal(move)


def nb_moves_position(depth, current_depth, board, verif_board):
    nb = 0
    
    moves = board.getAllMoves(board.turn, board.pieces, board.board)
    moves_Notation = []
    for move in moves:
        moves_Notation.append(Move.from_uci(moveToCoords(move, board.pieces)))

    if depth == 0 or len(moves) == 0:  #stop
        return 1
    else:
        for k,move in enumerate(moves):
            new_board = deepcopy(board)
            new_verif_board = deepcopy(verif_board)
            
            if new_verif_board.is_legal(moves_Notation[k]):
                if len(move) == 3:
                    new_board.playMove(move[0], move[1][0], move[1][1], move[2])
                else:
                    new_board.playMove(move[0], move[1][0], move[1][1])
                new_verif_board.push(moves_Notation[k])
                nb += nb_moves_position(depth-1, current_depth+1, new_board, new_verif_board)
            else:
                print(board)
                print(move)
                return "error"
    return nb

def process_move(move, board, depth, verif_board = None, move_notation = None):
    """Traite un seul mouvement dans le parcours."""
    new_board = deepcopy(board)
    if verif_board != None:
        new_verif_board = deepcopy(verif_board)
        if new_verif_board.is_legal(move_notation):
            if len(move) == 3:
                new_board.playMove(move[0], move[1][0], move[1][1], move[2])
            else:
                new_board.playMove(move[0], move[1][0], move[1][1])
            new_verif_board.push(move_notation)
            return nb_moves_position_parallel(depth - 1, new_board, new_verif_board)
        else:
            print(verif_board, flush=True)
            print(move, flush= True)
            raise ValueError("Mouvement illégal détecté")
    else:
        if len(move) == 3:
                new_board.playMove(move[0], move[1][0], move[1][1], move[2])
        else:
            new_board.playMove(move[0], move[1][0], move[1][1])
        return nb_moves_position_parallel(depth - 1, new_board, None)
        

def nb_moves_position_parallel(depth, board, verif_board=None):
    nb = 0
    moves = board.getAllMoves(board.turn, board.pieces, board.board)
    if len(moves) == 0:  # stop condition
        return 1
    elif depth == 1:    # stop condition
        return len(moves)
    
    if verif_board != None:
        moves_notation = [Move.from_uci(moveToCoords(move, board.pieces)) for move in moves]
        # Parallélisation sur les mouvements
        results = Parallel(n_jobs=-1)(
            delayed(process_move)(move, board, depth, verif_board, move_notation)
            for move, move_notation in zip(moves, moves_notation)
        )
        nb = sum(results)

    else:
        # Parallélisation sur les mouvements
        results = Parallel(n_jobs=-1)(
            delayed(process_move)(move, board, depth)
            for move in moves
        )
        nb = sum(results)

    return nb




if __name__ == "__main__":
    board = Board()
    board.reset()
    #verif_board = chess.Board()
    t0 = time()
    print("Nombre moves : ", nb_moves_position_parallel(4, board))
    dt = time() - t0
    print(dt)