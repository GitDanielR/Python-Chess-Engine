NONE = 0
KING = 1
PAWN = 2
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 6

WHITE = 8
BLACK = 16

KNIGHT_MOVEMENT_DIRECTIONS = [(-2,1),(-2,-1),(2,1),(2,-1),(-1,2),(-1,-2),(1,2),(1,-2)]

PIECE_VALUES = {
    NONE: 0,
    PAWN: 1,
    KNIGHT: 3,
    BISHOP: 3,
    QUEEN: 9,
    KING: float('inf')
}

def is_white(piece):
    return (piece & WHITE) == WHITE
    
def get_piece_type(piece):
    return (piece & 0b00111)
    
def get_piece_color(piece):
    return (piece & 0b11000)
    
def get_piece_value(piece):
    piece_type = get_piece_type(piece)
    return PIECE_VALUES[piece_type]

def get_piece_string(piece):
    piece_type = get_piece_type(piece)
    if piece_type == NONE:
        return "None"
    if piece_type == PAWN:
        return "Pawn"
    if piece_type == KNIGHT:
        return "Knight"
    if piece_type == "Bishop":
        return "Bishop"
    if piece_type == QUEEN:
        return "Queen"
    return "King"

def get_fen_representation_from_piece(piece):
    piece_fen_representation = ""
    if piece == NONE:
        return piece_fen_representation
    
    piece_type = get_piece_type(piece)
    if piece_type == KING:
        piece_fen_representation = "k"
    elif piece_type == PAWN:
        piece_fen_representation = "p"
    elif piece_type == KNIGHT:
        piece_fen_representation = "n"
    elif piece_type == BISHOP:
        piece_fen_representation = "b"
    elif piece_type == ROOK:
        piece_fen_representation = "r"
    elif piece_type == QUEEN:
        piece_fen_representation = "q"
        
    if get_piece_color(piece) == WHITE:
        piece_fen_representation = piece_fen_representation.upper()
        
    return piece_fen_representation
    
def convert_to_piece(piece_type, is_white):
    return piece_type | (WHITE if is_white else BLACK)

def can_pin_in_direction(piece, d_file, d_rank):
    piece_type = get_piece_type(piece)
    
    if d_file == d_rank == 0:
        return False
    
    if piece_type == QUEEN:
        return True
    if piece_type == BISHOP:
        return not (d_file == 0 or d_rank == 0)
    if piece_type == ROOK:
        return d_file == 0 or d_rank == 0
    return False
    