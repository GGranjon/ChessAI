from math import floor
from copy import deepcopy
from time import sleep
from random import choice
import pygame

# Parameters
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
IMG_FACTOR = 0.65
PIECES_SIZE = pygame.image.load('images/bp.png').get_width()*IMG_FACTOR
SQUARE_SIZE = WIDTH // COLS
OFFSET = (SQUARE_SIZE - PIECES_SIZE)/2


# Colors
WHITE = (235, 235, 235)
BLACK = (0, 0, 0)
BROWN = (150, 77, 34)
#file = open("historic_captures.txt", 'a')


def add_vect(u,v):
    return [u[0]+v[0], u[1]+v[1]]

def isInBoard(vect):
    return (vect[0]>0 and vect[0]<9 and vect[1]>0 and vect[1]<9)

opp = {'w':'b', 'b':'w'}

nb_castle = 0
nb_passant = 0
nb_capture = 0
nb_check = 0
nb_promote = 0
nb_checkmate = 0

class Board():
    def __init__(self):
        self.load_pieces()
        

    def load_pieces(self):
        """initialize each piece : its position, image, type, etc."""
        self.turn = 'w'   # white turn
        self.nb_moves = 0
        self.castle = {'w':{'s':True, 'b':True}, 'b':{'s':True, 'b':True}}
        self.enPassant = []
        self.piece_images = {}
        self.pieces = {'w':{'P':{'1':[1,2], '2':[2,2],'3':[3,2],'4':[4,2],'5':[5,2],'6':[6,2],'7':[7,2],'8':[8,2]},
                            'R':{'1':[1,1], '2':[8,1]},
                            'N':{'1':[2,1], '2':[7,1]},
                            'B':{'1':[3,1], '2':[6,1]},
                            'K':{'1':[5,1]},
                            'Q':{'1':[4,1]}},

                       'b':{'P':{'1':[1,7], '2':[2,7],'3':[3,7],'4':[4,7],'5':[5,7],'6':[6,7],'7':[7,7],'8':[8,7]},
                            'R':{'1':[1,8], '2':[8,8]},
                            'N':{'1':[2,8], '2':[7,8]},
                            'B':{'1':[3,8], '2':[6,8]},
                            'K':{'1':[5,8]},
                            'Q':{'1':[4,8]}}}

        self.piecesPositions = {'w':{'P':{'1':[1,2],'2':[2,2],'3':[3,2],'4':[4,2],'5':[5,2],'6':[6,2],'7':[7,2],'8':[8,2]},
                            'R':{'1':[1,1], '2':[8,1]},
                            'N':{'1':[2,1], '2':[7,1]},
                            'B':{'1':[3,1], '2':[6,1]},
                            'K':{'1':[5,1]},
                            'Q':{'1':[4,1]}},

                       'b':{'P':{'1':[1,7], '2':[2,7],'3':[3,7],'4':[4,7],'5':[5,7],'6':[6,7],'7':[7,7],'8':[8,7]},
                            'R':{'1':[1,8], '2':[8,8]},
                            'N':{'1':[2,8], '2':[7,8]},
                            'B':{'1':[3,8], '2':[6,8]},
                            'K':{'1':[5,8]},
                            'Q':{'1':[4,8]}}}
        
        for color in self.piecesPositions:
            for type in self.piecesPositions[color]:
                for index in self.piecesPositions[color][type]:
                    self.piecesPositions[color][type][index] = self.get_coords(self.pieces[color][type][index])


        self.board = {1:{1:'wR1', 2:'wP1', 3:None, 4:None, 5:None, 6:None, 7:'bP1', 8:'bR1'},
                      2:{1:'wN1', 2:'wP2', 3:None, 4:None, 5:None, 6:None, 7:'bP2', 8:'bN1'},
                      3:{1:'wB1', 2:'wP3', 3:None, 4:None, 5:None, 6:None, 7:'bP3', 8:'bB1'},
                      4:{1:'wQ1', 2:'wP4', 3:None, 4:None, 5:None, 6:None, 7:'bP4', 8:'bQ1'},
                      5:{1:'wK1', 2:'wP5', 3:None, 4:None, 5:None, 6:None, 7:'bP5', 8:'bK1'},
                      6:{1:'wB2', 2:'wP6', 3:None, 4:None, 5:None, 6:None, 7:'bP6', 8:'bB2'},
                      7:{1:'wN2', 2:'wP7', 3:None, 4:None, 5:None, 6:None, 7:'bP7', 8:'bN2'},
                      8:{1:'wR2', 2:'wP8', 3:None, 4:None, 5:None, 6:None, 7:'bP8', 8:'bR2'}}

        # load and scale each piece's image
        surnames = ['bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'wP', 'wN', 'wB', 'wR', 'wQ', 'wK']
        for surname in surnames:
            self.piece_images[surname] = pygame.image.load(f'images/{surname}.png')
            self.piece_images[surname] = pygame.transform.smoothscale(self.piece_images[surname], ((self.piece_images[surname]).get_width()*IMG_FACTOR, (self.piece_images[surname]).get_height()*IMG_FACTOR))
        
    def changeTurn(self):   #OK
        if self.turn == 'w':
            self.turn = 'b'
        else:
            self.turn = 'w'

    def draw_board(self, win):   #OK
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, win):   #OK
        for color in self.piecesPositions:
            for type in self.piecesPositions[color]:
                for index in self.piecesPositions[color][type]:
                    if self.piecesPositions[color][type][index] != None:
                        [x,y] = self.piecesPositions[color][type][index]
                        surname = color+type
                        win.blit(self.piece_images[surname], (x + OFFSET, y + OFFSET))

    def get_board_position(self, coord_x, coord_y):   #OK
        """returns the position of the given coordinates on the chess board (from (1,1) to (8,8))"""
        return (floor(1 + coord_x/SQUARE_SIZE), floor(9 - coord_y/SQUARE_SIZE))
    
    def get_coords(self, square):   #OK
        """returns the coordinates given the position"""
        return [(square[0]-1)*SQUARE_SIZE, (8-square[1])*SQUARE_SIZE]
    
    def pieceMoves(self, id, pieces, board):   #OK
        if pieces[id[0]][id[1]][id[2]] == None:
            return []
        type = id[1]
        match type:
            case 'P':
                return self.pawnMoves(id, pieces, board)
            case 'R':
                return self.rookMoves(id, pieces, board)
            case 'B':
                return self.bishopMoves(id, pieces, board)
            case 'N':
                return self.knightMoves(id, pieces, board)
            case 'K':
                return self.kingMoves(id, pieces, board)
            case 'Q':
                return [*self.rookMoves(id, pieces, board), *self.bishopMoves(id, pieces, board)]

    def pieceCanGo(self, id, x, y, pieces, board):  #OK
        return [x,y] in self.pieceMoves(id, pieces, board)
    
    def getAllMoves(self,color, pieces, board):  #currently en passant not taken into account
        allMoves = []
        direction = {'w':1, 'b':-1}
        if self.canSmallCastle(color, pieces, board):
            print("SMALL CASTLE")
            initial = {'b':8, 'w':1}
            init = initial[color]
            allMoves.append([color+'K1', [7,init]])
        if self.canBigCastle(color, pieces, board):
            print("BIG CASTLE")
            initial = {'b':8, 'w':1}
            init = initial[color]
            allMoves.append([color+'K1', [3,init]])
        for elt in self.enPassant:
            id = board[elt[0][0]][elt[0][1]]
            if id != None and id[0] == color and id[1] == 'P' and not self.verifyCheckEnPassant(id, elt[0][0] + elt[1], elt[0][1] + direction[color], pieces, board):
                print("EN PASSANT")
                allMoves.append([id, [elt[0][0] + elt[1], elt[0][1] + direction[color]]])
        for type in pieces[color]:
            for index in pieces[color][type]:
                id = color + type + index
                moves = self.pieceMoves(id, pieces, board)
                for move in moves:
                    if id[1] == 'P' and (move[1] == 8 or move[1] == 1) and not self.verifyForCheckWithMove(id, move[0], move[1], pieces, board):
                        for upType in ['Q', 'N', 'B', 'R']:
                            allMoves.append([id, move, upType])
                            print("UP THE PAWN")
                    elif not self.verifyForCheckWithMove(id, move[0], move[1], pieces, board):
                        allMoves.append([id,move])
        return allMoves

    def isCheckmate(self, color, pieces, board):  #OK
        """verify is the color given is checkmated, i.e it does not have any moves and is in check"""

        return self.getAllMoves(color, pieces, board) == [] and self.kingInCheck(color, pieces, board)

    def isStalemate(self, color, pieces, board):  #OK
        """verify is the color given got stalemate, i.e it does not have any moves but is not in check"""
        return self.getAllMoves(color, pieces, board) == [] and not self.kingInCheck(color, pieces, board)

    def capture(self, id):   #OK
        """Deletes the id piece"""
        [x,y] = self.pieces[id[0]][id[1]][id[2]]
        self.pieces[id[0]][id[1]][id[2]] = None
        self.piecesPositions[id[0]][id[1]][id[2]] = None
        self.board[x][y] = None
    
    def bishopMoves(self, id, pieces, board):   #OK
        positions = []
        trajectories = [(1,1), (-1,-1), (1,-1), (-1,1)]
        color = id[0]
        current_pos = pieces[color][id[1]][id[2]]
        if current_pos == None: return []
        for traj in trajectories:
            k = 1
            pos = add_vect(current_pos,(k*traj[0], k*traj[1]))
            while isInBoard(pos) and board[pos[0]][pos[1]] == None:
                positions.append(pos)
                k+=1
                pos = add_vect(current_pos,(k*traj[0], k*traj[1]))
            if isInBoard(pos):
                #there was a piece
                if board[pos[0]][pos[1]][0] != color:
                    positions.append(pos)
        return positions
    
    def rookMoves(self, id, pieces, board):   #OK
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1)]
        color = id[0]
        current_pos = pieces[color][id[1]][id[2]]
        if current_pos == None: return []
        for traj in trajectories:
            k = 1
            pos = add_vect(current_pos,(k*traj[0], k*traj[1]))
            while isInBoard(pos) and board[pos[0]][pos[1]] == None:
                positions.append(pos)
                k+=1
                pos = add_vect(current_pos,(k*traj[0], k*traj[1]))
            if isInBoard(pos):
                #there was a piece
                if board[pos[0]][pos[1]][0] != color:
                    positions.append(pos)
        return positions
                
    def kingMoves(self, id, pieces, board):   #OK
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1), (1,1), (-1,-1), (1,-1), (-1,1)]
        color = id[0]
        current_pos = pieces[color][id[1]][id[2]]
        if current_pos == None: return []
        for traj in trajectories:
            pos = add_vect(current_pos,(traj[0], traj[1]))
            if isInBoard(pos) and board[pos[0]][pos[1]] == None:
                positions.append(pos)
            elif isInBoard(pos):
                #there was a piece
                if board[pos[0]][pos[1]][0] != color:
                    positions.append(pos)
        return positions
                
    def knightMoves(self, id, pieces, board):   #OK
        positions = []
        trajectories = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-2,-1), (-1,2), (-1,-2)]
        color = id[0]
        current_pos = pieces[color][id[1]][id[2]]
        if current_pos == None: return []
        for traj in trajectories:
            pos = add_vect(current_pos,(traj[0], traj[1]))
            if isInBoard(pos) and board[pos[0]][pos[1]] == None:
                positions.append(pos)
            elif isInBoard(pos):
                #there was a piece
                if board[pos[0]][pos[1]][0] != color:
                    positions.append(pos)
        return positions

    def pawnMoves(self, id, pieces, board): #OK
        positions = []
        color = id[0]
        direction = {'w':(1,2), 'b':(-1,7)}
        current_pos = pieces[color][id[1]][id[2]]
        if current_pos == None: return []
        [x,y] = current_pos
        if isInBoard([x,y + direction[color][0]]) and board[x][y + direction[color][0]] == None:  #the square in front
            positions.append([x,y + direction[color][0]])
            if y == direction[color][1] and board[x][y + direction[color][0]] == None and board[x][y + direction[color][0]*2] == None:   #first move up 2
                positions.append([x,y + direction[color][0]*2])
        for elt in [-1,1]:
            if x+elt >0 and x+elt<9:
                square = board[x+elt][y+direction[color][0]]
                if y<=7 and square != None and square[0] == opp[color]:
                    positions.append([x+elt, y+direction[color][0]])
        return positions

    def canSmallCastle(self, color, pieces, board, castles = None): #OK
        if castles == None:
            castles = self.castle
        dico = {'w':1, 'b':8}
        check = self.kingInCheck(color, pieces, board)
        if (not check) and castles[color]['s'] and board[6][dico[color]] == None and board[7][dico[color]] == None:

            potBoard1 = deepcopy(board)
            potPieces1 = deepcopy(pieces)
            potBoard1[6][dico[color]] = color + 'K1'
            potBoard1[5][dico[color]] = None
            potPieces1[color]['K']['1'] = [6,dico[color]]

            potBoard2 = deepcopy(board)
            potPieces2 = deepcopy(pieces)
            potPieces2[color]['K']['1'] = [7,dico[color]]
            potBoard2[7][dico[color]] = color + 'K1'
            potBoard2[5][dico[color]] = None
            
            return (not self.kingInCheck(color, potPieces1, potBoard1)) and (not self.kingInCheck(color, potPieces2, potBoard2))
        return False

    def canBigCastle(self, color, pieces, board, castles = None): #OK
        if castles == None:
            castles = self.castle
        dico = {'w':1, 'b':8}
        check = self.kingInCheck(color, pieces, board)
        if (not check) and castles[color]['b'] and board[2][dico[color]] == None and board[3][dico[color]] == None and board[4][dico[color]] == None:
            potBoard1 = deepcopy(board)
            potPieces1 = deepcopy(pieces)
            potBoard1[3][dico[color]] = color + 'K1'
            potBoard1[5][dico[color]] = None
            potPieces1[color]['K']['1'] = [3,dico[color]]

            potBoard2 = deepcopy(board)
            potPieces2 = deepcopy(pieces)
            potPieces2[color]['K']['1'] = [4,dico[color]]
            potBoard2[4][dico[color]] = color + 'K1'
            potBoard1[2][dico[color]] = None
            if (not self.kingInCheck(color, potPieces1, potBoard1)) and (not self.kingInCheck(color, potPieces2, potBoard2)):
                return True
        return False

    def do_castle(self,color, type_castle): #OK
        dico = {'w':1, 'b':8, "small":(6,7), "big":(4,3), 's2':8, 'b2':1}
        if type_castle == "small":
            self.board[5][dico[color]] = None
            self.board[8][dico[color]] = None
            self.board[6][dico[color]] = color + 'R2'
            self.board[7][dico[color]] = color + 'K1'
            self.pieces[color]['K']['1'] = [7,dico[color]]
            self.pieces[color]['R']['2'] = [6,dico[color]]
            self.piecesPositions[color]['R']['2'] = self.get_coords([6,dico[color]])
            self.piecesPositions[color]['K']['1'] = self.get_coords([7,dico[color]])
        else:
            self.board[1][dico[color]] = None
            self.board[5][dico[color]] = None
            self.board[4][dico[color]] = color + 'R1'
            self.board[3][dico[color]] = color + 'K1'
            self.pieces[color]['K']['1'] = [3,dico[color]]
            self.pieces[color]['R']['1'] = [4,dico[color]]
            self.piecesPositions[color]['R']['1'] = self.get_coords([4,dico[color]])
            self.piecesPositions[color]['K']['1'] = self.get_coords([3,dico[color]])
        return None

    def updateCastle(self, id, x, y): #OK
        """piece is about to move to (x,y), update the possibility of castling"""
        color = id[0]
        if id[1] == 'K':    #the king moved
            self.castle[color]['s'] = False
            self.castle[color]['b'] = False
            return None
        if id[1] == 'R':    #a rook moved
            if id[2] == 1:
                self.castle[color]['b'] = False
            elif id[2] == 2:
                self.castle[color]['s'] = False
        
        opp_square = {'w':8, 'b':1}
        if y == opp_square[color]: #might have eaten a rook
            if x == 1:
                self.castle[opp[color]]['b'] = False
                return None
            elif x == 8:
                self.castle[opp[color]]['s'] = False
                return None
        return None


    def triesToCastle(self, id, x, y, pieces): #OK
        [px, py] = pieces[id[0]][id[1]][id[2]]
        return id[1] == 'K' and px == 5 and ((py == 1 and y == 1) or (py == 8 and y == 8)) and (x == px + 2 or x == px - 2)

    def canEnPassant(self, id, x, y, pieces): #OK
        """update after each move the list of pawns that can en passant (id go to x,y)"""
        if id[1] != 'P':
            self.enPassant = []
            return None
        else:
            [px,py] = pieces[id[0]][id[1]][id[2]]
            if py - y == 2 or py - y == -2:
                for move in [[[x-1, y],1],[[x+1, y],-1]]:
                    if isInBoard(move[0]):
                        self.enPassant.append(move)
                return None
            else:
                self.enPassant = []

    def doEnPassant(self, id, new_x, new_y): #OK
        """eat the pawn, update board, pieces and piecesPositions"""
        dico = {'w':-1, 'b':1}
        old_x, old_y = self.pieces[id[0]][id[1]][id[2]]
        id2 = self.board[new_x][old_y]
        for elt in self.enPassant:
            if elt[0] == [new_x, new_y]:
                direction = elt[1]
        
        self.board[new_x][new_y] = id
        self.board[old_x][old_y] = None
        self.board[new_x][old_y] = None
        self.pieces[id[0]][id[1]][id[2]] = [new_x, new_y]
        self.pieces[id2[0]][id2[1]][id2[2]] = None
        self.piecesPositions[id[0]][id[1]][id[2]] = self.get_coords([new_x, new_y])
        self.piecesPositions[id2[0]][id2[1]][id2[2]] = None

    
    def isUppingPawn(self, id, pieces): #OK
        """checks if a pawn needs to be upped"""
        return id[1] == 'P' and (pieces[id[0]][id[1]][id[2]][1] == 1 or pieces[id[0]][id[1]][id[2]][1] == 8)

    def upThePawn(self, id, newType, new_x, new_y): #OK
        """turns the id pawn into the new type (queen rook bishop knight)"""
        color = id[0]
        type = id[1]
        index = id[2]
        [x,y] = self.pieces[color][type][index]
        self.pieces[color][type][index] = None  #remove the pawn
        self.piecesPositions[color][type][index] = None
        self.pieces[color][newType][str(len(self.pieces[color][newType])+1)] = [new_x,new_y]  #add the new type
        self.piecesPositions[color][newType][str(len(self.piecesPositions[color][newType])+1)] = self.get_coords([new_x,new_y])
        self.board[new_x][new_y] = color + newType + str(len(self.pieces[color][newType]))
        self.board[x][y] = None

    def isEnPassant(self, id, x, y, pieces): #OK
        """checks if a pawn move to (x,y) is in the self.enPassant"""
        if id[1] != 'P': return False
        color = id[0]
        [px, py] = pieces[id[0]][id[1]][id[2]]
        direction = {'b':-1, 'w':1}
        return [[px, py],x-px] in self.enPassant and y == py + direction[color]
    
    def verifyCheckEnPassant(self, id, x, y, pieces, board):    #maybe put directly in code to optimize
        """checks if doing en passant is going to put your king in check"""
        [px, py] = pieces[id[0]][id[1]][id[2]]
        new_board = deepcopy(board)
        new_pieces = deepcopy(pieces)
        id2 = new_board[x][py]

        new_board[x][y] = id
        new_board[px][py] = None
        new_board[x][py] = None
        new_pieces[id2[0]][id2[1]][id2[2]] = None
        new_pieces[id[0]][id[1]][id[2]] = [x,y]
        return self.kingInCheck(id[0], new_pieces, new_board)

    def isLegalMove(self, id, x, y, pieces, board): #OK moyen
        """checks if the move piece to (x,y) is a legal move"""
        color = id[0]
        type = id[1]
        if self.isEnPassant(id, x, y, pieces):  #plus de verif a faire, verif si roi est check
            return not self.verifyCheckEnPassant(id, x, y, pieces, board)
        if type == 'K':
            if self.triesToCastle(id, x, y, pieces):   #maybe tries to castle:
                if x == 7:
                    return self.canSmallCastle(color, pieces, board)
                elif x == 3:
                    return self.canBigCastle(color, pieces, board)
        return self.pieceCanGo(id, x, y, pieces, board) and (not self.verifyForCheckWithMove(id, x, y, pieces, board))

    def verifyForCheckWithMove(self, id, x, y, pieces, board): #OK peut etre mettre direct dans code pr opti
        """verifies if moving the piece in (x,y) puts you in check"""
        new_board = deepcopy(board)
        new_pieces = deepcopy(pieces)
        square = new_board[x][y]
        
        if square != None:  #There is a piece
            new_pieces[square[0]][square[1]][square[2]] = None
        [px, py] = pieces[id[0]][id[1]][id[2]]
        new_pieces[id[0]][id[1]][id[2]] = [x,y]
        new_board[x][y] = id
        new_board[px][py] = None

        return self.kingInCheck(id[0], new_pieces, new_board)    #we look if we are in check by doing this move

    def kingInCheck(self, color, pieces, board): #OK
        """verifies if the 'color' king is in check or not on the board"""
        [king_x, king_y] = pieces[color]['K']['1']
        for type in pieces[opp[color]] :
            for index in pieces[opp[color]][type] :
                id = opp[color] + type + index
                if self.pieceCanGo(id, king_x, king_y, pieces, board):
                    return True
        return False
    
    def playGame(self, list_moves, dt):
        for move in list_moves:
            board.playMove(self, move)
            self.draw_board()
            self.draw_pieces()
            sleep(dt)
            pygame.display.flip()
    
    def playMove(self, id, new_x, new_y, upType = None):
        global nb_castle
        global nb_passant
        global nb_capture
        global nb_promote
        global nb_checkmate
        #global file
        nb_moves_increase = True
        #if id[0] == 'w' and id[1] == 'P' and new_y == 5:
        #    print(id, new_x, new_y)
        if self.board[new_x][new_y] != None:    #there is an opposite piece
            #print("lalala")
            #file.write(id + " " + self.board[new_x][new_y] + '\n')
            self.capture(self.board[new_x][new_y])
            nb_capture += 1
            #print(nb_capture)
            
            nb_moves_increase = False
        
        old_x, old_y = self.pieces[id[0]][id[1]][id[2]]
        
        if upType != None:
            nb_promote += 1
            if upType not in ['Q', 'R', 'N', 'B']:
                self.upThePawn(id, 'Q', new_x, new_y)
            else:
                self.upThePawn(id, upType, new_x, new_y)
            nb_moves_increase = False

        elif self.triesToCastle(id, new_x, new_y, self.pieces): #we try to castle
            nb_castle += 1
            if new_x == 7:
                self.do_castle(id[0], "small")
            else:
                self.do_castle(id[0], "big")
        else:
            if self.isEnPassant(id, new_x, new_y, self.pieces):   #we want to en passant
                nb_passant += 1
                self.doEnPassant(id, new_x, new_y) #rm the enpassanted pawn, update the position of the pawn
                self.enPassant = []
            else:
                self.canEnPassant(id, new_x, new_y, self.pieces)     #update the possibility of en passant after the move
                self.pieces[id[0]][id[1]][id[2]] = [new_x, new_y]
                self.board[new_x][new_y] = id
                self.board[old_x][old_y] = None
                self.piecesPositions[id[0]][id[1]][id[2]] = self.get_coords([new_x, new_y]) #update the screen coords
        
        if nb_moves_increase:
            self.nb_moves += 1
        else:
            self.nb_moves = 0
        if self.nb_moves == 50:
            print('Draw 50 moves rule')
            reset(self)
        self.updateCastle(id, new_x, new_y)
        self.changeTurn()
        if self.isCheckmate(self.turn, self.pieces, self.board):
            print("checkmate !")
            nb_checkmate += 1
            reset(self)
        if self.isStalemate(self.turn, self.pieces, self.board):
            print("stalemate...")
            reset(self)
        #print(self.getAllMoves(board.turn, self.pieces, self.board))
        id = None

def nb_moves(depth, board:Board):
    board.piece_images = None
    nb = 0
    moves = board.getAllMoves(board.turn, board.pieces, board.board)
    if depth == 1 or len(moves) == 0:
        return len(moves)
    else:
        for move in moves:
            new_board = deepcopy(board)
            if len(move) == 3:
                new_board.playMove(move[0], move[1][0], move[1][1], move[2])
            else:
                new_board.playMove(move[0], move[1][0], move[1][1])
            nb += nb_moves(depth-1, new_board)
            if depth == 5:
                print(nb)
    return nb


def reset(board:Board):
    board.load_pieces()
    board.playMove('wP4', 4,7)
    board.playMove('wB2', 3,4)
    board.playMove('wN2', 5,2)
    board.playMove('bN2', 6,2)
    board.playMove('bB2', 5,7)
    board.playMove('bK1',6,8)
    board.playMove('bP3', 3,6)
    board.turn = 'w'