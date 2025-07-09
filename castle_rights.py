from constants import NUM_TILES
from piece import WHITE, KING, ROOK

castle_rights = []
castle_rights_states = []

WHITE_KING_SIDE = 0
WHITE_QUEEN_SIDE = 1
BLACK_KING_SIDE = 2
BLACK_QUEEN_SIDE = 3

def init(castle_rights_string):
    global castle_rights, castle_rights_states
    
    castle_rights = [False for _ in range(4)]
    if castle_rights_string != "-":
        for castle_rights_key in castle_rights_string:
            castle_rights[get_enum_from_type_string(castle_rights_key)] = True
    castle_rights_states.append(castle_rights)

def get_enum_from_type_string(castle_rights_key):
    if castle_rights_key == "K":
        return WHITE_KING_SIDE
    elif castle_rights_key == "Q":
        return WHITE_QUEEN_SIDE
    elif castle_rights_key == "k":
        return BLACK_KING_SIDE
    return BLACK_QUEEN_SIDE

def get_fen_representation():
    fen_representation_string = ""
    if castle_rights[WHITE_KING_SIDE]:
        fen_representation_string += "K"
    if castle_rights[WHITE_QUEEN_SIDE]:
        fen_representation_string += "Q"
    if castle_rights[BLACK_KING_SIDE]:
        fen_representation_string += "k"
    if castle_rights[BLACK_QUEEN_SIDE]:
        fen_representation_string += "q"
    return "-" if fen_representation_string == "" else fen_representation_string

def has_rights(castle_type):
    return castle_rights[castle_type]

def pop_and_restore_previous_rights():
    global castle_rights, castle_rights_states

    if len(castle_rights_states) == 1:
        castle_rights = castle_rights_states[0]
    else:
        castle_rights = castle_rights_states.pop()

def save_castle_state():
    global castle_rights_states
    castle_rights_states.append(castle_rights.copy())

def get_castle_rook_squares(king_end_tile, piece_color, file_rank_to_square_index):
    rank = NUM_TILES - 1 if piece_color == WHITE else 0
    file, _ = king_end_tile

    is_king_side = file == 6
    start_square = file_rank_to_square_index((file + (1 if is_king_side else -2), rank))
    end_square = file_rank_to_square_index((file + (-1 if is_king_side else 1), rank))
    return (start_square, end_square)

def update_castle_rights(piece_type, piece_tile, piece_color):
    if piece_type == KING:
        revoke_castle_rights(piece_color, revoke_queen_side=True, revoke_king_side=True)
    elif piece_type == ROOK:
        file, rank = piece_tile
        if rank == 0 or rank == NUM_TILES - 1:
            if file == 0:
                revoke_castle_rights(piece_color, revoke_queen_side=True, revoke_king_side=False)
            elif file == NUM_TILES - 1:
                revoke_castle_rights(piece_color, revoke_queen_side=False, revoke_king_side=True)

def revoke_castle_rights(piece_color, revoke_queen_side, revoke_king_side):
    global castle_rights

    if revoke_queen_side:
        queen_side_rights = WHITE_QUEEN_SIDE if piece_color == WHITE else BLACK_QUEEN_SIDE
        castle_rights[queen_side_rights] = False
    if revoke_king_side:
        king_side_rights = WHITE_KING_SIDE if piece_color == WHITE else BLACK_KING_SIDE
        castle_rights[king_side_rights] = False