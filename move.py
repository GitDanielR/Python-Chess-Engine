from piece import get_piece_value, get_piece_string

class move:
    def __init__(self, start_tile: tuple, end_tile: tuple, captured_piece: int = 0, captured_piece_tile: tuple = (0,0), is_castle: bool = False, is_promotion: bool = False, is_double_pawn_push: bool = False):
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.captured_piece = captured_piece
        self.captured_piece_tile = captured_piece_tile
        self.is_castle = is_castle
        self.is_promotion = is_promotion
        self.is_double_pawn_push = is_double_pawn_push

    def get_move_value(self):
        return get_piece_value(self.captured_piece)
    
    def __eq__(self, other):
        return self.start_tile == other.start_tile and self.end_tile == other.end_tile
    
    def __str__(self):
        return f"Start tile: {self.start_tile}, End tile: {self.end_tile}, Captured piece: {get_piece_string(self.captured_piece)}, Captured piece tile: {self.captured_piece_tile}, Is castle: {self.is_castle}, Is promotion: {self.is_promotion}, Is Double Pawn Push: {self.is_double_pawn_push}"