"""
current GameState info, valid moves, MoveLog
"""
#   ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
import copy
import ctypes

class GameState:
    '''
    Holds memory of the state of the game in a list
    '''
    def __init__(self):
        # 8x8 2d list, each element 2 chars, first char repr color, second char repr piece type
        # chessboard
        self.board = [
            ["--", "--", "--", "--", "bK", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "wK", "--"],
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'B': self.get_bishop_moves, 'N': self.get_knight_moves,
                               'R': self.get_rook_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.white_to_move = True  # boolean tracking turns
        self.move_log = []  # logs all moves made throughout game
        self.white_king_pos = (7, 4)  # cords of white king
        self.black_king_pos = (0, 4)  # cords of black king
        self.in_check = False  # flag var for checks
        self.pins = []  # list of pins
        self.checks = []  # list of checks
        self.checkmate = False  # checkmate boolean
        self.stalemate = False  # stalemate boolean
        self.en_passant_possible = ()  # cords of possible en passant square
        self.current_castle_rights = CastleRights(True, True, True, True)  # castling rights
        self.castle_log = [CastleRights(self.current_castle_rights.ws, self.current_castle_rights.bs,
                                        self.current_castle_rights.wl, self.current_castle_rights.bl)]
        # log of castle rights


    def make_move(self, move):
        '''
        takes a move as a parameter and executes it (doesn't work with en passant, castling or pawn promotion)
        '''
        self.board[move.start_row][move.start_col] = "--"  # makes starting square of piece moved blank
        self.board[move.end_row][move.end_col] = move.piece_moved  # places moving piece on the ending square
        self.move_log.append(move)  # logs move
        if move.piece_moved == "wK":  # update white king loc if moved
            self.white_king_pos = (move.end_row, move.end_col)
        if move.piece_moved == "bK":  # update black king loc if moved
            self.black_king_pos = (move.end_row, move.end_col)
        self.white_to_move = not self.white_to_move  # switches turn
        if move.is_pawn_promotion:  # pawn promotion
            promoted_piece = input("Promote to Q, R, B, or N:")
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # todo improve pawn promotion
        if move.is_en_passant:  # en passant
            self.board[move.start_row][move.end_col] = "--"  # captures pawn
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:  # if a two square advance is made
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)  # updates en passantpsble
        else:
            self.en_passant_possible = ()
        if move.is_castle:
            if move.end_col - move.start_col == 2:  # short castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # move rook
                self.board[move.end_row][move.end_col + 1] = "--"  # erase old rook
            else:  # long castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # move rook
                self.board[move.end_row][move.end_col - 2] = "--"  # erase old rook
        self.update_castle_rights(move)
        self.castle_log.append(CastleRights(self.current_castle_rights.ws, self.current_castle_rights.bs,
                                            self.current_castle_rights.wl, self.current_castle_rights.bl))

    def undo_move(self):
        '''
        Undoes the last move made
        '''
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved  # moves moved piece back to starting square
            self.board[move.end_row][move.end_col] = move.piece_captured  # re-places original piece/blank square on
            # ending square
            if move.piece_moved == "wK":  # update white king loc if move undone
                self.white_king_pos = (move.start_row, move.start_col)
            if move.piece_moved == "bK":  # update black king loc if move undone
                self.black_king_pos = (move.start_row, move.start_col)
            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)
            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()
            self.white_to_move = not self.white_to_move  # switches turn
            self.castle_log.pop()  # get rid of the new castle rights from undone move
            temp_castle_rights = copy.deepcopy(
                self.castle_log[-1])  # set current castle rights to (now) last one in list
            self.current_castle_rights = temp_castle_rights
            if move.is_castle:
                if move.end_col - move.start_col == 2:  # short castle
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:  # long castle
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

    # todo make a redo function maybe????

    def update_castle_rights(self, move):
        '''
        Update castling rights given move made
        '''
        if move.piece_moved == "wK":  # white king moved
            self.current_castle_rights.ws = False
            self.current_castle_rights.wl = False
        elif move.piece_moved == "bK":  # black king moved
            self.current_castle_rights.bs = False
            self.current_castle_rights.bl = False
        elif move.piece_moved == "wR":  # one of white's rooks moved
            if move.start_col == 0:  # left rook
                self.current_castle_rights.wl = False
            if move.start_col == 7:  # right rook
                self.current_castle_rights.ws = False
        elif move.piece_moved == "bR":  # one of black's rooks moved
            if move.start_col == 0:  # left rook
                self.current_castle_rights.bl = False
            if move.start_col == 7:  # right rook
                self.current_castle_rights.bs = False


    def square_attacked(self, r, c):
        '''
        Check if opponent pressures (is able to attack) square [r][c]
        '''
        self.white_to_move = not self.white_to_move
        enemy_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in enemy_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False


    def get_valid_moves(self):
        '''
        All moves considering checks
        '''
        moves = []  # list of valid moves
        # print(moves)
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()  # see function mentioned
        if self.white_to_move:
            moves.append(self.get_castle_moves(self.white_king_pos[0], self.white_king_pos[1], moves))
        else:
            moves.append(self.get_castle_moves(self.black_king_pos[0], self.black_king_pos[1], moves))
        if self.white_to_move:  # if it's white's turn the following is the king position
            king_row = self.white_king_pos[0]
            king_col = self.white_king_pos[1]
        else:  # if it's black's turn this is the king position
            king_row = self.black_king_pos[0]
            king_col = self.black_king_pos[1]
        if self.in_check:  # is king in check
            print("check")
            if len(self.checks) == 1:  # if only in check once
                print("one check")
                potential_moves = self.get_all_possible_moves()  # get potential moves
                print(potential_moves)
                check = self.checks[0]  # getting check data
                check_row = check[0]  # where in the row we are checked from
                check_col = check[1]  # where in the column we are checked from
                piece_checking = self.board[check_row][check_col]  # where is the piece that is checking us
                valid_squares = []  # list of valid squares to move to
                if piece_checking[1] == "N":  # if it's a knight
                    print("knight")
                    valid_squares = [(check_row, check_col)]  # you have to capture the piece
                else:  # for the other pieces
                    print("not knight")
                    for i in range(1, 8):  # block the check
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # or capture the piece
                            break
                for i in range(len(potential_moves) - 1, -1, -1):  # go through potential move list (backwards)
                    if potential_moves[i].piece_moved[1] != "K":  # if the king isn't moved
                        if not (potential_moves[i].end_row, potential_moves[i].end_col) in valid_squares:  # or if
                            # the check
                            # isn't blocked
                            # or checking piece isn't captured
                            potential_moves.remove(potential_moves[i])  # remove those moves from list
                moves.append(potential_moves)
            else:  # if in check twice
                self.get_king_moves(king_row, king_col, moves)  # you have to move the king
        else:  # if not in check
            print("not in check")
            moves += self.get_all_possible_moves()  # all moves are valid
        #if self.in_check:  # in check
        #    print("no moves left")
        #    if len(moves) == 0: # no valid moves
        #        self.checkmate = True
        #    else:
        #        self.stalemate = True
        #else:
        #    self.checkmate = False
        #    self.stalemate = False
        print(moves)
        return moves



    def get_all_possible_moves(self):
        '''
        All moves without considering checks
        '''
        moves = []
        for r in range(len(self.board)):  # no of rows
            for c in range(len(self.board[r])):  # no of columns in given row
                player = self.board[r][c][0]
                if (player == 'w' and self.white_to_move) or (player == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    # noinspection PyArgumentList
                    self.move_functions[piece](r, c, moves)  # calls piece move function based on piece type
        if self.white_to_move:
            print("White to move")
        else:
            print("Black to move")
        print(moves)
        return moves


    def get_pawn_moves(self, r, c, moves):  # todo simplify pawn move function
        '''
        Get all potential pawn moves for pawn at square [r][c] and add these to the list of possible moves
        '''
        piece_pinned = False  # flag variable to see if pinned
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # go through list of pins (backwards)
            if self.pins[i][0] == r and self.pins[i][1] == c:  # is this piece on a "pinned square"
                piece_pinned = True  # it's pinned
                pin_direction = (self.pins[i][2], self.pins[i][3])  # get pin direction
                self.pins.remove(self.pins[i])  # remove from list of pins
                break

        if self.white_to_move:  # white pawn moves
            if self.board[r - 1][c] == "--":  # one square pawn advance
                if not piece_pinned or pin_direction == (-1, 0):  # is piece pinned?
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # a-h2 to a-h4, or a two square pawn advance
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # pawn captures to the left
                if self.board[r - 1][c - 1][0] == 'b':  # there is an enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, -1):  # is piece pinned?
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.en_passant_possible:  # there is an en passant possible
                    if not piece_pinned or pin_direction == (-1, -1):  # is piece pinned?
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, is_en_passant=True))
            if c + 1 <= 7:  # pawn captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # there is an enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, 1):  # is piece pinned?
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.en_passant_possible:  # there is an en passant possible
                    if not piece_pinned or pin_direction == (-1, 1):  # is piece pinned?
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, is_en_passant=True))


        if not self.white_to_move:  # black pawn moves
            if self.board[r + 1][c] == "--":  # one square pawn advance
                if not piece_pinned or pin_direction == (1, 0):  # is piece pinned?
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # a-h7 to a-h5, or a two square pawn advance
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c + 1 <= 7:  # pawn captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  # there is an enemy piece to capture
                    if not piece_pinned or pin_direction == (1, 1):  # is piece pinned?
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.en_passant_possible:  # there is an en passant possible
                    if not piece_pinned or pin_direction == (1, 1):  # is piece pinned?
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, is_en_passant=True))
            if c - 1 >= 0:  # pawn captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # there is an enemy piece to capture
                    if not piece_pinned or pin_direction == (1, -1):  # is piece pinned?
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.en_passant_possible:  # there is an en passant possible
                    if not piece_pinned or pin_direction == (1, -1):  # is piece pinned?
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, is_en_passant=True))


    def get_bishop_moves(self, r, c, moves):
        '''
        Get all potential bishop moves for bishop at square [r][c] and add these to the list of possible moves
        '''
        piece_pinned = False  # flag variable to see if pinned
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # go through list of pins (backwards)
            if self.pins[i][0] == r and self.pins[i][1] == c:  # is this piece on a "pinned square"
                piece_pinned = True  # it's pinned
                pin_direction = (self.pins[i][2], self.pins[i][3])  # get pin direction
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])  # remove from list of pins
                break
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # ways it can move
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):  # squares it can move to according to the ways it can move
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # not off board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # is our end sq empty?
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # is there an enemy piece to capture?
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break


    def get_knight_moves(self, r, c, moves):
        '''
        Get all potential knight moves for knight at square [r][c] and add these to the list of possible moves
        '''
        piece_pinned = False  # flag variable to see if pinned
        for i in range(len(self.pins) - 1, -1, -1):  # go through list of pins (backwards)
            if self.pins[i][0] == r and self.pins[i][1] == c:  # is this piece on a "pinned square"
                piece_pinned = True  # it's pinned
                self.pins.remove(self.pins[i])  # remove from list of pins
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == enemy_color or end_piece[0] == "-":
                        moves.append(Move((r, c), (end_row, end_col), self.board))


    def get_rook_moves(self, r, c, moves):
        '''
        Get all potential rook moves for rook at square [r][c] and add these to the list of possible moves
        '''
        piece_pinned = False  # flag variable to see if pinned
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # go through list of pins (backwards)
            if self.pins[i][0] == r and self.pins[i][1] == c:  # is this piece on a "pinned square"
                piece_pinned = True  # it's pinned
                pin_direction = (self.pins[i][2], self.pins[i][3])  # get pin direction
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])  # remove from list of pins
                break
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break


    def get_queen_moves(self, r, c, moves):
        '''
        Get all potential queen moves for queen at square [r][c] and add these to the list of possible moves
        '''
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

                                                    ## FIX CHECKS KING IS ALL FUCKED UP BRO WYD RETARD BOY
    def get_king_moves(self, r, c, moves):
        '''
        Get all potential king moves for king at square [r][c] and add these to the list of possible moves
        '''
        move_directions = [[-1, -1], [-1, 0], [0, 1], [1, 1], [-1, 0], [1, -1], [1, -1], [0, 1]]
        enemy_color = "b" if self.white_to_move else "w"
        for dx, dy in move_directions:
            end_row = r + int(dx)
            end_col = c + int(dy)
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color or end_piece[0] == "-":
                    if enemy_color == "b":
                        self.white_king_pos = (end_row, end_col)
                    else:
                        self.black_king_pos = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    if enemy_color == "b":
                        self.white_king_pos = (r, c)
                    else:
                        self.black_king_pos = (r, c)

    def get_castle_moves(self, r, c, moves):
        '''
        Generate possible castle moves
        '''
        if self.in_check:
            return  # can't castle while in check
        else:
            if (self.white_to_move and self.current_castle_rights.ws) or (
                    not self.white_to_move and self.current_castle_rights.bs):
                self.get_short_castle(r, c, moves)
            if (self.white_to_move and self.current_castle_rights.wl) or (
                    not self.white_to_move and self.current_castle_rights.bl):
                self.get_long_castle(r, c, moves)
            return moves

    def get_short_castle(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_attacked(r, c + 1) and not self.square_attacked(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle=True))

    def get_long_castle(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_attacked(r, c - 1) and not self.square_attacked(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle=True))


    def check_for_pins_and_checks(self):
        '''
        Returns a list of pins and a list of potential checks if the player is in check
        '''
        pins = []  # position of allied pinned piece and direction from where it's pinned
        checks = []  # squares where enemy is (potentially) checking player
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_pos[0]
            start_col = self.white_king_pos[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_pos[0]
            start_col = self.black_king_pos[1]
        # check outward from king for pins and checks, keep track of (potential) pins
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (1, 1), (1, -1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        if (0 <= j <= 3 and piece_type == "R") or \
                                (4 <= j <= 7 and piece_type == "B") or \
                                (i == 1 and piece_type == "P" and ((enemy_color == "w" and 6 <= j <= 7) or (
                                        enemy_color == "b" and 4 <= j <= 5))) or \
                                (piece_type == "Q") or (i == 1 and piece_type == "K"):
                            if possible_pin == ():
                                print("Check")
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    in_check = True
                    # noinspection PyUnboundLocalVariable
                    checks.append((end_row, end_col, d[0], d[1]))
        return in_check, pins, checks


class CastleRights:
    '''
    Mapping
    '''
    def __init__(self, ws, bs, wl, bl):
        self.ws = ws
        self.bs = bs
        self.wl = wl
        self.bl = bl


class Move:
    '''
    Maps keys to values, key : value
    '''
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant=False, is_castle=False):
        '''
        Variable conversion
        '''
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.start_sq = start_sq
        self.end_sq = end_sq
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or \
                                 (self.piece_moved == "bP" and self.end_row == 7)
        self.is_en_passant = is_en_passant
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        if self.is_en_passant:
            self.piece_captured = board[self.start_row][self.end_col]
        self.is_castle = is_castle
    def __repr__(self):
        #return str(self.start_sq) + str(self.end_sq)
        # todo make real chess notation
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def __eq__(self, other):
        '''
        Overrides equals method
        '''
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        '''
        Return "chess notation"
        '''
        # todo make real chess notation
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        '''
        Return rank and file numbers for "chess notation"
        '''
        return self.cols_to_files[c] + self.rows_to_ranks[r]
