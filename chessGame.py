from math import floor
from time import sleep
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

def add_vect(u,v):
    return [u[0]+v[0], u[1]+v[1]]

def isInBoard(vect):
    return (vect[0]>0 and vect[0]<9 and vect[1]>0 and vect[1]<9)

opp = {'w':'b', 'b':'w'}

# load and scale each piece's image
piece_images = {}
surnames = ['bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'wP', 'wN', 'wB', 'wR', 'wQ', 'wK']
for surname in surnames:
    piece_images[surname] = pygame.image.load(f'images/{surname}.png')
    piece_images[surname] = pygame.transform.smoothscale(piece_images[surname], ((piece_images[surname]).get_width()*IMG_FACTOR, (piece_images[surname]).get_height()*IMG_FACTOR))

class Board():
    def __init__(self):
        self.init()
        
    def init(self):
        """initialize the board"""
        self.turn = 'w'   # white turn
        self.nb_moves = 0
        self.castle = {'w':{'s':True, 'b':True}, 'b':{'s':True, 'b':True}}
        self.enPassant = []
        self.pieces = {'w':{'Q':{'1':[4,1]},
                            'B':{'1':[3,1], '2':[6,1]},
                            'N':{'1':[2,1], '2':[7,1]},
                            'R':{'1':[1,1], '2':[8,1]},
                            'K':{'1':[5,1]},
                            'P':{'1':[1,2], '2':[2,2],'3':[3,2],'4':[4,2],'5':[5,2],'6':[6,2],'7':[7,2],'8':[8,2]}},

                       'b':{'Q':{'1':[4,8]},
                            'B':{'1':[3,8], '2':[6,8]},
                            'N':{'1':[2,8], '2':[7,8]},
                            'R':{'1':[1,8], '2':[8,8]},
                            'K':{'1':[5,8]},
                            'P':{'1':[1,7], '2':[2,7],'3':[3,7],'4':[4,7],'5':[5,7],'6':[6,7],'7':[7,7],'8':[8,7]}}}

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

        
    def changeTurn(self):
        if self.turn == 'w':
            self.turn = 'b'
        else:
            self.turn = 'w'

    def draw_board(self, win):
        win.fill(WHITE)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(win, BROWN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, win):
        for color in self.piecesPositions:
            for type in self.piecesPositions[color]:
                for index in self.piecesPositions[color][type]:
                    if self.piecesPositions[color][type][index] != None:
                        [x,y] = self.piecesPositions[color][type][index]
                        surname = color+type
                        win.blit(piece_images[surname], (x + OFFSET, y + OFFSET))

    def get_board_position(self, coord_x, coord_y):
        """returns the position of the given coordinates on the chess board (from (1,1) to (8,8))"""
        return (floor(1 + coord_x/SQUARE_SIZE), floor(9 - coord_y/SQUARE_SIZE))
    
    def get_coords(self, square):
        """returns the coordinates given the position"""
        return [(square[0]-1)*SQUARE_SIZE, (8-square[1])*SQUARE_SIZE]
    
    def pieceMoves(self, id, pieces, board):
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

    def pieceCanGo(self, id, x, y, pieces, board):
        return [x,y] in self.pieceMoves(id, pieces, board)
    
    def getAllMoves(self,color, pieces, board):  #currently en passant not taken into account
        allMoves = []
        direction = {'w':1, 'b':-1}
        if self.canSmallCastle(color, pieces, board):   #ok
            initial = {'b':8, 'w':1}
            init = initial[color]
            allMoves.append([color+'K1', [7,init]])
        if self.canBigCastle(color, pieces, board): #ok
            initial = {'b':8, 'w':1}
            init = initial[color]
            allMoves.append([color+'K1', [3,init]])
        for elt in self.enPassant:
            id = board[elt[0][0]][elt[0][1]]
            if id != None and id[0] == color and id[1] == 'P' and not self.verifyCheckEnPassant(id, elt[0][0] + elt[1], elt[0][1] + direction[color], pieces, board):
                #print("EN PASSANT")
                allMoves.append([id, [elt[0][0] + elt[1], elt[0][1] + direction[color]]])
        for type in pieces[color]:
            for index in pieces[color][type]:
                id = color + type + index
                moves = self.pieceMoves(id, pieces, board)
                for move in moves:
                    if id[1] == 'P' and (move[1] == 8 or move[1] == 1) and not self.verifyForCheckWithMove(id, move[0], move[1], pieces, board):
                        for upType in ['Q', 'N', 'B', 'R']:
                            allMoves.append([id, move, upType])
                            #print("UP THE PAWN")
                    elif not self.verifyForCheckWithMove(id, move[0], move[1], pieces, board):
                        allMoves.append([id,move])
        return allMoves

    def isCheckmate(self, color, pieces, board):
        """verify is the color given is checkmated, i.e it does not have any moves and is in check"""
        return self.getAllMoves(color, pieces, board) == [] and self.kingInCheck(color, pieces, board)

    def isStalemate(self, color, pieces, board):
        """verify is the color given got stalemate, i.e it does not have any moves but is not in check"""
        return self.getAllMoves(color, pieces, board) == [] and not self.kingInCheck(color, pieces, board)

    def capture(self, id):
        """Deletes the id piece"""
        [x,y] = self.pieces[id[0]][id[1]][id[2]]
        self.pieces[id[0]][id[1]][id[2]] = None
        self.piecesPositions[id[0]][id[1]][id[2]] = None
        self.board[x][y] = None
    
    def bishopMoves(self, id, pieces, board):
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
    
    def rookMoves(self, id, pieces, board):
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
                
    def kingMoves(self, id, pieces, board):
        """return the list of board coordinates where the king can go"""
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
                
    def knightMoves(self, id, pieces, board):
        """return the list of board coordinates where the knight can go"""
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

    def pawnMoves(self, id, pieces, board):
        """return the list of board coordinates where the pawn can go"""
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

    def canSmallCastle(self, color, pieces, board, castles = None):
        """checks if small castle is allowed"""
        if castles == None:
            castles = self.castle
        dico = {'w':1, 'b':8}
        check = self.kingInCheck(color, pieces, board)
        if (not check) and castles[color]['s'] and board[6][dico[color]] == None and board[7][dico[color]] == None:

            #we verify if in check on the first castle square
            board[6][dico[color]] = color + 'K1'
            board[5][dico[color]] = None
            pieces[color]['K']['1'] = [6,dico[color]]

            inCheck1 = self.kingInCheck(color, pieces, board)

            #we verify if in check on the second castle square
            board[6][dico[color]] = None
            board[7][dico[color]] = color + 'K1'
            pieces[color]['K']['1'] = [7,dico[color]]

            inCheck2 = self.kingInCheck(color, pieces, board)
            
            #we put the board back to its original position
            board[5][dico[color]] = color + 'K1'
            board[7][dico[color]] = None
            pieces[color]['K']['1'] = [5,dico[color]]

            return (not inCheck1) and (not inCheck2)
        return False

    def canBigCastle(self, color, pieces, board, castles = None):
        """checks if big castle is allowed"""
        if castles == None:
            castles = self.castle
        dico = {'w':1, 'b':8}
        check = self.kingInCheck(color, pieces, board)
        if (not check) and castles[color]['b'] and board[2][dico[color]] == None and board[3][dico[color]] == None and board[4][dico[color]] == None:
            
            #we verify if in check on the first castle square
            board[4][dico[color]] = color + 'K1'
            board[5][dico[color]] = None
            pieces[color]['K']['1'] = [4,dico[color]]

            inCheck1 = self.kingInCheck(color, pieces, board)

            #we verify if in check on the second castle square
            pieces[color]['K']['1'] = [3,dico[color]]
            board[3][dico[color]] = color + 'K1'
            board[4][dico[color]] = None

            inCheck2 = self.kingInCheck(color, pieces, board)

            #we put the board back to its original position
            pieces[color]['K']['1'] = [5, dico[color]]
            board[5][dico[color]] = color + 'K1'
            board[3][dico[color]] = None

            return (not inCheck1) and (not inCheck2)
        return False

    def do_castle(self,color, type_castle):
        """makes the move of castling"""
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

    def updateCastle(self, id, x, y):
        """id is about to move to (x,y), update the possibility of castling"""
        color = id[0]
        if id[1] == 'K':    #the king moved
            self.castle[color]['s'] = False
            self.castle[color]['b'] = False
            return None
        if id[1] == 'R':    #a rook moved
            if id[2] == '1':
                self.castle[color]['b'] = False
            elif id[2] == '2':
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


    def triesToCastle(self, id, x, y, pieces):
        """checks if the move is a castle"""
        [px, py] = pieces[id[0]][id[1]][id[2]]
        return id[1] == 'K' and px == 5 and ((py == 1 and y == 1) or (py == 8 and y == 8)) and (x == px + 2 or x == px - 2)

    def updateEnPassant(self, id, px, py, x, y):
        """update after each move the list of pawns that can en passant (id go from px, py to x,y)"""
        self.enPassant = []    #clear
        if id[1] == 'P':
            if py - y == 2 or py - y == -2:
                for move in [[[x-1, y],1],[[x+1, y],-1]]:
                    if isInBoard(move[0]):
                        self.enPassant.append(move)

    def doEnPassant(self, id, new_x, new_y):
        """eat the pawn, update board, pieces and piecesPositions"""

        old_x, old_y = self.pieces[id[0]][id[1]][id[2]]
        id2 = self.board[new_x][old_y]
        
        self.board[new_x][new_y] = id
        self.board[old_x][old_y] = None
        self.board[new_x][old_y] = None
        self.pieces[id[0]][id[1]][id[2]] = [new_x, new_y]
        self.pieces[id2[0]][id2[1]][id2[2]] = None
        self.piecesPositions[id[0]][id[1]][id[2]] = self.get_coords([new_x, new_y])
        self.piecesPositions[id2[0]][id2[1]][id2[2]] = None

    def upThePawn(self, id, newType, new_x, new_y):
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

    def isEnPassant(self, id, x, y, pieces):
        """checks if a pawn move to (x,y) is in the self.enPassant"""
        if id[1] != 'P': return False
        color = id[0]
        [px, py] = pieces[id[0]][id[1]][id[2]]
        direction = {'b':-1, 'w':1}
        return [[px, py],x-px] in self.enPassant and y == py + direction[color]
    
    def verifyCheckEnPassant(self, id, x, y, pieces, board):
        """checks if doing en passant is going to put your king in check"""
        [px, py] = pieces[id[0]][id[1]][id[2]]
        id2 = board[x][py]

        #modify the board to check for check
        board[x][y] = id
        board[px][py] = None
        board[x][py] = None
        pieces[id2[0]][id2[1]][id2[2]] = None
        pieces[id[0]][id[1]][id[2]] = [x,y]

        #reset the board
        board[x][y] = None
        board[px][py] = id
        board[x][py] = id2
        pieces[id2[0]][id2[1]][id2[2]] = [x,py]
        pieces[id[0]][id[1]][id[2]] = [px, py]

        inCheck = self.kingInCheck(id[0], pieces, board)
        return inCheck

    def isLegalMove(self, id, x, y, pieces, board): #OK moyen
        """checks if the move piece to (x,y) is a legal move"""
        color = id[0]
        type = id[1]
        if self.isEnPassant(id, x, y, pieces):
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
        
        square = board[x][y]
        [px, py] = pieces[id[0]][id[1]][id[2]]

        if square != None:  #There is a piece
            pieces[square[0]][square[1]][square[2]] = None
        pieces[id[0]][id[1]][id[2]] = [x,y]
        board[x][y] = id
        board[px][py] = None

        inCheck = self.kingInCheck(id[0], pieces, board)    #we look if we are in check by doing this move

        if square != None:
            pieces[square[0]][square[1]][square[2]] = [x,y]
        pieces[id[0]][id[1]][id[2]] = [px,py]
        board[x][y] = square
        board[px][py] = id
        

        return inCheck

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
        """allows to visualize a game that has been played, with a time dt between each move"""
        for move in list_moves:
            self.playMove(self, *move)
            self.draw_board()
            self.draw_pieces()
            sleep(dt)
            pygame.display.flip()
    
    def playMove(self, id, new_x, new_y, upType = None):
        nb_moves_increase = True
        if self.board[new_x][new_y] != None:    #there is an opposite piece
            self.capture(self.board[new_x][new_y])  #maybe just put the code directly
            nb_moves_increase = False
        
        old_x, old_y = self.pieces[id[0]][id[1]][id[2]]
        
        if upType != None:
            if upType not in ['Q', 'R', 'N', 'B']:
                self.upThePawn(id, 'Q', new_x, new_y)
            else:
                self.upThePawn(id, upType, new_x, new_y)
            nb_moves_increase = False

        elif self.triesToCastle(id, new_x, new_y, self.pieces): #we try to castle
            if new_x == 7:
                self.do_castle(id[0], "small")
            else:
                self.do_castle(id[0], "big")
        else:
            if self.isEnPassant(id, new_x, new_y, self.pieces):   #we want to en passant
                self.doEnPassant(id, new_x, new_y) #rm the enpassanted pawn, update the position of the pawn
            else:
                self.pieces[id[0]][id[1]][id[2]] = [new_x, new_y]
                self.board[new_x][new_y] = id
                self.board[old_x][old_y] = None
                self.piecesPositions[id[0]][id[1]][id[2]] = self.get_coords([new_x, new_y]) #update the screen coords
        
        self.updateEnPassant(id, old_x, old_y, new_x, new_y)     #update the possibility of en passant after the move
        self.updateCastle(id, new_x, new_y)

        if nb_moves_increase:
            self.nb_moves += 1
        else:
            self.nb_moves = 0
        if self.nb_moves == 50:
            print('Draw 50 moves rule')
            #self.init()

        self.changeTurn()
        if self.isCheckmate(self.turn, self.pieces, self.board):
            print("checkmate !")
            #self.init()
        if self.isStalemate(self.turn, self.pieces, self.board):
            print("stalemate...")
            #self.init()
        #print(self.getAllMoves(self.turn, self.pieces, self.board), "\n\n\n")
        return self

    def setPos1(self):
        self.init()
        self.playMove('wP4', 4,7)
        self.playMove('wB2', 3,4)
        self.playMove('wN2', 5,2)
        self.playMove('bN2', 6,2)
        self.playMove('bB2', 5,7)
        self.playMove('bK1',6,8)
        self.playMove('bP3', 3,6)
        self.turn = 'w'
    def setPos2(self):
        self.init()
        self.playMove("wN1", 3,3)
        self.playMove("wN2", 5,5)
        self.playMove("wQ1", 6,3)
        self.playMove("wP4", 4,5)
        self.playMove("wP5", 5,4)
        self.playMove("wB1", 4,2)
        self.playMove("wB2", 5,2)

        self.playMove("bN1", 2,6)
        self.playMove("bN2", 6,6)
        self.playMove("bP2", 2,4)
        self.playMove("bP5", 5,6)
        self.playMove("bP7", 7,6)
        self.playMove("bP8", 8,3)
        self.playMove("bB1", 1,6)
        self.playMove("bB2", 7,7)
        self.playMove("bQ1", 5,7)
