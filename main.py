import sys
import pygame

from chessGame import Board, WIDTH, HEIGHT, PIECES_SIZE
from bot import Bot
WIDTH, HEIGHT = 800, 800
IMG_FACTOR = 0.65
PIECES_SIZE = pygame.image.load('images/bp.png').get_width()*IMG_FACTOR
FPS = 120


board = Board()
board.setPos2()
bot = Bot('w')

def waitKey():
    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                waiting_for_key = False
                return
            elif event.type == pygame.KEYDOWN:
                waiting_for_key = False
                print("Touche appuyee :", pygame.key.name(event.key).upper())
                return pygame.key.name(event.key).upper()

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu d'Échecs")
    clock = pygame.time.Clock()
    id = None
    dragging = False
    running = True
    board.draw_board(win)
    while running:
        clock.tick(FPS)
        
        if False and board.turn == bot.color:
            move = bot.getMove(board)
            if len(move) == 3:
                board.playMove(move[0], move[1][0], move[1][1], move[2])
            else:
                board.playMove(move[0], move[1][0], move[1][1])

        for event in pygame.event.get():    # EVENTS
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:    # Check if we click on a piece
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pos_x, pos_y = board.get_board_position(mouse_x, mouse_y)
                if board.board[pos_x][pos_y] != None:
                        dragging = True
                        id = board.board[pos_x][pos_y]
            
            elif event.type == pygame.MOUSEBUTTONUP:    # Check if we place the piece
                if id != None:# and board.turn == 'w':
                    dragging = False
                    pieces_pos = board.piecesPositions[id[0]][id[1]][id[2]]
                    new_x, new_y = board.get_board_position(pieces_pos[0] + PIECES_SIZE/2, pieces_pos[1] + PIECES_SIZE/2)
                    
                    if id[0] == board.turn and board.isLegalMove(id, new_x, new_y, board.pieces, board.board):
                        if id[1] == 'P' and (new_y == 8 or new_y == 1):
                            upType = waitKey()
                            board.playMove(id, new_x, new_y, upType)
                        else:
                            board.playMove(id, new_x, new_y)

                    else:
                        board.piecesPositions[id[0]][id[1]][id[2]] = board.get_coords(board.pieces[id[0]][id[1]][id[2]])

            elif event.type == pygame.MOUSEMOTION:    # Check if we move the piece
                if dragging:
                    board.piecesPositions[id[0]][id[1]][id[2]][0], board.piecesPositions[id[0]][id[1]][id[2]][1] = pygame.mouse.get_pos()
                    board.piecesPositions[id[0]][id[1]][id[2]][0]-=PIECES_SIZE/2
                    board.piecesPositions[id[0]][id[1]][id[2]][1]-=PIECES_SIZE/2
        
        board.draw_board(win)
        board.draw_pieces(win)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__" and 1:
    main()