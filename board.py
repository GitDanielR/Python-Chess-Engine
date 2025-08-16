import castle_rights
import constants
import move
import piece

board = []
tiles_enemy_attacks = list()
piece_lists = []
pinned_pieces = []
checking_paths = []
move_log = []
legal_moves = {}
is_checkmate = False
white_to_move = True

def init():
    position_from_fen(constants.CURRENT_BOARD_FEN_STRING)

def position_from_fen(fen_string):
    global board, piece_lists, move_log, white_to_move, tiles_enemy_attacks
    
    piece_type_from_symbol = {
        "k": piece.KING,
        "p": piece.PAWN,
        "n": piece.KNIGHT,
        "b": piece.BISHOP,
        "r": piece.ROOK,
        "q": piece.QUEEN
    }
    
    fen_sections = fen_string.split(" ")
    fen_board = fen_sections[0]
    
    file, rank = 0, 0
    
    board = [piece.NONE for _ in range(constants.NUM_TILES_ON_BOARD)]
    piece_lists = [list() for _ in range(constants.NUM_PIECES)]
    move_log = []
    tiles_enemy_attacks = list()
    for char in fen_board:
        if char == "/":
            file = 0
            rank += 1
        else:
            if char.isdigit():
                file += int(char)
            else:
                piece_color = piece.WHITE if char.isupper() else piece.BLACK
                piece_type = piece_type_from_symbol[char.lower()]
                piece_square = file_rank_to_square_index((file, rank))
                board[piece_square] = piece_color | piece_type
                piece_lists[piece_type_color_to_list_index(piece_color, piece_type)].append(piece_square)
                file += 1
                
    white_to_move = fen_sections[1] == "w"
    castle_rights.init(fen_sections[2])
    if fen_sections[3] != "-":
        en_passant_target_file, en_passant_target_rank  = algebraic_to_file_rank(fen_sections[3])
        enemy_pawn_movement_direction = 1 if white_to_move else -1
        start_tile = (en_passant_target_file, en_passant_target_rank - enemy_pawn_movement_direction)
        end_tile = (en_passant_target_file, en_passant_target_rank + enemy_pawn_movement_direction)
        move_log.append(move.move(start_tile, end_tile, piece.NONE, end_tile, False, False, True))
    update_legal_moves()

def get_position_as_fen():
    fen_string = ""
    
    for rank in range(constants.NUM_TILES):
        num_empty_squares = 0
        for file in range(constants.NUM_TILES):
            current_piece = get_piece_at_file_rank((file, rank))
            
            symbol = piece.get_fen_representation_from_piece(current_piece)
            if symbol == "":
                num_empty_squares += 1
            else:
                fen_string += (str(num_empty_squares) if num_empty_squares > 0 else "") + symbol
                num_empty_squares = 0
        fen_string += (str(num_empty_squares) if num_empty_squares > 0 else "") + ("/" if rank < 7 else "")
    
    fen_string += " w" if white_to_move else " b"
    fen_string += " " + castle_rights.get_fen_representation()
    if len(move_log) > 0 and move_log[-1].is_double_pawn_push:
        fen_string += " " + file_rank_to_algebraic(move_log[-1].start_tile)
    else:
        fen_string += " -"
    fen_string += " 0 1"
    
    return fen_string

def get_piece_list_offset(piece_color):
    return (constants.NUM_PIECES // 2) * (piece_color == piece.BLACK)

def get_piece_list_index_from_piece(chess_piece):
    piece_color = piece.get_piece_color(chess_piece)
    piece_type = piece.get_piece_type(chess_piece)
    return piece_type_color_to_list_index(piece_color, piece_type)
    
def piece_type_color_to_list_index(piece_color, piece_type):
    offset = -1 + get_piece_list_offset(piece_color)
    return offset + piece_type

def is_enemy_at_tile(tile_pos):
    if not is_file_rank_inbounds(tile_pos):
        return False
    piece_at_square = get_piece_at_file_rank(tile_pos)
    return is_piece_enemy(piece_at_square)

def is_piece_enemy(chess_piece):
    return chess_piece != piece.NONE and piece.is_white(chess_piece) != white_to_move

def make_player_move(start_tile, end_tile):
    start_tile_square_index = file_rank_to_square_index(start_tile)
    piece_legal_moves = legal_moves[start_tile_square_index]
    
    desired_move = move.move(start_tile, end_tile)
    try:
        chosen_move_index = piece_legal_moves.index(desired_move)
        make_move(piece_legal_moves[chosen_move_index])
        return True
    except ValueError:
        return False

def make_ai_move():
    chosen_move = best_move()
    make_move(chosen_move)
    
def get_current_player_best_move():
    best_move = None
    maximum_score = -1

    def get_best_move(square_index):
        nonlocal best_move, maximum_score

        possible_moves = legal_moves[square_index]
        for possible_move in possible_moves:
            move_value = possible_move.get_move_value()

            if move_value > maximum_score:
                maximum_score = move_value
                best_move = possible_move
    
    iterate_color_pieces(get_best_move, iterate_white=white_to_move)
    return best_move

def make_move(chosen_move):    
    move_log.append(chosen_move)
    update_board_with_move(chosen_move)

def undo_last_move():
    if len(move_log) == 0:
        return
    
    previous_move = move_log.pop()
    update_board_with_move(previous_move,  is_undoing=True)
    
def update_board_with_move(chosen_move, is_undoing = False):
    global white_to_move
    
    start_square = file_rank_to_square_index(chosen_move.start_tile)
    end_square = file_rank_to_square_index(chosen_move.end_tile)
    captured_piece_square = file_rank_to_square_index(chosen_move.captured_piece_tile)
    
    moving_piece = board[end_square] if is_undoing else board[start_square]
    moving_piece_type = piece.get_piece_type(moving_piece)
    moving_piece_color = piece.get_piece_color(moving_piece)
    moving_piece_is_white = piece.is_white(moving_piece)

    if is_undoing:
        castle_rights.pop_and_restore_previous_rights()

        if chosen_move.is_promotion:
            moving_piece_as_pawn = piece.convert_to_piece(piece.PAWN, is_white=moving_piece_is_white)
            set_piece_information_at_square_index(moving_piece_as_pawn, start_square)
        else:
            set_piece_information_at_square_index(board[end_square], start_square)
        set_piece_information_at_square_index(piece.NONE, end_square)
        set_piece_information_at_square_index(chosen_move.captured_piece, captured_piece_square)

        if chosen_move.is_castle:
            rook_start_square, rook_end_square = castle_rights.get_castle_rook_squares(chosen_move.end_tile, moving_piece_color, file_rank_to_square_index)
            set_piece_information_at_square_index(board[rook_end_square], rook_start_square)
            set_piece_information_at_square_index(piece.NONE, rook_end_square)
    else:
        castle_rights.save_castle_state()
        if chosen_move.is_castle:
            rook_start_square, rook_end_square = castle_rights.get_castle_rook_squares(chosen_move.end_tile, moving_piece_color, file_rank_to_square_index)
            set_piece_information_at_square_index(board[rook_start_square], rook_end_square)
            set_piece_information_at_square_index(piece.NONE, rook_start_square)
        castle_rights.update_castle_rights(moving_piece_type, chosen_move.start_tile, moving_piece_color)

        set_piece_information_at_square_index(piece.NONE, captured_piece_square)
        if chosen_move.is_promotion:
            moving_piece_as_queen = piece.convert_to_piece(piece.QUEEN, is_white=moving_piece_is_white)
            set_piece_information_at_square_index(moving_piece_as_queen, end_square)
        else:
            set_piece_information_at_square_index(board[start_square], end_square)
        set_piece_information_at_square_index(piece.NONE, start_square)

    white_to_move = not white_to_move
    update_legal_moves()

def set_piece_information_at_square_index(chess_piece, square_index):
    global board, piece_lists
    
    if chess_piece != piece.NONE:
        piece_list_index = get_piece_list_index_from_piece(chess_piece)
        piece_lists[piece_list_index].append(square_index)
    elif (piece_at_square := board[square_index]) != piece.NONE:
        piece_list_index = get_piece_list_index_from_piece(piece_at_square)
        piece_lists[piece_list_index].remove(square_index)
    
    board[square_index] = chess_piece

def iterate_color_pieces(function, iterate_white):
    piece_list_offset = get_piece_list_offset(piece.WHITE if iterate_white else piece.BLACK)
    
    for piece_type in range(constants.NUM_PIECES // 2):
        piece_list_index = piece_type + piece_list_offset
        for piece_list in piece_lists[piece_list_index]:
            if isinstance(piece_list, int):
                function(piece_list)
            else:
                for piece_square in piece_list:
                    function(piece_square)

def update_legal_moves():
    global legal_moves, is_checkmate
    
    legal_moves = {}
    update_tiles_enemy_attacks()
    update_pinned_and_checking_pieces()

    num_times_current_player_king_attacked = tiles_enemy_attacks.count(get_king_tile_from_color(piece.WHITE if white_to_move else piece.BLACK))
    piece_other_than_king_can_move = num_times_current_player_king_attacked < 2

    num_legal_moves = 0
    def get_piece_moves(square_index):
        nonlocal num_legal_moves

        piece_moves = get_piece_legal_moves(square_index, piece_other_than_king_can_move=piece_other_than_king_can_move)
        filtered_moves = filter_sudo_legal_moves(board[square_index], piece_moves)
        num_legal_moves += len(filtered_moves)
        legal_moves[square_index] = filtered_moves
    iterate_color_pieces(get_piece_moves, iterate_white=white_to_move)
    is_checkmate = num_legal_moves == 0

def filter_sudo_legal_moves(moving_piece, piece_moves):
    if len(piece_moves) == 0 or len(checking_paths) == 0:
        return piece_moves
    checking_path = checking_paths[0]
    if piece.get_piece_type(moving_piece) == piece.KING:
        return piece_moves
    return [piece_move for piece_move in piece_moves if file_rank_to_square_index(piece_move.end_tile) in checking_path]

def update_tiles_enemy_attacks():
    global tiles_enemy_attacks
    
    def get_opponent_piece_attacked_squares(square_index):
        possible_moves = get_piece_legal_moves(square_index, piece_other_than_king_can_move=True)
        tiles_enemy_attacks.extend([possible_move.end_tile for possible_move in possible_moves])
    
    tiles_enemy_attacks = list()
    iterate_color_pieces(get_opponent_piece_attacked_squares, iterate_white=(not white_to_move))

def get_current_player_king_square():
    return board.index(piece.convert_to_piece(piece.KING, is_white=white_to_move))

def get_piece_at_file_rank(tile):
    square_index = file_rank_to_square_index(tile)
    return board[square_index]

def update_pinned_and_checking_pieces():
    global pinned_pieces, checking_paths, tiles_enemy_attacks
    pinned_pieces = []
    checking_paths = []
    
    king_square = get_current_player_king_square()
    king_file, king_rank = square_index_to_file_rank(king_square)
    for d_rank in [-1,0,1]:
        for d_file in [-1,0,1]:
            if d_rank == d_file == 0:
                continue
            
            current_file = king_file
            current_rank = king_rank
            
            pinned_square_path = []
            checking_square_path = []
            number_friendly_pieces_in_direction = 0
            while is_file_rank_inbounds((current_file + d_file, current_rank + d_rank)):
                current_file += d_file
                current_rank += d_rank
                
                current_square = file_rank_to_square_index((current_file, current_rank))
                current_piece = board[current_square]
                
                checking_square_path.append(current_square)
                if is_piece_enemy(current_piece):
                    if piece.can_pin_in_direction(current_piece, d_file, d_rank):
                        pinned_pieces.extend(pinned_square_path)
                        if number_friendly_pieces_in_direction == 0:
                            # Stops king from moving opposite of rook/bishop/queen piece checking
                            if is_file_rank_inbounds((king_file - d_file, king_rank - d_rank)):
                                tiles_enemy_attacks.append((king_file - d_file, king_rank - d_rank))
                            checking_paths.append(checking_square_path)
                    break
                
                if current_piece != piece.NONE:
                    pinned_square_path.append(current_square)
                    number_friendly_pieces_in_direction += 1
                    if number_friendly_pieces_in_direction == 2:
                        break

def get_king_tile_from_color(piece_color):
    king_value = piece.KING | piece_color
    return get_king_tile(king_value)

def get_king_tile(king_value):
    king_square = board.index(king_value)
    return square_index_to_file_rank(king_square)

def get_piece_legal_moves(square_index, piece_other_than_king_can_move):
    current_piece = board[square_index]
    piece_type = piece.get_piece_type(current_piece)

    if piece_type != piece.KING and not piece_other_than_king_can_move:
        return []
    
    piece_legal_moves = []
    piece_color = piece.get_piece_color(current_piece)
    file, rank = square_index_to_file_rank(square_index)
    if piece_type == piece.PAWN:
        piece_legal_moves.extend(get_pawn_moves(file, rank, piece_color))
    elif piece_type == piece.KNIGHT:
        piece_legal_moves.extend(get_knight_moves(file, rank))
    elif piece_type == piece.KING:
        piece_legal_moves.extend(get_king_moves(file, rank, piece_color))
        
    if piece_type == piece.BISHOP or piece_type == piece.QUEEN:
        piece_legal_moves.extend(get_diagonal_sliding_moves(file, rank))
    if piece_type == piece.ROOK or piece_type == piece.QUEEN:
        piece_legal_moves.extend(get_vertical_sliding_moves(file, rank))
        
    return piece_legal_moves

def add_move_data(move_list, start_tile, end_tile, captured_piece_tile = None, is_castle = False, is_promotion = False, is_double_pawn_push = False):
    global tiles_enemy_attacks

    if captured_piece_tile == None:
        captured_piece_tile = end_tile
    
    if is_file_rank_inbounds(end_tile):
        captured_piece = get_piece_at_file_rank(captured_piece_tile)
        moving_piece = get_piece_at_file_rank(start_tile)

        if moving_piece == piece.KING or not piece_movement_violates_pin(start_tile, end_tile):
            captured_piece_is_white = piece.is_white(captured_piece)
            moving_piece_is_white = piece.is_white(moving_piece)

            captured_piece_is_enemy = captured_piece != piece.NONE and captured_piece_is_white != moving_piece_is_white
            captured_piece_is_friendly = captured_piece != piece.NONE and captured_piece_is_white == moving_piece_is_white
            if captured_piece == piece.NONE or captured_piece_is_enemy:
                move_list.append(move.move(start_tile, end_tile, captured_piece, captured_piece_tile, is_castle, is_promotion, is_double_pawn_push))
                if captured_piece_is_enemy:
                    return False
                return True
            elif captured_piece_is_friendly:
                tiles_enemy_attacks.append(end_tile)
    return False

def piece_movement_violates_pin(start_tile, end_tile):
    start_square = file_rank_to_square_index(start_tile)
    
    if start_square in pinned_pieces:
        king_square = get_current_player_king_square()
        king_file, king_rank = square_index_to_file_rank(king_square)
        
        start_file, start_rank = start_tile
        end_file, end_rank = end_tile
        
        move_aligned_vertical = (king_rank < start_rank < end_rank) or (end_rank < start_rank < king_rank)
        move_aligned_horizontal = (king_file < start_file < end_file) or (end_file < start_file < king_file)
        
        if start_file == end_file == king_file:
            return not move_aligned_vertical
        if start_rank == end_rank == king_rank:
            return not move_aligned_horizontal
        # Aligned diagonally
        return not (move_aligned_horizontal and move_aligned_vertical)
    return False

def is_tile_empty(tile_pos):
    piece_at_tile = get_piece_at_file_rank(tile_pos)
    return piece_at_tile == piece.NONE

def get_pawn_moves(file, rank, piece_color):
    direction = -1 if piece_color == piece.WHITE else 1
    start_tile = (file, rank)
    
    move_list = []
    if is_tile_empty((file, rank + direction)):
        end_rank = rank + direction
        add_move_data(move_list, start_tile, (file, rank + direction), is_promotion=(end_rank == 0 or end_rank == constants.NUM_TILES - 1))
        if (rank == 1 and piece_color == piece.BLACK) or (rank == 6 and piece_color == piece.WHITE):
            if is_tile_empty((file, rank + direction * 2)):
                add_move_data(move_list, start_tile, (file, rank + direction * 2), is_double_pawn_push=True)
    if is_enemy_at_tile((file + 1, rank + direction)):
        add_move_data(move_list, start_tile, (file + 1, rank + direction))
    if is_enemy_at_tile((file - 1, rank + direction)):
        add_move_data(move_list, start_tile, (file - 1, rank + direction))
    
    # En Passant
    if len(move_log) > 0 and (rank == 3 and piece_color == piece.WHITE) or (rank == 4 and piece_color == piece.BLACK):
        previous_move = move_log[-1]
        previous_move_file, _ = previous_move.end_tile
        if previous_move.is_double_pawn_push and previous_move_file == file - 1:
            add_move_data(move_list, start_tile, (file - 1, rank + direction), captured_piece_tile=(file - 1, rank))
        elif previous_move.is_double_pawn_push and previous_move_file == file + 1:
            add_move_data(move_list, start_tile, (file + 1, rank + direction), captured_piece_tile=(file + 1, rank))
    return move_list
    
def get_knight_moves(file, rank):
    move_list = []
    start_tile = (file, rank)
    
    for d_file, d_rank in piece.KNIGHT_MOVEMENT_DIRECTIONS:
        add_move_data(move_list, start_tile, (file + d_file, rank + d_rank))
    return move_list
    
def get_king_moves(file, rank, piece_color):
    move_list = []
    start_tile = (file, rank)

    for d_rank in [-1,0,1]:
        for d_file in [-1,0,1]:
            if d_file == d_rank == 0:
                continue
            end_tile = (file + d_file, rank + d_rank)

            if end_tile not in tiles_enemy_attacks:
                add_move_data(move_list, start_tile, end_tile)
            
    king_side_castle_right = castle_rights.WHITE_KING_SIDE if piece_color == piece.WHITE else castle_rights.BLACK_KING_SIDE
    queen_side_castle_right = castle_rights.WHITE_QUEEN_SIDE if piece_color == piece.WHITE else castle_rights.BLACK_QUEEN_SIDE
    
    if castle_rights.has_rights(king_side_castle_right):
        tiles_on_king_side = [(file + 1, rank), (file + 2, rank)]
        if all(get_piece_at_file_rank(tile) == piece.NONE and not (tile in tiles_enemy_attacks) for tile in tiles_on_king_side):
            add_move_data(move_list, start_tile, (file + 2, rank), is_castle=True)
    if castle_rights.has_rights(queen_side_castle_right):
        tiles_on_queen_side = [(file - 1, rank), (file - 2, rank), (file - 3, rank)]
        if all(get_piece_at_file_rank(tile) == piece.NONE and not (tile in tiles_enemy_attacks) for tile in tiles_on_queen_side):
            add_move_data(move_list, start_tile, (file - 2, rank), is_castle=True)
    return move_list
    
def get_diagonal_sliding_moves(file, rank):
    move_list = []
    start_tile = (file, rank)
    
    for d_rank in [-1,1]:
        for d_file in [-1,1]:
            current_file = file + d_file
            current_rank = rank + d_rank
            
            while add_move_data(move_list, start_tile, (current_file, current_rank)):
                current_file += d_file
                current_rank += d_rank
    return move_list
    
def get_vertical_sliding_moves(file, rank):
    move_list = []
    start_tile = (file, rank)
    
    def slide(increment_file):
        for movement_direction in [-1,1]:
            current_pos = file if increment_file else rank
            current_pos += movement_direction
            
            while add_move_data(move_list, start_tile, (current_pos if increment_file else file, current_pos if not increment_file else rank)):
                current_pos += movement_direction
    
    slide(True)
    slide(False)
    return move_list

def file_rank_to_square_index(coord):
    tens_place = coord[1] * constants.NUM_TILES
    return tens_place + coord[0]
    
def square_index_to_file_rank(square_index):
    file = square_index % constants.NUM_TILES
    rank = square_index // constants.NUM_TILES
    return (file, rank)
    
def validate_start_tile(start_tile):
    piece_at_square = get_piece_at_file_rank(start_tile)
    return piece_at_square != piece.NONE and piece.is_white(piece_at_square) == white_to_move

def is_file_rank_inbounds(tile):
    file, rank = tile
    return 0 <= file < constants.NUM_TILES and 0 <= rank < constants.NUM_TILES

def algebraic_to_file_rank(algebraic_repr):
    character_ascii_offset = 0x61
    algebraic_file = algebraic_repr[0]
    algebraic_rank = algebraic_repr[1]
    return (ord(algebraic_file) - character_ascii_offset, constants.NUM_TILES - int(algebraic_rank))

def file_rank_to_algebraic(start_tile):
    character_ascii_offset = 0x61
    file, rank = start_tile
    enemy_movement_direction = -1 if white_to_move else 1
    algebraic_file = chr(character_ascii_offset + file)
    algebraic_rank = constants.NUM_TILES - rank + enemy_movement_direction
    return algebraic_file + str(algebraic_rank)

def evaluate_board():
    white_eval = 0
    black_eval = 0

    for chess_piece in board:
        chess_piece_type = piece.get_piece_type(chess_piece)
        if chess_piece_type != piece.NONE and chess_piece_type != piece.KING:
            piece_value = piece.get_piece_value(chess_piece)
            if piece.is_white(chess_piece):
                white_eval += piece_value
            else:
                black_eval += piece_value
    
    evaluation = white_eval - black_eval
    perspective = 1 if white_to_move else -1

    return evaluation * perspective

def order_moves(moves):
    def evaluate_move(possible_move):
        move_score_guess = 0
        moving_piece = get_piece_at_file_rank(possible_move.start_tile)
        moving_piece_type = piece.get_piece_type(moving_piece)
        captured_piece_type = piece.get_piece_type(possible_move.captured_piece)

        if captured_piece_type != piece.NONE:
            move_score_guess = 10 * piece.get_piece_value(captured_piece_type) - piece.get_piece_value(moving_piece_type)
        if possible_move.is_promotion:
            move_score_guess += piece.get_piece_value(piece.QUEEN)
        if possible_move.end_tile in tiles_enemy_attacks:
            move_score_guess -= piece.get_piece_value(moving_piece_type)
        return move_score_guess
    moves.sort(key=evaluate_move)

def best_move():
    best_move = None
    best_eval = float("-inf")

    def search_board_for_move(depth, alpha, beta):
        nonlocal best_move, best_eval 

        if depth == 0:
            return evaluate_board()
        if is_checkmate:
            return float("-inf")

        current_legal_moves = [move for move_list in legal_moves.values() for move in move_list] 
        order_moves(current_legal_moves)
        for legal_move in current_legal_moves:
            make_move(legal_move)
            evaluation = -search_board_for_move(depth - 1, -beta, -alpha)
            undo_last_move()
            if evaluation >= beta:
                return beta
            if evaluation > alpha:
                alpha = evaluation
                best_move = legal_move
                best_eval = evaluation

        return alpha
    search_board_for_move(constants.AI_SEARCH_DEPTH, float("-inf"), float("inf"))
    return best_move