#!/usr/bin/env python3
"""
main driver file, handles user input and gui display
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512  # board size
DIMENSION = 8  # amount of rows and columns
SQ_SIZE = HEIGHT // DIMENSION  # tile size
MAX_FPS = 15  # animation speed?
IMAGES = {}  # dictionary of images

'''
initializes glob dict of images. only call once
'''


def load_images():
    pieces = ['wP', 'wB', 'wN', 'wR', 'wQ', 'wK', 'bP', 'bB', 'bN', 'bR', 'bQ', 'bK']  # list of pieces
    for piece in pieces:  # tells the images where they need to be
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # print(IMAGES[piece])
        # NOTE: images accessible with 'IMAGES['piece']'


'''
main driver code (user input & graphics)
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))  # initializes display
    clock = p.time.Clock()  # initializes clock
    screen.fill(p.Color("pink"))  # background color
    gs = ChessEngine.GameState()  # generates current gamestate
    valid_moves = gs.get_valid_moves()  # generates valid moves
    move_made = False  # flag var for when a move is made

    load_images()  # generates images
    running = True
    sq_selected = ()  # keeps track of last click location user
    player_clicks = []  # keeps track of player clicks (two tuples: [(4, 7), (3, 5)])
    while running:  # main while loop (where the magic happens)
        for e in p.event.get():
            if e.type == p.QUIT:  # stops program when window is closed
                running = False

            # handles mouse events
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # location of mouse
                col = location[0] // SQ_SIZE  # y_pos mouse
                row = location[1] // SQ_SIZE  # x_pos mouse
                if sq_selected == (row, col):  # if we clicked something, where?
                    sq_selected = ()
                    player_clicks = []
                else:  # did we click something?
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:  # after 2nd click (move piece)
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)  # keeps track of current move
                    print(move.get_chess_notation())  # prints move to console
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:  # checks if move valid
                            gs.make_move(valid_moves[i])  # this actually makes the move
                            move_made = True
                            sq_selected = ()  # emptying to get rea-
                            player_clicks = []  # -dy for a new move
                    if not move_made:
                        player_clicks = [sq_selected]
            # handles keyboard events
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:  # undo when left key is pressed
                    gs.undo_move()
                    move_made = True

        if move_made:  # if we made a move
            valid_moves = gs.get_valid_moves()  # generate new valid moves
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


'''
creates all graphics within current game state
'''


def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)


'''
draw chessboard
'''


def draw_board(screen):
    colors = [p.Color("lightslategray"), p.Color("darkslategray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
draws pieces on board using current gs.board
'''


def draw_pieces(screen, board):  # places pieces where need be
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
