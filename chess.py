import pygame
import sys
from math import floor
pygame.init()

# Parameters
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
IMG_FACTOR = 0.65
SQUARE_SIZE = WIDTH // COLS
PIECES_SIZE = pygame.image.load('images/bp.png').get_width()*IMG_FACTOR
OFFSET = (SQUARE_SIZE - PIECES_SIZE)/2
FPS = 120

# Colors
WHITE = (235, 235, 235)
BLACK = (0, 0, 0)
BROWN = (150, 77, 34)

# Window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu d'Échecs")

def add_vect(u,v):
    return (u[0]+v[0], u[1]+v[1])

def isInBoard(vect):
    return(vect[0]>0 and vect[0]<9 and vect[1]>0 and vect[1]<9)

def board_copy(board):
    new_board = []
    for elt in board:
        new_board.append(Piece(elt.color, elt.type, elt.x, elt.y))
    return new_board

def toChessCoord(x,y = None):
    dico = {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}
    if y == None:
        return dico[x]
    return dico[x]+str(y)


class Piece():
    def __init__(self, color, type, x, y):
        self.color = color
        self.type = type
        self.x = x
        self.y = y
        self.coord_x = self.get_coords(x,y)[0]
        self.coord_y = self.get_coords(x,y)[1]
        self.surname = self.color + self.type
        self.image = None

    def get_coords(self, x, y):
        """returns the coordinates given the position"""
        return ((x-1)*SQUARE_SIZE, (8-y)*SQUARE_SIZE)
    def is_equal(self, piece2):
        return self.surname == piece2.surname and self.x == piece2.x and self.y == piece2.y

class Board():
    def __init__(self):
        self.turn = 'w'   # white turn
        self.bsc = True   #castles
        self.bbc = True
        self.wsc = True
        self.wbc = True
        self.enPassant = []
        self.piece_images = {}
        self.init_board()
        self.load_pieces()
        

    def load_pieces(self):
        """initialize each piece : its position, image, type, etc."""
        
        self.white_pieces = []
        self.black_pieces = []

        #pawns
        for i in range(2):
            for j in range(1,9):
                if i == 0:
                    piece = Piece('w', 'P', j, 2)
                    self.white_pieces.append(piece)
                elif i == 1:
                    piece = Piece('b', 'P', j, 7)
                    self.black_pieces.append(piece)

        #other pieces
        pieces_array = [('w', 'R', 1, 1), ('w', 'R', 8, 1), ('w', 'N', 2, 1), ('w', 'N', 7, 1), ('w', 'B', 3, 1), ('w', 'B', 6, 1),
                        ('w', 'Q', 4, 1), ('b', 'R', 1, 8), ('b', 'R', 8, 8), ('b', 'N', 2, 8), ('b', 'N', 7, 8),
                        ('b', 'B', 3, 8), ('b', 'B', 6, 8), ('b', 'Q', 4, 8),('w', 'K', 5, 1), ('b', 'K', 5, 8)]
        for elt in pieces_array:
            if elt[0] == 'w':
                self.white_pieces.append(Piece(*elt))
            else:
                self.black_pieces.append(Piece(*elt))

        self.pieces = [*self.white_pieces, *self.black_pieces]

        # load and scale each piece's image
        for elt in self.pieces:
            self.piece_images[elt.surname] = pygame.image.load(f'images/{elt.surname}.png')
            self.piece_images[elt.surname] = pygame.transform.smoothscale(self.piece_images[elt.surname], ((self.piece_images[elt.surname]).get_width()*IMG_FACTOR, (self.piece_images[elt.surname]).get_height()*IMG_FACTOR))
            elt.image = self.piece_images[elt.surname]
        
    def changeTurn(self):
        if self.turn == 'w':
            self.turn = 'b'
        else:
            self.turn = 'w'

    def draw_board(self):
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Placer les pièces initialement
    def init_board(self):
        self.board_map = [
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["bp"] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            ["wp"] * 8,
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"]
        ]
    
    def draw_pieces(self):
        for piece in self.pieces:
            win.blit(piece.image, (piece.coord_x + OFFSET, piece.coord_y + OFFSET))

    def get_board_position(self, coord_x, coord_y):
        """returns the position of the given coordinates on the chess board (from (1,1) to (8,8))"""
        return (floor(1 + coord_x/SQUARE_SIZE), floor(9 - coord_y/SQUARE_SIZE))
    
    def get_coords(self, x, y):
        """returns the coordinates given the position"""
        return ((x-1)*SQUARE_SIZE, (8-y)*SQUARE_SIZE)
    
    def pieceMoves(self, piece, new_board = None):
        px, py, color = piece.x, piece.y, piece.color
        match piece.type:
            case 'P':
                return self.pawnMoves(px, py, color, new_board)
            case 'R':
                return self.rookMoves(px, py, color, new_board)
            case 'B':
                return self.bishopMoves(px,py,color, new_board)
            case 'N':
                return self.knightMoves(px,py,color, new_board)
            case 'K':
                return self.kingMoves(px, py, color, new_board)
            case 'Q':
                return [*self.rookMoves(px, py, color, new_board), *self.bishopMoves(px, py, color, new_board)]

    def getAllMoves(self,color, new_board = None):
        boards = {0:self.pieces, 1:new_board}
        allMoves = []
        if self.canSmallCastle(color, new_board):
            allMoves.append("O-O")
        if self.canBigCastle(color, new_board):
            allMoves.append("O-O-O") 
        for elt in self.enPassant:
            allMoves.append(elt)
        for k,piece in enumerate(boards[new_board!=None]):
            if piece.color == color:
                moves = [(k,elt) for elt in self.pieceMoves(piece, new_board) if not self.verifyForCheckWithMove(k,elt[0], elt[1], new_board)]
                allMoves += moves
        return allMoves

    def whoCanGo(self, color, x, y, type, new_board = None):
        """return the list of indexes of pieces that can go to that square"""
        allMoves = self.getAllMoves(color, new_board)
        list = []
        for elt in allMoves:
            if elt[1][0] == x and elt[1][1] == y:
                if new_board[elt[0]].type == type:
                    list.append(elt[0])
        print(list, allMoves)
        return list

    def chessNotation(self, move, old_x, old_y, color, piece_was_taken = False, promoted = False):
        """this command must be used after the move has been played"""
        opponent_color = {'w':'b', 'b':'w'}
        direction = {'b': -1, 'w': 1}

        notation = ""
        if self.isCheckmate(opponent_color[color]):
            notation+="#"
        elif self.kingInCheck(opponent_color[color], board_copy(self.pieces)):
            notation += "+"
        if move == "O-O" or move == "O-O-O":    #castle
            return move + notation
        if type(move[0]) != int:    #en passant
            return toChessCoord(move[0][0])+"x"+toChessCoord(move[0][0]+move[1], move[0][1] + direction[color]) + notation      #exf6
        
        else:   #cas classique
            if promoted:     #is promoting pawn
                notation = "=Q"+notation
            piece = self.pieces[move[0]]
            piece_type = piece.type
            new_coord = toChessCoord(move[1][0], move[1][1])
            new_board = board_copy(self.pieces)
            new_board[move[0]].x = old_x
            new_board[move[0]].y = old_y
            if piece_was_taken:
                new_board.append(Piece(opponent_color[color], 'P', move[1][0], move[1][1]))

            if len(self.whoCanGo(color, move[1][0], move[1][1], piece_type, new_board)) == 1:
                if piece_was_taken:
                        notation = piece.type + 'x' + new_coord + notation
                else:
                    notation = piece.type + new_coord + notation
            else:
                #there is 2 different pieces of the same type that could have went there
                None
        notation = notation.replace('P', '')
        if notation[0] == 'x':
            notation = toChessCoord(old_x) + notation
        if "=" in notation and "x" in notation:
            notation = toChessCoord(old_x) + notation[1:]
        return notation

    def isCheckmate(self, color, newBoard = None):
        """verify is the color given is checkmated, i.e it does not have any moves and is in check"""
        boards = {0:self.pieces, 1:newBoard}
        return self.getAllMoves(color) == [] and self.kingInCheck(color, boards[newBoard != None])

    def isStalemate(self, color, newBoard = None):
        """verify is the color given got stalemate, i.e it does not have any moves but is not in check"""
        boards = {0:self.pieces, 1:newBoard}
        return self.getAllMoves(color) == [] and not self.kingInCheck(color, boards[newBoard != None])

    def isEmptySquare(self, square, other_pieces = None):
        """0 = empty square, else piece.color"""
        if other_pieces == None:
            for piece in self.pieces:
                if (piece.x, piece.y) == square:
                    return piece.color
        else:
            for piece in other_pieces:
                if (piece.x, piece.y) == square:
                    return piece.color
        return 0

    def capture(self, indice_piece):
        color = self.pieces[indice_piece].color
        self.pieces.pop(indice_piece)
        if color == 'w':
            self.white_pieces.pop(indice_piece)
        else:
            self.black_pieces.pop(indice_piece-len(self.white_pieces))
    
    def getPieceIndexes(self, x, y):
        loc_index, glob_index = 0,0
        for k,piece in enumerate(self.pieces):
            if (piece.x, piece.y) == (x,y):
                glob_index = k
                loc_index = k
                if piece.color == 'b':
                    loc_index -= len(self.white_pieces)
                return (glob_index, loc_index)
        return (-1,-1)

    def bishopMoves(self, x, y, color, other_pieces = None):
        positions = []
        trajectories = [(1,1), (-1,-1), (1,-1), (-1,1)]
        for traj in trajectories:
            k = 1
            pos = add_vect((x,y),(k*traj[0], k*traj[1]))
            empty_square = self.isEmptySquare(pos, other_pieces)
            while isInBoard(pos) and empty_square == 0:
                positions.append(pos)
                k+=1
                pos = add_vect((x,y),(k*traj[0], k*traj[1]))
                empty_square = self.isEmptySquare(pos, other_pieces)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions
    
    def rookMoves(self, x, y, color, other_pieces = None):
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1)]
        for traj in trajectories:
            k = 1
            pos = add_vect((x,y),(k*traj[0], k*traj[1]))
            empty_square = self.isEmptySquare(pos, other_pieces)
            while isInBoard(pos) and empty_square == 0:
                positions.append(pos)
                k+=1
                pos = add_vect((x,y),(k*traj[0], k*traj[1]))
                empty_square = self.isEmptySquare(pos, other_pieces)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions
                
    def kingMoves(self, x, y, color, other_pieces = None):
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1), (1,1), (-1,-1), (1,-1), (-1,1)]
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            empty_square = self.isEmptySquare(pos, other_pieces)
            if empty_square == 0 and isInBoard(pos):
                positions.append(pos)
            elif isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions
                
    def knightMoves(self, x, y, color, other_pieces = None):
        positions = []
        trajectories = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-2,-1), (-1,2), (-1,-2)]
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            empty_square = self.isEmptySquare(pos, other_pieces)
            if empty_square == 0 and isInBoard(pos):
                positions.append(pos)
            elif isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions

    def pawnMoves(self, x, y, color, other_pieces = None):
        positions = []
        trajectories = []
        match color:
            case "w":
                trajectories.append((0,1))
                for elt in [-1,1]:
                    if y<=7 and self.isEmptySquare((x+elt,y+1), other_pieces) == "b":
                        trajectories.append((elt, 1))
                if y == 2:  #first move
                    trajectories.append((0,2))
            case 'b':
                trajectories.append((0,-1))
                for elt in [-1,1]:
                    if y >=2 and self.isEmptySquare((x+elt,y-1), other_pieces) == "w":
                        trajectories.append((elt, -1))
                if y == 7:
                    trajectories.append((0,-2))
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            empty_square = self.isEmptySquare(pos, other_pieces)
            if isInBoard(pos) and empty_square == 0:
                positions.append(pos)
            elif empty_square != color: #there is an opponent piece
                if traj[0] != 0:    #if its on the side
                    positions.append(pos)
        return positions

    def pieceCanGo(self, piece, x, y):
        color = piece.color
        match piece.type:
            case 'P':
                return (x,y) in self.pawnMoves(piece.x, piece.y, color)
            case 'R':
                return (x,y) in self.rookMoves(piece.x, piece.y, color)
            case 'B':
                return (x,y) in self.bishopMoves(piece.x,piece.y,color)
            case 'N':
                return (x,y) in self.knightMoves(piece.x,piece.y,color)
            case 'K':
                return (x,y) in self.kingMoves(piece.x, piece.y, color)
            case 'Q':
                return (x,y) in [*self.rookMoves(piece.x, piece.y, color), *self.bishopMoves(piece.x, piece.y, color)]
        return False

    def canSmallCastle(self, color, new_board = None):
        boards = {0:self.pieces, 1:new_board}
        dico = {"wHasNotMoved":self.wsc, "bHasNotMoved":self.bsc, "w":1, "b":8}
        check = self.kingInCheck(color, self.pieces)
        if (not check) and dico[color+"HasNotMoved"] and self.isEmptySquare((6,dico[color])) == 0 and self.isEmptySquare((7,dico[color])) == 0:
            k_index = self.kingIndex(color)
            potBoard1 = board_copy(boards[new_board != None])
            potBoard1[k_index].x = 6
            potBoard2 = board_copy(boards[new_board != None])
            potBoard2[k_index].x = 7
            if (not self.kingInCheck(color, potBoard1)) and (not self.kingInCheck(color, potBoard2)):
                return True
        return False

    def canBigCastle(self, color, new_board = None):
        boards = {0:self.pieces, 1:new_board}
        dico = {"wHasNotMoved":self.wbc, "bHasNotMoved":self.bbc, "w":1, "b":8}
        check = self.kingInCheck(color, self.pieces)
        if (not check) and dico[color+"HasNotMoved"] and self.isEmptySquare((3,dico[color])) == 0 and self.isEmptySquare((4,dico[color])) == 0:
            k_index = self.kingIndex(color)
            potBoard1 = board_copy(boards[new_board != None])
            potBoard1[k_index].x = 3
            potBoard2 = board_copy(boards[new_board != None])
            potBoard2[k_index].x = 4
            if (not self.kingInCheck(color, potBoard1)) and (not self.kingInCheck(color, potBoard2)):
                return True
        return False

    def kingIndex(self, color):
        """global index"""
        for k,elt in enumerate(self.pieces):
            if elt.color == color and elt.type == 'K':
                return k
        return None

    def castle(self,color, type):
        dico = {'w':1, 'b':8, "small":(6,7), "big":(4,3), 's2':8, 'b2':1}
        rook_pos = (dico[type[0]+'2'],dico[color])
        king_pos = (5,dico[color])
        for k,piece in enumerate(self.pieces):
            if (piece.x, piece.y) == rook_pos:
                piece.x = dico[type][0]
                piece.coord_x, piece.coord_y = board.get_coords(dico[type][0], piece.y)
                if color == 'w':
                    self.white_pieces[k].x = piece.x
                    self.white_pieces[k].coord_x, self.white_pieces[k].coord_y = board.get_coords(dico[type][0], piece.y)
                else:
                    self.black_pieces[k - len(self.white_pieces)].x = piece.x
                    self.black_pieces[k - len(self.white_pieces)].coord_x, self.black_pieces[k - len(self.white_pieces)].coord_y = board.get_coords(dico[type][0], piece.y)

            elif (piece.x, piece.y) == king_pos:
                piece.x = dico[type][1]
                piece.coord_x, piece.coord_y = board.get_coords(dico[type][1], piece.y)
                if color == 'w':
                    self.white_pieces[k].x = piece.x
                    self.white_pieces[k].coord_x, self.white_pieces[k].coord_y = board.get_coords(dico[type][1], piece.y)
                else:
                    self.black_pieces[k - len(self.white_pieces)].x = piece.x
                    self.black_pieces[k - len(self.white_pieces)].coord_x, self.black_pieces[k - len(self.white_pieces)].coord_y = board.get_coords(dico[type][1], piece.y)

    def updateCastle(self, piece):
        """piece has just moved, update the possibility of castling"""
        match piece.color:
            case 'w':
                if piece.type == 'K':
                    self.wsc = False
                    self.wbc = False
                elif piece.type == 'R':
                    if piece.x == 1:
                        self.wbc = False
                    elif piece.x == 8:
                        self.wsc = False
            case 'b':
                if piece.type == 'K':
                    self.bsc = False
                    self.bbc = False
                elif piece.type == 'R':
                    if piece.x == 1:
                        self.bbc = False
                    elif piece.x == 8:
                        self.bsc = False

    def triesToCastle(self, piece, x, y):
        return piece.type == 'K' and piece.x == 5 and ((piece.y == 1 and y == 1) or (piece.y == 8 and y == 8)) and (x == piece.x + 2 or x == piece.x - 2)

    def canEnPassant(self, piece, x, y):
        """update after each move the list of pawns that can en passant (the piece is moving to x, y)"""
        possible = []
        if piece.type == 'P':
            color = piece.color
            dico = {'w':(2,1), 'b':(7,-1)}
            if piece.y == dico[color][0] and y == piece.y + 2*dico[color][1]:
                #we need to look for potential pawns
                square1 = self.isEmptySquare((x-1, y))
                square2 = self.isEmptySquare((x+1, y))
                if square1 != 0 and square1 != color:
                    index1 = self.getPieceIndexes(x-1, y)[0]
                    piece1 = self.pieces[index1]
                    if piece1.type == 'P':
                        possible.append([(piece1.x, piece1.y),1])
                if square2 != 0 and square2 != color:
                    index2 = self.getPieceIndexes(x+1, y)[0]
                    piece2 = self.pieces[index2]
                    if piece2.type == 'P':
                        possible.append([(piece2.x, piece2.y),-1])
        self.enPassant = possible    

    def doEnPassant(self, x, y, color):
        """eat the pawn that is supposed to be eaten"""
        dico = {'w':-1, 'b':1}
        coord = (x, y + dico[color])
        index = self.getPieceIndexes(coord[0], coord[1])
        piece = self.pieces[index[0]]
        pcolor = piece.color
        self.pieces.pop(index[0])
        if pcolor == 'w': self.white_pieces.pop(index[1])
        else: self.black_pieces.pop(index[1])

    def isUppingPawn(self, piece):
        return (piece.color == 'b' and piece.y == 1) or (piece.color == 'w' and piece.y == 8)

    def upThePawn(self, glob_index, loc_index):
        piece = self.pieces[glob_index]
        self.pieces[glob_index].type = 'Q'
        self.pieces[glob_index].surname = piece.color + 'Q'
        self.pieces[glob_index].image = pygame.image.load(f'images/{piece.surname}.png')
        self.pieces[glob_index].image = pygame.transform.smoothscale(self.pieces[glob_index].image, ((self.pieces[glob_index].image).get_width()*IMG_FACTOR, (self.pieces[glob_index].image).get_height()*IMG_FACTOR))
        if piece.color == 'b':
            self.black_pieces[loc_index].type = 'Q'
            self.black_pieces[loc_index].surname = piece.color + 'Q'
            self.black_pieces[loc_index].image = self.pieces[glob_index].image
        else:
            self.white_pieces[loc_index].type = 'Q'
            self.white_pieces[loc_index].surname = piece.color + 'Q'
            self.white_pieces[loc_index].image = self.pieces[glob_index].image
    def isLegalMove(self, piece_index, x, y):
        """checks if the move piece to (x,y) is a legal move"""
        piece = self.pieces[piece_index]
        if [(piece.x, piece.y),x-piece.x] in self.enPassant:
            self.doEnPassant(x,y, piece.color)
            return True
        if piece.type == 'K':
            if self.triesToCastle(piece, x, y):   #maybe tries to castle:
                if x == 7:
                    return self.canSmallCastle(piece.color)
                elif x == 3:
                    return self.canBigCastle(piece.color)

        return (not self.verifyForCheckWithMove(piece_index, x, y)) and self.pieceCanGo(piece, x, y)

    def verifyForCheckWithMove(self, piece_index, x, y, new_board2 = None):
        """verifies if moving the piece in (x,y) puts you in check"""
        boards = {0:self.pieces, 1:new_board2}
        piece = boards[new_board2 != None][piece_index]
        new_board = board_copy(boards[new_board2 != None])
        glob_index, loc_index = self.getPieceIndexes(x, y)    #we will look if there is a piece there
        if glob_index != -1:
            if self.pieceCanGo(piece, x, y):    #if we can go there, we look at what will happen if we take it
                new_board.pop(glob_index)
                if glob_index < piece_index:
                    piece_index -= 1
        new_board[piece_index].x = x
        new_board[piece_index].y = y
        return self.kingInCheck(piece.color, new_board)    #we look if we are in check by doing this move

    def kingInCheck(self, color, new_board):
        """verifies if the 'color' king is in check or not on the board 'new_board' """
        k_index = -1
        k = 0
        while k_index == -1:
            piece = new_board[k]
            if piece.surname == color + 'K': k_index = k
            else : k+=1
        king_x, king_y = new_board[k_index].x, new_board[k_index].y
        for piece in new_board :
            if piece.color != color:
                px, py = piece.x, piece.y
                match piece.type :
                    case 'P':
                        if (king_x, king_y) in self.pawnMoves(px, py, piece.color, new_board) and (king_x != px):   #only pawn attack moves
                            return True
                    case 'Q':
                        if (king_x, king_y) in self.rookMoves(px, py, piece.color, new_board) or (king_x, king_y) in self.bishopMoves(px, py, piece.color, new_board):
                            return True
                    case 'R':
                        if (king_x, king_y) in self.rookMoves(px, py, piece.color, new_board):
                            return True
                    case 'B':
                        if (king_x, king_y) in self.bishopMoves(px, py, piece.color, new_board):
                            return True
                    case 'N':
                        if (king_x, king_y) in self.knightMoves(px, py, piece.color, new_board):
                            return True
                    case 'K':
                        if (king_x, king_y) in self.kingMoves(px, py, piece.color, new_board):
                            return True
        return False

board = Board()

# Fonction principale
def main():
    clock = pygame.time.Clock()
    moving_piece = None
    dragging = False
    running = True
    board.draw_board()
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():    # EVENTS

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:    # Check if we click on a piece

                mouse_x, mouse_y = pygame.mouse.get_pos()
                pos_x, pos_y = board.get_board_position(mouse_x, mouse_y)
                for k, piece in enumerate(board.pieces):
                    if piece.x == pos_x and piece.y == pos_y:
                        dragging = True
                        moving_piece = k 

            elif event.type == pygame.MOUSEBUTTONUP:    # Check if we place the piece

                if moving_piece != None:
                    dragging = False
                    p = board.pieces[moving_piece]
                    new_x, new_y = board.get_board_position(p.coord_x + PIECES_SIZE/2, p.coord_y + PIECES_SIZE/2)
                    
                    if p.color == board.turn and board.isLegalMove(moving_piece, new_x, new_y):
                        pieceTaken = False
                        glob_index, loc_index = board.getPieceIndexes(new_x, new_y)
                        if glob_index != -1:    #there is an opposite piece
                            board.capture(glob_index)
                            pieceTaken = True
                        old_x, old_y = p.x, p.y
                        board.canEnPassant(p, new_x, new_y)     #update the possibility of en passant after the move
                        move = ()
                        if board.triesToCastle(p, new_x, new_y):
                            if new_x == 7:
                                board.castle(p.color, "small")
                                move = "O-O"
                            else:
                                board.castle(p.color, "big")
                                move = "O-O-O"
                        else:
                            p.x, p.y = new_x, new_y
                            print(p.type)
                            promoted = p.type == 'P' and (p.y == 1 or p.y == 8)
                            print(promoted)
                            p.coord_x, p.coord_y = board.get_coords(new_x, new_y)
                            move = (board.getPieceIndexes(new_x, new_y)[0], (new_x, new_y))

                        if board.isUppingPawn(p):
                            (glob_index, loc_index) = board.getPieceIndexes(new_x, new_y)
                            board.upThePawn(glob_index, loc_index)
                        if p.type == 'K' or p.type == 'R':
                            board.updateCastle(p)
                        board.changeTurn()
                        print(board.chessNotation(move, old_x, old_y, p.color, pieceTaken, promoted))
                        #print(board.getAllMoves(board.turn))
                        if board.isCheckmate(board.turn):
                            print("checkmate !")
                        if board.isStalemate(board.turn):
                            print("stalemate...")
                        moving_piece = None
                    else:
                        p.coord_x, p.coord_y = board.get_coords(p.x, p.y)


            elif event.type == pygame.MOUSEMOTION:    # Check if we move the piece

                if dragging:
                    p = board.pieces[moving_piece]
                    p.coord_x, p.coord_y = pygame.mouse.get_pos()
                    board.pieces[moving_piece].coord_x-=PIECES_SIZE/2
                    board.pieces[moving_piece].coord_y-=PIECES_SIZE/2
        board.draw_board()
        board.draw_pieces()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()