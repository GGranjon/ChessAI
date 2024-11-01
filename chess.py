import pygame
import sys
from math import floor
from copy import copy
pygame.init()

# Parameters
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
IMG_FACTOR = 0.65
SQUARE_SIZE = WIDTH // COLS
PIECES_SIZE = pygame.image.load('images/bp.png').get_width()*IMG_FACTOR
OFFSET = (SQUARE_SIZE - PIECES_SIZE)/2
FPS = 60

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
    
    def all_positions(self):
        match self.type:
            case 'p':
                return all_pawn_positions(self)
        return None
    
    def all_possible_positions(self, pieces):
        return None
    
    def all_pawn_positions(self):
        positions = []




class Board():
    def __init__(self):
        self.turn = 0   # white turn
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
                    piece = Piece('w', 'p', j, 2)
                    self.white_pieces.append(piece)
                elif i == 1:
                    piece = Piece('b', 'p', j, 7)
                    self.black_pieces.append(piece)

        #other pieces
        pieces_array = [('w', 'r', 1, 1), ('w', 'r', 8, 1), ('w', 'n', 2, 1), ('w', 'n', 7, 1), ('w', 'b', 3, 1), ('w', 'b', 6, 1),
                        ('w', 'q', 4, 1), ('b', 'r', 1, 8), ('b', 'r', 8, 8), ('b', 'n', 2, 8), ('b', 'n', 7, 8),
                        ('b', 'b', 3, 8), ('b', 'b', 6, 8), ('b', 'q', 4, 8),('w', 'k', 5, 1), ('b', 'k', 5, 8)]
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
    
    def draw_pieces2(self):
        for piece in self.pieces:
            win.blit(piece.image, (piece.coord_x + OFFSET, piece.coord_y + OFFSET))

    # Dessiner les pièces
    def draw_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board_map[row][col]
                if piece != "":
                    win.blit(self.piece_images[piece], (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + OFFSET))

    def get_board_position(self, coord_x, coord_y):
        """returns the position of the given coordinates on the chess board (from (1,1) to (8,8))"""
        return (floor(1 + coord_x/SQUARE_SIZE), floor(9 - coord_y/SQUARE_SIZE))
    
    def get_coords(self, x, y):
        """returns the coordinates given the position"""
        return ((x-1)*SQUARE_SIZE, (8-y)*SQUARE_SIZE)
    
    def isCheckmate(self):
        return 0

    def isEmptySquare(self, vect):
        """0 = empty square, else piece.color"""
        for piece in self.pieces:
            if (piece.x, piece.y) == vect:
                return piece.color
        return 0

    def bishopMoves(self, x, y, color):
        positions = []
        trajectories = [(1,1), (-1,-1), (1,-1), (-1,1)]
        for traj in trajectories:
            k = 1
            pos = add_vect((x,y),(k*traj[0], k*traj[1]))
            empty_square = self.isEmptySquare(pos)
            while isInBoard(pos) and empty_square == 0:
                #print(f"iteration {k}\n")
                #print(f"pos : ({pos[0]}, {pos[1]}) \n")
                positions.append(pos)
                k+=1
                pos = add_vect((x,y),(k*traj[0], k*traj[1]))
                empty_square = self.isEmptySquare(pos)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions
    
    def rookMoves(self, x, y, color):
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1)]
        for traj in trajectories:
            k = 1
            pos = add_vect((x,y),(k*traj[0], k*traj[1]))
            empty_square = self.isEmptySquare(pos)
            while isInBoard(pos) and empty_square == 0:
                #print(f"iteration {k}\n")
                #print(f"pos : ({pos[0]}, {pos[1]}) \n")
                positions.append(pos)
                k+=1
                pos = add_vect((x,y),(k*traj[0], k*traj[1]))
                empty_square = self.isEmptySquare(pos)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions

    def kingMoves(self, x, y, color):
        positions = []
        trajectories = [(1,0), (-1,0), (0,-1), (0,1), (1,1), (-1,-1), (1,-1), (-1,1)]
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            empty_square = self.isEmptySquare(pos)
            if isInBoard(pos) and empty_square == 0:
                positions.append(pos)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions
                
    def knightMoves(self, x, y, color):
        positions = []
        trajectories = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-2,-1), (-1,2), (-1,-2)]
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            empty_square = self.isEmptySquare(pos)
            if isInBoard(pos) and empty_square == 0:
                positions.append(pos)
            if isInBoard(pos):
                #there was a piece
                if empty_square != color:
                    positions.append(pos)
        return positions

    def pawnMoves(self, x, y, color):
        print(x,y)
        positions = []
        trajectories = []
        match color:
            case "w":
                if self.isEmptySquare((x,y+1)) == 0:
                    trajectories.append((0,1))
                for elt in [-1,1]:
                    print((x+elt,y+1))
                    print(self.isEmptySquare((x+elt,y+1)))
                    if y<=7 and self.isEmptySquare((x+elt,y+1)) == "b":
                        trajectories.append((elt, 1))
                if y == 2:
                    trajectories.append((0,2))
                print(trajectories)
            case 'b':
                if self.isEmptySquare((x,y-1)) == 0:
                    trajectories.append((0,-1))
                for elt in [-1,1]:
                    if y >=2 and self.isEmptySquare((x+elt,y-1)) == "w":
                        trajectories.append((elt, -1))
                if y == 7:
                    trajectories.append((0,-2))
        for traj in trajectories:
            pos = add_vect((x,y),(traj[0], traj[1]))
            print(pos)
            empty_square = self.isEmptySquare(pos)
            if isInBoard(pos) and empty_square != color:
                positions.append(pos)
        print(positions)
        return positions

    def isLegalMove(self, piece_index, x, y):
        piece = self.pieces[piece_index]
        color = piece.color
        match piece.type:
            case 'p':
                return (x,y) in self.pawnMoves(piece.x, piece.y, color)
            case 'r':
                return (x,y) in self.rookMoves(piece.x, piece.y, color)
            case 'b':
                return (x,y) in self.bishopMoves(piece.x,piece.y,color)
            case 'n':
                return (x,y) in self.knightMoves(piece.x,piece.y,color)
            case 'k':
                return (x,y) in self.kingMoves(piece.x, piece.y, color)
            case 'q':
                return (x,y) in [*self.rookMoves(piece.x, piece.y, color), *self.bishopMoves(piece.x, piece.y, color)]
        return True

    def kingInCheck(self, color, pieces):
        """white king : index = 15, black king : index = 31"""
        inCheck = False
        if color == 'w' : index = 15
        else : index = 31
        king_x, king_y = pieces[index].x, pieces[index].y
        for piece in enumerate(pieces) :
            if piece.color != color:
                px, py = piece.x, piece.y
                match piece.type :
                    case 'p':
                        if (king_x == px - 1 and king_y == py + 1) or (king_x == px + 1 and king_y == py + 1):
                            return True
                    case 'q':
                        if rookCanGo(self, piece.x, piece.y, king_x, king_y, pieces) or bishopCanGo(self, piece.x, piece.y, king_x, king_y, pieces):    #TODO : a optimiser : appeler ces fcts une fois et sauvergarder leur resultat
                            return True
                    case 'r':
                        if rookCanGo(self, piece.x, piece.y, king_x, king_y, pieces):
                            return True
                    case 'b':
                        if bishopCanGo(self, piece.x, piece.y, king_x, king_y, pieces):
                            return True
                    case 'n':
                        if (king_x, king_y) in [(px-1,py+2),(px+1,py+2),(px-1,py-2),(px+1,py-2),(px-2,py+1),(px-2,py-1),(px+2,py-1),(px+2,py+1)]:
                            return True
                    case 'k':
                        None
        return False

    def isDraw(self):
        return 0

board = Board()

def animate():
    if board.turn == 0: #white to play
        None
    return 0
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
                    
                    if board.isLegalMove(moving_piece, new_x, new_y):
                        p.x, p.y = new_x, new_y
                        p.coord_x, p.coord_y = board.get_coords(new_x, new_y)
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
        board.draw_pieces2()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()