#-------------------------------------- Constants you can change --------------------------------------#
# Screen size
WIDTH = 800
HEIGHT = 800

# Controls if black makes moves for itself
IS_AI_MODE = False

# Board FEN strings
STARTING_POSITION_FEN_STRING = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PAWN_PINNED_FEN_STRING = "rnb1kbnr/pppp1ppp/8/4p3/3P3q/P7/1PP1PPPP/RNBQKBNR w KQkq - 0 1"
BISHOP_PINNED_FEN_STRING = "rnb1kbnr/pppp1ppp/8/4p3/3P3q/P7/1PP1BBPP/RNBQKBNR w KQkq - 0 1"
CASTLE_FEN_STRING = "r3k2r/ppppqppp/8/8/8/8/PPPP1QPP/R3K2R w KQkq - 0 1"
CHECK_FEN_STRING = "r3k2r/pppp1ppp/8/8/8/4q3/PPPP2PP/R3K2R w KQkq - 0 1"
CHECKMATE_FEN_STRING = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1"
ONE_MOVE_FROM_CHECKMATE_FEN_STRING = "rnb1kbnr/pppp1ppp/8/4p3/6qP/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 1"
FOOLS_MATE_SETUP_FEN_STRING = "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 1"
EN_PASSANT_SETUP_FEN_STRING = "rnb1kbnr/pppp1ppp/8/3Pp3/7q/P7/1PP1BBPP/RNBQKBNR b KQkq - 0 1"
PAWN_PROMOTION_SETUP_FEN_STRING = "rn3bnr/p2P1ppp/6k1/4p2q/Q7/P7/1PP1BBPP/RNB1KBNR w KQ - 0 1"
PIECE_DEFENSE_FEN_STRING = "7r/7k/Q4Q1p/7B/8/b7/1PP2BPP/RNB1KBNR w KQ - 0 1"

# FEN string chess board loads on game start/reset 
CURRENT_BOARD_FEN_STRING = PIECE_DEFENSE_FEN_STRING

#-------------------------------------- Constants & functions that aren't meant to be changed --------------------------------------#
# Chess Constants
NUM_PIECES = 12
NUM_TILES = 8
NUM_TILES_ON_BOARD = NUM_TILES * NUM_TILES

# Computed constants for displaying board
TILE_SIZE = None
X_OFFSET = None
Y_OFFSET = None

def set_width_height(_width, _height):
    global WIDTH, HEIGHT
    
    WIDTH = _width
    HEIGHT = _height
    calculate_tile_size()
    
def calculate_tile_size():
    global TILE_SIZE, X_OFFSET, Y_OFFSET
    
    TILE_SIZE = min(WIDTH, HEIGHT) // NUM_TILES
    X_OFFSET = (WIDTH - TILE_SIZE * NUM_TILES) // 2
    Y_OFFSET = (HEIGHT - TILE_SIZE * NUM_TILES) // 2
