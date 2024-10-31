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
FPS = 60

# Colors
WHITE = (235, 235, 235)
BLACK = (0, 0, 0)
BROWN = (150, 77, 34)

# Window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu d'Échecs")

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
                        ('w', 'k', 5, 1), ('w', 'q', 4, 1), ('b', 'r', 1, 8), ('b', 'r', 8, 8), ('b', 'n', 2, 8), ('b', 'n', 7, 8),
                        ('b', 'b', 3, 8), ('b', 'b', 6, 8), ('b', 'k', 5, 8), ('b', 'q', 4, 8)]
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

    def isLegalMove(self):
        return 0

    def KingInCheck(self):
        return 0

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifie si l'on clique sur la pièce
                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(mouse_x, mouse_y, '\n')
                pos_x, pos_y = board.get_board_position(mouse_x, mouse_y)
                print(pos_x, pos_y, '\n')
                print(str(board.get_coords(pos_x, pos_y)) + '\n')
                for k, piece in enumerate(board.pieces):
                    if piece.x == pos_x and piece.y == pos_y:
                        dragging = True
                        moving_piece = k

            elif event.type == pygame.MOUSEBUTTONUP:
                # Relâcher la pièce
                if moving_piece != None:
                    dragging = False
                    new_x, new_y = board.get_board_position(board.pieces[moving_piece].coord_x+PIECES_SIZE/2, board.pieces[moving_piece].coord_y+PIECES_SIZE/2)
                    board.pieces[moving_piece].x = new_x
                    board.pieces[moving_piece].y = new_y
                    board.pieces[moving_piece].coord_x, board.pieces[moving_piece].coord_y = board.get_coords(new_x, new_y)
                    moving_piece = None


            elif event.type == pygame.MOUSEMOTION:
                # Déplacer la pièce si on la tient
                if dragging:
                    board.pieces[moving_piece].coord_x, board.pieces[moving_piece].coord_y = pygame.mouse.get_pos()
                    board.pieces[moving_piece].coord_x-=PIECES_SIZE/2
                    board.pieces[moving_piece].coord_y-=PIECES_SIZE/2
        board.draw_board()
        board.draw_pieces2()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()